job "sglang-worker" {
  datacenters = ["dc1"]
  type        = "service"
  group "sglang" {
    count          = 1
    shutdown_delay = "10s"
    network {
      port "http" {
        to = 8000
      }
    }
    service {
      name     = "sglang-worker"
      port     = "http"
      provider = "consul"
      check {
        name     = "sglang-health"
        type     = "http"
        path     = "/health"
        interval = "15s"
        timeout  = "5s"
      }
    }
    task "sglang" {
      driver = "docker"
      config {
        image      = "lmsysorg/sglang:latest"
        ports      = ["http"]
        force_pull = true
        command = "python3"
        args = [
          "-m",
          "sglang.launch_server",
          "--model-path",
          "Qwen/Qwen2.5-3B-Instruct",
          "--host",
          "0.0.0.0",
          "--port",
          "8000",
          "--tp-size",
          "1"
        ]
      }
      resources {
        cpu    = 4000
        memory = 8192
        device "nvidia/gpu" {
          count = 1
        }
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