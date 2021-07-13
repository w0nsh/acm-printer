import argparse
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import io
import cgi
from uuid import uuid4
import subprocess
from pathlib import Path

os.chdir(os.path.dirname(os.path.abspath(__file__)))

class PrinterServer(SimpleHTTPRequestHandler):
    STORAGE = Path('./codes')
    MAX_CONTENT_LENGTH = 30000
    INDEX_HTML = str(open('./index.html').read())

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def _print(self, content, filename):
        name = str(uuid4())
        os.makedirs(str(self.STORAGE / name), exist_ok=True)
        path = self.STORAGE / name / filename
        ps_path = path.with_suffix('.ps')
        with open(path, 'w+') as file:
            file.write(content)

        proc = subprocess.run(['a2ps', str(path), '-o', str(ps_path)])
        if proc.returncode != 0:
            return (False, f'Could not convert {path} to .ps file')
        
        proc = subprocess.run(['lp', str(ps_path)])
        if proc.returncode != 0:
            return (False, f'Could not add {ps_path} to print queue')

        return (True, f'Printed file')

    def do_GET(self):
        self._set_headers()
        self.wfile.write(self.INDEX_HTML.encode('utf8'))

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        print('Post by:', self.client_address)
        r, info = self.deal_post_data()
        print(info, 'by:', self.client_address)
        f = io.BytesIO()
        if r:
            f.write(b'Success\n')
        else:
            f.write(b'Failed\n')
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.send_header('Content-Length', str(length))
        self.end_headers()
        if f:
            self.copyfile(f, self.wfile)
            f.close()

    def deal_post_data(self):
        ctype, pdict = cgi.parse_header(self.headers['Content-Type'])
        pdict['boundary'] = bytes(pdict['boundary'], 'utf-8')
        pdict['CONTENT-LENGTH'] = int(self.headers['Content-Length'])
        content_length = pdict['CONTENT-LENGTH']
        print(content_length)
        if content_length > self.MAX_CONTENT_LENGTH:
            return (False, f'Content too large: {content_length}')
        if ctype == 'multipart/form-data':
            form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': self.headers['Content-Type']})
            records = [x for x in form['file']] if isinstance(form['file'], list) else [form['file']]
            for record in records:
                success, msg = self._print(record.file.read().decode('utf-8'), record.filename)
                if not success:
                    print(msg)
                    return (False, f'Failed to print file {record.filename}')
        return (True, 'All files printed')

def run(server_class=HTTPServer, handler_class=PrinterServer, addr='localhost', port=8000):
    server_address = (addr, port)
    httpd = server_class(server_address, handler_class)

    print(f'Starting httpd server on {addr}:{port}')
    print('')
    httpd.serve_forever()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Simple HTTP printer server')
    parser.add_argument(
        '-l',
        '--listen',
        default='0.0.0.0',
        help='Specify the IP address on which the server listens',
    )
    parser.add_argument(
        '-p',
        '--port',
        type=int,
        default=1234,
        help='Specify the port on which the server listens',
    )
    args = parser.parse_args()
    run(addr=args.listen, port=args.port)
