from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import json
import mimetypes

BASE_DIR = Path(__file__).resolve().parent
HOST = "127.0.0.1"
PORT = 8000


class LandingPageHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        requested_path = parsed.path.strip("/")

        if requested_path in ("", "index.html"):
            file_path = BASE_DIR / "index.html"
        elif requested_path == "style.css":
            file_path = BASE_DIR / "style.css"
        else:
            self._send_response(404, "text/plain", "Not Found")
            return

        if not file_path.exists():
            self._send_response(404, "text/plain", "File not found")
            return

        content_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
        content = file_path.read_bytes()
        self._send_response(200, content_type, content)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/submit":
            self._send_response(404, "text/plain", "Not Found")
            return

        length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(length) if length else b""
        body = raw_body.decode("utf-8", errors="replace")
        form_data = parse_qs(body, keep_blank_values=True)

        cleaned = {key: values[0].strip() if values else "" for key, values in form_data.items()}
        name = cleaned.get("name", "")
        email = cleaned.get("email", "")
        project = cleaned.get("project", "")

        if not name or not email or not project:
            response = {
                "status": "error",
                "message": "Name, email, and project details are required.",
            }
            self._send_response(400, "application/json", json.dumps(response).encode("utf-8"))
            return

        print("New project inquiry:")
        print(f"Name: {name}")
        print(f"Email: {email}")
        print(f"Project: {project}")

        response = {
            "status": "success",
            "message": "Thanks! We'll be in touch shortly.",
            "data": {"name": name, "email": email, "project": project},
        }
        self._send_response(200, "application/json", json.dumps(response).encode("utf-8"))

    def _send_response(self, status_code, content_type, content):
        if isinstance(content, str):
            payload = content.encode("utf-8")
        else:
            payload = content

        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format, *args):
        return


def main():
    server = ThreadingHTTPServer((HOST, PORT), LandingPageHandler)
    print(f"Serving Northstar Studio at http://{HOST}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
