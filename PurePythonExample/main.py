from http.server import BaseHTTPRequestHandler, HTTPServer
import time


class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>MIPT Python Web Demo</title></head>", "utf-8"))
        self.wfile.write(bytes(f"<p>Request: {self.path}</p>", "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        self.wfile.write(bytes("<p>This is an example web server.</p>", "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))


VAR_name = '"" OR TRUE'
VAR_id = '"" OR TRUE'
f"""
SELECT user_id, user_name, secret_data FROM users WHERE user_name = {VAR_name} AND user_id = {VAR_id}
"""

f"""
SELECT user_id, user_name, secret_data FROM users WHERE user_name = "" OR TRUE AND user_id = "" OR TRUE
"""


if __name__ == "__main__":
    hostname = "localhost"
    port = 8000

    webServer = HTTPServer((hostname, port), MyServer)
    print(f"Server started http://{hostname}:{port}")

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")