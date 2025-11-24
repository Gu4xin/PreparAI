from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
import requests
from openai import OpenAI

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app)

# Leia a chave da OpenAI pela variável de ambiente OPENAI_API_KEY
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logging.warning("OPENAI_API_KEY não definida. Defina a variável de ambiente antes de executar o servidor.")

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


def montar_contexto(user_message: str) -> str:
    contexto = f"O usuário perguntou: {user_message}\n\n"
    contexto += "Responda de forma didática, citando se possível referências ou exemplos relevantes para o ENEM."
    return contexto


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"reply": "Mensagem vazia."}), 400

    if not client:
        logging.error("Cliente OpenAI não configurado. OPENAI_API_KEY ausente.")
        return jsonify({"reply": "Servidor não configurado para acessar a API da OpenAI."}), 500

    contexto = montar_contexto(user_message)

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é um assistente que ajuda com o ENEM."},
                {"role": "user", "content": contexto}
            ]
        )

        # parsing robusto: diferentes versões da lib retornam objetos/dicionários
        texto = None
        try:
            texto = completion['choices'][0]['message']['content']
        except Exception:
            try:
                choice = completion.choices[0]
                msg = getattr(choice, 'message', None)
                if msg is not None:
                    texto = getattr(msg, 'content', None) or (msg.get('content') if isinstance(msg, dict) else None)
            except Exception:
                texto = None

        if not texto:
            logging.warning("Não foi possível extrair conteúdo da resposta do modelo; retornando saída bruta.")
            texto = str(completion)

        return jsonify({"reply": texto})

    except Exception as e:
        logging.exception("Erro ao chamar OpenAI: %s", e)
        return jsonify({"reply": "Erro ao gerar resposta."}), 500


if __name__ == "__main__":
    # Recomendado executar com: set OPENAI_API_KEY=...; python model/app.py
    app.run(host="0.0.0.0", port=5000, debug=True)
