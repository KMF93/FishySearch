# ~/Documents/FishySearch/run_all.py
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

def run_server():
    """Run HTTP server directly in current process"""
    print("\n🌐 Starting web server...")
    os.chdir(os.path.expanduser("~/Documents/FishySearch"))
    
    class ReusableTCPServer(socketserver.TCPServer):
        allow_reuse_address = True
        
    PORT = 8000
    handler = http.server.SimpleHTTPRequestHandler
    httpd = ReusableTCPServer(("", PORT), handler)
    
    print(f"🔗 Server ready at http://localhost:{PORT}")
    webbrowser.open(f"http://localhost:{PORT}/frontend/index.html")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server shutdown")
        httpd.server_close()

if __name__ == "__main__":
    if run_aggregator():
        time.sleep(0.5)  # Brief pause for output readability
        run_server()
    else:
        print("❌ Aborting server start due to aggregation failure")
