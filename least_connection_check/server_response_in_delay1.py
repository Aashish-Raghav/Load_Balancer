import time
from http.server import SimpleHTTPRequestHandler, HTTPServer


class SlowHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.handle_health_check()
        elif self.path == "/":
            self.handle_home()
        else:
            # Default behavior for other paths (e.g., static files)
            super().do_GET()

    def handle_health_check(self):
        # Respond instantly for health check
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Server is healthy")

    def handle_home(self):
        # Simulate delay for home page
        time.sleep(1)  # Delay to trigger timeout
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Welcome to the Home Page 8080!")


if __name__ == "__main__":
    server_address = ("127.0.0.1", 8080)
    httpd = HTTPServer(server_address, SlowHandler)
    print("Serving on port 8080...")
    httpd.serve_forever()
