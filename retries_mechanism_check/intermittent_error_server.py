import random
from http.server import BaseHTTPRequestHandler, HTTPServer

class FlakyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if random.random() < 0.5:  # 50% chance of failure
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"Internal Server Error")
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Hello from Flaky Server!")

if __name__ == "__main__":
    server_address = ("127.0.0.1", 8080)
    httpd = HTTPServer(server_address, FlakyHandler)
    print("Serving on port 8080...")
    httpd.serve_forever()
