import cgi
import json
import os
from BaseHTTPServer import BaseHTTPRequestHandler

from HiddenBackup.ConfigLoader import Config


class BackupThread(BaseHTTPRequestHandler):
    def do_POST(self):
        # Response object
        response = {}

        config = Config()

        # Get data from client
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST',
                     'CONTENT_TYPE': self.headers['Content-Type'],
                     })

        file_path = config.backup_dir() + "/" + form['file'].filename
        data = form['file'].file.read()

        try:
            open(file_path, "wb").write(data)
        except IOError:
            pass

        # Send response
        response["status"] = os.path.exists(file_path)
        json_response = json.dumps(response)
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-length', len(json_response))
        self.end_headers()
        self.wfile.write(json_response)
