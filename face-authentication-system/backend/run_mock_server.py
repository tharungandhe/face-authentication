from http.server import SimpleHTTPRequestHandler, HTTPServer
import json
from pathlib import Path


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/api/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            payload = {"status": "ok", "service": "face-authentication-system (mock)"}
            self.wfile.write(json.dumps(payload).encode())
            return

        # Fall back to serving static files from the frontend directory
        return super().do_GET()


if __name__ == "__main__":
    # Bind to localhost so browsers can open the site with http://127.0.0.1
    host = "127.0.0.1"
    port = 8000

    base = Path(__file__).resolve().parent.parent
    frontend_dir = base / "frontend"
    if frontend_dir.exists():
        # Serve files from the frontend directory
        import os

        os.chdir(str(frontend_dir))

    server = HTTPServer((host, port), Handler)
    print(f"Mock server running on http://{host}:{port} - serving {frontend_dir}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()

