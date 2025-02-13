document.addEventListener('DOMContentLoaded', () => {
    let dataTable;
    const configPath = '/config/savedfilter.json';
    const operators = [
        { value: 'contains', text: 'Contains' },
        { value: 'equals', text: 'Equals' },
        { value: 'starts', text: 'Starts With' },
        { value: 'ends', text: 'Ends With' },
        { value: 'empty', text: 'Is Empty' }
    ];

    // Load saved state
    async function loadSavedState() {
        try {
            const response = await fetch(configPath);
            if (!response.ok) return { filters: [], sorting: [] };
            return await response.json();
        } catch {
            return { filters: [], sorting: [] };
        }
    }

    // Save full state
    async function saveFullState(state) {
        try {
            await fetch(configPath, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(state)
            });
        } catch (error) {
            console.error('Save failed:', error);
        }
    }

    // Initialize DataTable
    const initTable = setInterval(() => {
        if ($.fn.DataTable.isDataTable('#resultTable')) {
            clearInterval(initTable);
            dataTable = $('#resultTable').DataTable({
                stateSave: false,
                order: []
            });
            initFilterUI();
            loadInitialState();
        }
    }, 100);

    async function loadInitialState() {
        const { filters, sorting } = await loadSavedState();
        if (filters.length > 0) {
            filters.forEach(f => addFilterRow(f));
            setTimeout(() => applyFilters(), 100);
        }
        if (sorting.length > 0) {
            dataTable.order(sorting).draw();
        }
    }

    function initFilterUI() {
        const $wrapper = $('#resultTable_wrapper');
        const $filterContainer = $(`
            <div class="filter-system">
                <div id="filterRows"></div>
                <div class="filter-controls">
                    <button id="addFilter" class="filter-btn">+ Filter</button>
                    <button id="loadState" class="filter-load-btn">Load</button>
                    <button id="saveState" class="filter-save-btn">Save</button>
                </div>
            </div>
        `).insertBefore($wrapper);

        $('#addFilter').click(() => addFilterRow());
        $('#saveState').click(() => saveCurrentState());
        $('#loadState').click(() => loadSavedStateUI());
    }

    async function loadSavedStateUI() {
        try {
            $('#filterRows').empty();
            const { filters, sorting } = await loadSavedState();
            
            if (filters.length > 0) {
                filters.forEach(f => addFilterRow(f));
                setTimeout(() => applyFilters(), 100);
            }

            if (sorting.length > 0) {
                dataTable.order(sorting).draw();
            }
        } catch (error) {
            console.error('Load failed:', error);
        }
    }

    function addFilterRow(savedFilter = {}) {
        const $row = $('<div class="filter-row">');
        const columns = [];
        
        dataTable.columns().every(function() {
            const colHeader = this.header().textContent.toLowerCase();
            if (!['image', 'url'].includes(colHeader)) {
                columns.push(colHeader);
            }
        });

        const $colSelect = $('<select class="filter-column">');
        columns.forEach(col => {
            $colSelect.append(`<option value="${col}">${col}</option>`);
        });
        if (savedFilter.column) $colSelect.val(savedFilter.column.toLowerCase());

        const $opSelect = $('<select class="filter-operator">');
        operators.forEach(op => {
            $opSelect.append(`<option value="${op.value}">${op.text}</option>`);
        });
        if (savedFilter.operator) $opSelect.val(savedFilter.operator);

        const $valueInput = $('<input type="text" class="filter-value" placeholder="Value">');
        if (savedFilter.value) $valueInput.val(savedFilter.value);

        const $removeBtn = $('<button class="filter-remove">X</button>').click(() => {
            $row.remove();
            applyFilters();
            saveCurrentState();
        });

        $row.append($colSelect, $opSelect, $valueInput, $removeBtn);
        $('#filterRows').append($row);

        $row.find('select, input').on('change input', () => {
            applyFilters();
            saveCurrentState();
        });
    }

    function getCurrentFilters() {
        const filters = [];
        $('.filter-row').each(function() {
            const $row = $(this);
            const filter = {
                column: $row.find('.filter-column').val(),
                operator: $row.find('.filter-operator').val(),
                value: $row.find('.filter-value').val().trim()
            };
            if (filter.operator === 'empty' || filter.value) {
                filters.push(filter);
            }
        });
        return filters;
    }

    function saveCurrentState() {
        const currentState = {
            filters: getCurrentFilters(),
            sorting: dataTable.order()[0] || [0, 'asc']
        };
        saveFullState(currentState);
    }

    function applyFilters() {
        $.fn.dataTable.ext.search = [];
        const filters = getCurrentFilters();

        if (filters.length > 0) {
            $.fn.dataTable.ext.search.push((settings, data, dataIndex) => {
                const row = dataTable.row(dataIndex).data();
                const mergedData = { ...row, ...(row.details || {}) };

                return filters.every(filter => {
                    const cellValue = String(mergedData[filter.column] || '').toLowerCase();
                    const filterValue = filter.value.toLowerCase();
                    
                    switch(filter.operator) {
                        case 'contains': return cellValue.includes(filterValue);
                        case 'equals': return cellValue === filterValue;
                        case 'starts': return cellValue.startsWith(filterValue);
                        case 'ends': return cellValue.endsWith(filterValue);
                        case 'empty': return cellValue === '';
                        default: return true;
                    }
                });
            });
        }

        dataTable.draw();
    }
});
