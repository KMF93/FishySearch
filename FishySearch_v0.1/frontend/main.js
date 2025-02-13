// ~/Documents/FishySearch/frontend/main.js
const resultsFolder = "../results/";
const tableID = "#resultTable";
let dataTable = null;
const priorityColumns = ["shop", "image", "name"];
const expandableColumns = new Set(["description", "service"]);
const maxTruncateLength = 120;

async function getResultFiles() {
  try {
    const response = await fetch(resultsFolder);
    const html = await response.text();
    return [...html.matchAll(/(\d{6}_result\.json)/g)]
      .map(m => m[1])
      .sort((a, b) => b.localeCompare(a));
  } catch (error) {
    console.error("Error fetching files:", error);
    return [];
  }
}

async function fetchJson(files) {
  try {
    const [master, previous] = await Promise.all([
      fetch(resultsFolder + files[0]).then(r => r.json()),
      files[1] ? fetch(resultsFolder + files[1]).then(r => r.json()) : null
    ]);
    return { master, previous };
  } catch (error) {
    console.error("Error loading JSON:", error);
    return { master: [], previous: null };
  }
}

function getColumnStructure(data) {
  const allColumns = new Set();
  data.forEach(item => {
    Object.keys(item)
      .filter(k => k !== 'details' && k !== 'url')
      .forEach(k => allColumns.add(k));
    
    if (item.details) {
      Object.keys(item.details)
        .filter(k => k !== 'url')
        .forEach(k => allColumns.add(k));
    }
  });

  // Add isNew to column set
  allColumns.add('isNew');

  // Sort columns with priority and position isNew after name
  const sortedColumns = [...priorityColumns];
  const remainingColumns = [...allColumns].filter(c => !priorityColumns.includes(c));
  
  // Insert isNew after name if exists
  const nameIndex = sortedColumns.indexOf('name');
  if (nameIndex > -1) {
    sortedColumns.splice(nameIndex + 1, 0, 'status');
  } else {
    sortedColumns.push('status');
  }

  return [...new Set([...sortedColumns, ...remainingColumns])];
}

function markNewEntries(data) {
  if (!data.previous) return data.master;

  const prevUrls = new Set(
    data.previous.flatMap(item => 
      item.details?.url ? [item.details.url] : []
    )
  );

  return data.master.map(item => ({
    ...item,
    details: {
      ...item.details,
      status: !prevUrls.has(item.details?.url) ? "NEW" : "existing"
    }
  }));
}

function createExpandableContent(data, column) {
  const isExpandable = expandableColumns.has(column.toLowerCase());
  const shouldTruncate = isExpandable && data && data.length > maxTruncateLength;
  const displayText = shouldTruncate ? 
    `${data.substring(0, maxTruncateLength)}...` : 
    data;

  return `
    <div class="content-container${isExpandable ? ' expandable' : ''}">
      ${isExpandable ? `
        <span class="chevron${shouldTruncate ? '' : ' hidden'}"></span>
      ` : ''}
      <span class="content-text">${displayText || ''}</span>
    </div>
  `;
}

function initializeTable(data) {
  if (dataTable) dataTable.destroy();

  const columns = getColumnStructure(data);

  dataTable = $(tableID).DataTable({
    data: data,
    columns: columns.map(col => ({
      data: function(row) {
        return row[col] ?? row.details?.[col];
      },
      title: col === 'status' ? 'Status' : col.charAt(0).toUpperCase() + col.slice(1),
      render: function(data, type, row) {
        if (col === 'image') {
          const url = row.details?.url || "#";
          return data ? `<a href="${url}" target="_blank"><img src="${data}"></a>` : "No Image";
        }
        if (col === 'status') {
          return `<span class="status-${data.toLowerCase()}">${data}</span>`;
        }
        const displayValue = typeof data === 'object' ? 
          JSON.stringify(data) : 
          data?.toString() || '';
        return createExpandableContent(displayValue, col);
      }
    })),
    columnDefs: [{
      targets: priorityColumns.map((_, i) => i),
      className: "no-truncate"
    }],
    createdRow: function(row) {
      $(row).find('.status-new').closest('td').addClass('highlight-new');
    }
  });

  // Existing click handler for expandable content...
}

(async function init() {
  const files = await getResultFiles();
  if (files.length === 0) return;
 
  const data = await fetchJson(files);
  const processedData = markNewEntries(data);
  initializeTable(processedData);
})();
