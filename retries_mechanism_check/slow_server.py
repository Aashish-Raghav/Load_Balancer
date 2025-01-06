import time
from http.server import SimpleHTTPRequestHandler, HTTPServer

class SlowHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        time.sleep(10)  # Delay of 10 seconds to trigger timeout
        super().do_GET()

if __name__ == "__main__":
    server_address = ("127.0.0.1", 8080)
    httpd = HTTPServer(server_address, SlowHandler)
    print("Serving on port 8080...")
    httpd.serve_forever()
