from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os


BUILD_DIR = Path(__file__).resolve().parent / 'build'


class SpaHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BUILD_DIR), **kwargs)

    def do_GET(self):
        requested = self.path.split('?', 1)[0].split('#', 1)[0]
        candidate = (BUILD_DIR / requested.lstrip('/')).resolve()

        # Serve real files directly. Everything else falls back to index.html for React Router.
        if requested in ('', '/') or not str(candidate).startswith(str(BUILD_DIR)) or not candidate.exists():
            self.path = '/index.html'

        return super().do_GET()


def main():
    port = int(os.environ.get('PORT', '3000'))
    server = ThreadingHTTPServer(('127.0.0.1', port), SpaHandler)
    print(f'Serving React build with SPA fallback on http://127.0.0.1:{port}')
    server.serve_forever()


if __name__ == '__main__':
    main()
