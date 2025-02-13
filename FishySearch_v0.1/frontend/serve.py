import http.server
import socketserver
import os
import webbrowser

PORT = 8000

class FishyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Handle config file requests
        if self.path.startswith('/config/'):
            config_file = os.path.join('config', self.path[8:])
            if os.path.exists(config_file):
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                with open(config_file, 'rb') as f:
                    self.wfile.write(f.read())
                return
        super().do_GET()

    def do_PUT(self):
        # Handle filter saving
        if self.path == '/config/savedfilter.json':
            try:
                os.makedirs('config', exist_ok=True)
                content_length = int(self.headers['Content-Length'])
                content = self.rfile.read(content_length)
                
                with open('config/savedfilter.json', 'wb') as f:
                    f.write(content)
                
                self.send_response(200)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
            except Exception as e:
                print(f"PUT error: {str(e)}")
                self.send_response(500)
                self.end_headers()
        else:
            self.send_response(403)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, PUT, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

if __name__ == "__main__":
    os.chdir(os.path.expanduser("~/Documents/FishySearch"))
    with socketserver.TCPServer(("", PORT), FishyHandler) as httpd:
        print(f"Serving at http://localhost:{PORT}")
        webbrowser.open(f"http://localhost:{PORT}/frontend/index.html")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Server stopped")
