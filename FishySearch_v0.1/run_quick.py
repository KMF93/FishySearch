# ~/Documents/FishySearch/run_quick.py
import os
import time
import http.server
import socketserver
import webbrowser


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
    run_server()

