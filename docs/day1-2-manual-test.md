Days 1–2: Single SGLang Worker — Manual Test Guide

Objective

Start one SGLang model server on one NVIDIA GPU, confirm that its health endpoint responds, and send a test completion request through its OpenAI-compatible API.

Current preparation status

The local project structure and Nomad job specifications have been prepared. Both Nomad job files passed syntax validation. The actual model server has not yet been tested because SSH/GPU access to the target host is unavailable.

Target configuration

* Model: Qwen/Qwen2.5-3B-Instruct
* Server port: 8000
* Tensor parallel size: 1
* Health endpoint: /health
* Chat completion endpoint: /v1/chat/completions
* Target environment: GPU host gpu-01

Step 1: Check the GPU host

When SSH access is granted, connect using the connection details supplied by the mentor or administrator. Do not guess the host address or credentials.

Run:

nvidia-smi
docker --version

Confirm that the NVIDIA GPU is visible and that Docker is available if using the container-based method.

Step 2: Start SGLang manually

On the GPU host, run the following command, provided Docker and NVIDIA Container Toolkit are configured:

docker run --rm --gpus all \
  --shm-size 4g \
  -p 8000:8000 \
  lmsysorg/sglang:latest \
  python3 -m sglang.launch_server \
  --model-path Qwen/Qwen2.5-3B-Instruct \
  --host 0.0.0.0 \
  --port 8000 \
  --tp-size 1

Keep the terminal running and watch the startup logs. The server must finish loading the model before API tests are attempted. Adjust shared memory or model settings if the host’s available resources require it.

Step 3: Check server health

From the GPU host or a machine that can reach port 8000, run:

curl -i http://localhost:8000/health

Expected result: an HTTP success response from the health endpoint. Record the actual status and response.

Step 4: Send a chat completion request

Run this from a terminal that can reach the server:

curl -sS http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen2.5-3B-Instruct",
    "messages": [
      {
        "role": "user",
        "content": "Explain what a GPU does in two sentences."
      }
    ],
    "max_tokens": 100,
    "temperature": 0
  }'

Expected result: a JSON response containing a generated assistant message. Save the actual response as evidence.

If running the request from another computer, replace localhost with the reachable GPU host address.

Troubleshooting notes

* GPU unavailable: Check nvidia-smi, the NVIDIA driver, and NVIDIA Container Toolkit configuration.
* Model loading fails: Inspect container logs, available GPU memory, network access to download the model, and the model path.
* Port already in use: Check whether another process is listening on port 8000 before choosing a different port.
* Health check fails: Review the SGLang startup logs and confirm the server is ready before retrying.
* Connection refused: Confirm that the server is running, the port mapping is correct, and the client can reach the host.
* Out-of-memory error: Review model memory usage, available GPU memory, context length, and server settings before retrying.

Evidence to collect

1. GPU information from nvidia-smi.
2. SGLang startup logs showing successful model loading.
3. Health-check response.
4. Chat completion response.
5. Any errors encountered and the steps used to resolve them.

Completion criteria

Days 1–2 can be marked fully complete only after the single worker starts successfully and a real chat completion request returns a generated response. Until then, local preparation is complete, but the GPU inference test remains pending.