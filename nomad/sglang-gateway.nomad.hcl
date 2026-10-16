job "sglang-gateway" {
  datacenters = ["dc1"]
  type        = "service"
  group "gateway" {
    count          = 1
    shutdown_delay = "10s"
    network {
      port "http" {
        static = 30000
        to     = 30000
      }
    }
    service {
      name     = "sglang-gateway"
      port     = "http"
      provider = "consul"
      check {
        name     = "gateway-health"
        type     = "http"
        path     = "/health"
        interval = "15s"
        timeout  = "5s"
      }
    }
    task "gateway" {
      driver = "docker"
      config {
        image      = "lmsysorg/sgl-model-gateway:latest"
        ports      = ["http"]
        force_pull = true
        args = [
          "--worker-urls",
          "http://sglang-worker.service.consul:8000",
          "--policy",
          "cache_aware",
          "--host",
          "0.0.0.0",
          "--port",
          "30000"
        ]
      }
      resources {
        cpu    = 500
        memory = 512
      }
      restart {
        attempts = 3
        interval = "5m"
        delay    = "15s"
        mode     = "fail"
      }
      kill_timeout = "30s"
    }
  }
}