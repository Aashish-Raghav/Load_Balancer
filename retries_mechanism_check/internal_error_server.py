from http.server import BaseHTTPRequestHandler, HTTPServer

class ErrorHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(500)  # Simulate internal server error
        self.end_headers()
        self.wfile.write(b"Internal Server Error")

if __name__ == "__main__":
    server_address = ("127.0.0.1", 8080)
    httpd = HTTPServer(server_address, ErrorHandler)
    print("Serving on port 8080...")
    httpd.serve_forever()
