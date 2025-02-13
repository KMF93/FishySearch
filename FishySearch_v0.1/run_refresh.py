# ~/Documents/FishySearch/run_refresh.py
import os
import time
from backend.aggregator import Aggregator
import http.server
import socketserver
import webbrowser

def run_aggregator():
    """Run aggregation directly without subprocess"""
    print("🚀 Starting data aggregation...")
    config_path = os.path.expanduser("~/Documents/FishySearch/config/config.json")
    aggregator = Aggregator(config_path)
    result = aggregator.run()
    print(f"✅ {result}")
    return "Critical failure" not in result


if __name__ == "__main__":
    run_aggregator()
