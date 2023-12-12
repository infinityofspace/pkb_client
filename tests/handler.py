import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from importlib import resources

from tests import responses

API_KEY = "key"
SECRET_API_KEY = "secret"


class RequestHandler(BaseHTTPRequestHandler):
    def _send_response(self, message, status=200):
        self.send_response(status)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps(message), "utf8"))

    def handle_auth(self):
        content_length = int(self.headers["Content-Length"])
        body = self.rfile.read(content_length)
        body = json.loads(body.decode("utf8"))
        if body.get("apikey", None) != API_KEY or body.get("secretapikey", None) != SECRET_API_KEY:
            with resources.open_text(responses, "invalid_api_key.json") as f:
                response = json.load(f)
            self._send_response(response, 403)
            return False
        return True

    def do_POST(self):
        if self.path == "/api/json/v3/pricing/get":
            with resources.open_text(responses, "pricing_get.json") as f:
                response = json.load(f)
            self._send_response(response)
        else:
            if not self.handle_auth():
                return
            if self.path == "/api/json/v3/ping":
                with resources.open_text(responses, "ping.json") as f:
                    response = json.load(f)
                self._send_response(response)

            elif self.path == "/api/json/v3/domain/getNs/example.com":
                with resources.open_text(responses, "domain_getNs.json") as f:
                    response = json.load(f)
                self._send_response(response)
            elif self.path == "/api/json/v3/domain/listAll":
                with resources.open_text(responses, "domain_listAll.json") as f:
                    response = json.load(f)
                self._send_response(response)
            elif self.path == "/api/json/v3/domain/updateNs/example.com":
                with resources.open_text(responses, "success.json") as f:
                    response = json.load(f)
                self._send_response(response)
            elif self.path == "/api/json/v3/domain/getUrlForwarding/example.com":
                with resources.open_text(responses, "domain_getUrlForwarding.json") as f:
                    response = json.load(f)
                self._send_response(response)
            elif self.path == "/api/json/v3/domain/addUrlForward/example.com":
                with resources.open_text(responses, "success.json") as f:
                    response = json.load(f)
                self._send_response(response)
            elif self.path == "/api/json/v3/domain/deleteUrlForward/example.com/123456":
                with resources.open_text(responses, "success.json") as f:
                    response = json.load(f)
                self._send_response(response)

            elif self.path == "/api/json/v3/dns/create/example.com":
                with resources.open_text(responses, "dns_create.json") as f:
                    response = json.load(f)
                self._send_response(response)
            elif self.path == "/api/json/v3/dns/edit/example.com/123456":
                with resources.open_text(responses, "success.json") as f:
                    response = json.load(f)
                self._send_response(response)
            elif self.path == "/api/json/v3/dns/delete/example.com/123456":
                with resources.open_text(responses, "success.json") as f:
                    response = json.load(f)
                self._send_response(response)
            elif self.path == "/api/json/v3/dns/retrieve/example.com":
                with resources.open_text(responses, "dns_retrieve.json") as f:
                    response = json.load(f)
                self._send_response(response)
            else:
                self.send_error(404)


if __name__ == "__main__":
    server = HTTPServer(("localhost", 8000), RequestHandler)
    server.serve_forever()
