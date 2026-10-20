from flask import Flask, jsonify, request

app = Flask(__name__)


@app.get("/health")

def health():

    return jsonify({"status": "ok"})


@app.post("/v1/chat/completions")

def chat_completions():

    data = request.get_json(silent=True) or {}

    messages = data.get("messages", [])

    user_message = messages[-1].get("content", "") if messages else ""

    return jsonify({

        "id": "mock-completion-001",

        "object": "chat.completion",

        "model": data.get("model", "local-mock-model"),

        "choices": [{

            "index": 0,

            "message": {

                "role": "assistant",

                "content": f"Mock worker received your message: {user_message}"

            },

            "finish_reason": "stop"

        }]

    })


if __name__ == "__main__":

    app.run(host="127.0.0.1", port=8000, debug=False)
 