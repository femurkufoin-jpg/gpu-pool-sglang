job "local-mock-worker-3" {

  datacenters = ["dc1"]

  type        = "service"

  group "mock" {

    count          = 1

    shutdown_delay = "10s"

    network {

      mode = "host"

      port "http" {

        static = 18002

      }

    }

    service {

      name         = "mock-sglang-worker-3"

      port         = "http"

      provider     = "consul"

      address      = "host.docker.internal"

      address_mode = "auto"

      check {

        name     = "mock-worker-3-health"

        type     = "http"

        path     = "/health"

        interval = "15s"

        timeout  = "5s"

      }

    }

    task "mock-worker-3" {

      driver = "raw_exec"

      config {

        command = "python"

        args = [

          "-c",
<<-PYTHON

import json

from http.server import BaseHTTPRequestHandler, HTTPServer

class Handler(BaseHTTPRequestHandler):

    def send_json(self, data):

        body = json.dumps(data).encode("utf-8")

        self.send_response(200)

        self.send_header("Content-Type", "application/json")

        self.send_header("Content-Length", str(len(body)))

        self.end_headers()

        self.wfile.write(body)

    def do_GET(self):

        if self.path == "/health":

            self.send_json({

                "status": "ok",

                "worker": "mock-worker-3"

            })

        else:

            self.send_response(404)

            self.end_headers()

    def do_POST(self):

        length = int(self.headers.get("Content-Length", 0))

        request_body = json.loads(self.rfile.read(length) or b"{}")

        self.send_json({

            "id": "mock-worker-3-response",

            "object": "chat.completion",

            "model": request_body.get("model", "mock-model"),

            "choices": [

                {

                    "index": 0,

                    "message": {

                        "role": "assistant",

                        "content": "Response from mock worker 3"

                    },

                    "finish_reason": "stop"

                }

            ]

        })

    def log_message(self, format, *args):

        pass

HTTPServer(("0.0.0.0", 18002), Handler).serve_forever()

          PYTHON

        ]

      }

      resources {

        cpu    = 100

        memory = 64

      }

    }

  }

}
