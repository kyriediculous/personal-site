"""Serve the built site on loopback only, including its branded 404 page."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

DIST = Path(__file__).resolve().parent / 'dist'

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIST), **kwargs)

    def send_error(self, code, message=None, explain=None):
        if code == 404 and (DIST / '404.html').exists():
            body = (DIST / '404.html').read_bytes()
            self.send_response(404)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            if self.command != 'HEAD': self.wfile.write(body)
        else:
            super().send_error(code, message, explain)

    def list_directory(self, path):
        self.send_error(404)
        return None

if __name__ == '__main__':
    print('Local preview: http://127.0.0.1:4173/', flush=True)
    ThreadingHTTPServer(('127.0.0.1', 4173), Handler).serve_forever()
