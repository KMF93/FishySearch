# ~/Documents/S9/backend/aggregator.py
import os
import json
import datetime
import warnings
from urllib.request import Request, urlopen
from urllib.parse import urljoin, urlsplit, urlunsplit, quote
from bs4 import BeautifulSoup

warnings.filterwarnings("ignore")

class Aggregator:
    def __init__(self, config_path):
        self.config_path = os.path.expanduser(config_path)
        self.results_dir = os.path.expanduser("~/Documents/FishySearch/results")
        self.load_config()

    def load_config(self):
        """Load JSON configuration with UTF-8 support."""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)
        except Exception as e:
            raise RuntimeError(f"Error loading configuration: {e}")

    def fetch_page(self, url):
        """Fetch HTML content while handling non-ASCII URLs."""
        try:
            req = Request(url, headers={'User-Agent': 'Pythonista Aggregator'})
            with urlopen(req) as response:
                return response.read()
        except Exception as e:
            raise RuntimeError(f"Network error: {str(e)}")

    def parse_main_page(self, html, shop_config):
        """Parse catalog page with Unicode URL encoding."""
        soup = BeautifulSoup(html, 'html.parser')
        results = []

        containers = soup.select(shop_config["selectors"]["catalog"])
        if not containers:
            print(f"[Warning] No containers found for {shop_config['shop_name']}")
            return []

        for container in containers:
            try:
                product_data = {"shop": shop_config["shop_name"]}

                # Process mainpage attributes
                for attr, selector in shop_config["mainpage_attributes"].items():
                    element = container.select_one(selector)
                    if element:
                        if attr == "image" and element.get('src'):
                            product_data[attr] = urljoin(shop_config["base_url"], element['src'])
                        else:
                            product_data[attr] = element.get_text(strip=True)

                # Process subpage link with URL validation and encoding
                link_element = container.select_one(shop_config["selectors"]["linktosubpage"])
                if link_element and (href := link_element.get('href')):
                    raw_subpage_url = urljoin(shop_config["base_url"], href)
                    # Encode path and query components
                    parsed_url = urlsplit(raw_subpage_url)
                    encoded_path = quote(parsed_url.path.encode('utf8'), safe='/')
                    encoded_query = quote(parsed_url.query.encode('utf8'), safe='&=')
                    encoded_url = urlunsplit(parsed_url._replace(
                        path=encoded_path,
                        query=encoded_query
                    ))
                    try:
                        product_data["details"] = self.parse_subpage(encoded_url, shop_config)
                    except Exception as e:
                        print(f"Subpage error ({encoded_url}): {str(e)}")
                        product_data["details"] = {"error": "Subpage failed to load"}

                # Skip if name is missing or contains excluded keywords
                name = product_data.get('name') or product_data.get('details', {}).get('name')
                if not name or not name.strip():
                    #print(f"Skipping product (missing name)")
                    continue
                excluded_keywords = shop_config.get("excluded_keywords", [])
                if any(kw.upper() in name.upper() for kw in excluded_keywords):
                    #print(f"Skipping product (excluded keyword): {name}")
                    continue

                results.append(product_data)

            except Exception as e:
                print(f"Skipping item: {str(e)}")
                
        return results

    def parse_subpage(self, url, shop_config):
        """Parse subpage with conditional URL tracking."""
        html = self.fetch_page(url)
        soup = BeautifulSoup(html, 'html.parser')
        details = {}
        valid_content = False

        for attr, selector in shop_config["subpage_attributes"].items():
            element = soup.select_one(selector)
            if element and (text := element.get_text(strip=True)):
                details[attr] = text
                valid_content = True
            else:
                details[attr] = None

        if valid_content:
            details["url"] = url  # Track URL only if valid content exists
        return details

    def get_result_filename(self):
        """Generate dated output filename."""
        today = datetime.datetime.now().strftime("%y%m%d")
        return os.path.join(self.results_dir, f"{today}_result.json")

    def check_existing_result(self):
        """Check if today's result file already exists."""
        result_file = self.get_result_filename()
        return os.path.exists(result_file)

    def save_results(self, aggregated_data):
        """Save data to results directory with date-based filename."""
        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir)

        with open(self.get_result_filename(), "w", encoding="utf-8") as f:
            json.dump(aggregated_data, f, indent=2, ensure_ascii=False)

    def run(self):
        """Main execution flow."""
        if self.check_existing_result():
            return "Aggregation skipped: Results for today already exist."

        try:
            all_results = []
            for shop_name, shop_config in self.config.items():
                print(f"Processing {shop_name}...")
                html = self.fetch_page(shop_config["base_url"])
                all_results.extend(self.parse_main_page(html, shop_config))
            
            self.save_results(all_results)
            return f"Completed: {len(all_results)} items aggregated"
        except Exception as e:
            return f"Critical failure: {str(e)}"


if __name__ == "__main__":
    config_path = "~/Documents/FishySearch/config/config.json"
    aggregator = Aggregator(config_path)
    print(aggregator.run())
