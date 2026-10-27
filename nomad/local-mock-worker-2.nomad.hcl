job "local-mock-worker-2" {
 datacenters = ["dc1"]
 type        = "service"
 group "mock" {
   count          = 1
   shutdown_delay = "10s"
   network {
     mode = "host"
     port "http" {
       static = 18001
     }
   }
   service {
     name         = "mock-sglang-worker-2"
     port         = "http"
     provider     = "consul"
     address      = "host.docker.internal"
     address_mode = "auto"
     check {
       name     = "mock-worker-2-health"
       type     = "http"
       path     = "/health"
       interval = "15s"
       timeout  = "5s"
     }
   }
   task "mock-worker-2" {
     driver = "raw_exec"
     config {
       command = "python"
       args = [
         "-c",
         "import json; from http.server import BaseHTTPRequestHandler, HTTPServer; H=type('H',(BaseHTTPRequestHandler,),{'do_GET':lambda s:(s.send_response(200),s.end_headers(),s.wfile.write(b'mock-worker-2-ok')) if s.path=='/health' else (s.send_response(404),s.end_headers()),'do_POST':lambda s:(s.send_response(200),s.send_header('Content-Type','application/json'),s.end_headers(),s.wfile.write(json.dumps({'worker':'mock-worker-2','choices':[{'message':{'role':'assistant','content':'Response from mock worker 2'}}]}).encode())) if s.path=='/v1/chat/completions' else (s.send_response(404),s.end_headers())}); HTTPServer(('0.0.0.0',18001),H).serve_forever()"
       ]
     }
     resources {
       cpu    = 100
       memory = 64
     }
   }
 }
}