import os
import threading

import telebot
from flask import Flask, abort, request
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID_AUTORIZADO = os.getenv("TELEGRAM_CHAT_ID")  # opcional: restringe a um chat específico

app = Flask(__name__)
bot = telebot.TeleBot(TOKEN)

FORMATO_ESPERADO = (
    "Formato esperado:\n"
    "CNPJ: 12.345.678/0001-90\n"
    "Valor: 1500,00\n"
    "Descrição: Consultoria em TI"
)


def parse_mensagem(texto: str) -> dict:
    """
    Extrai campos chave:valor da mensagem.
    Retorna dict com chaves em minúsculas sem acento.
    """
    mapa_chaves = {
        "cnpj": "cnpj",
        "valor": "valor",
        "descrição": "descricao",
        "descricao": "descricao",
        "descricao do servico": "descricao",
        "descrição do serviço": "descricao",
    }
    dados = {}
    for linha in texto.strip().splitlines():
        if ":" in linha:
            chave, _, valor = linha.partition(":")
            chave_normalizada = chave.strip().lower()
            if chave_normalizada in mapa_chaves:
                dados[mapa_chaves[chave_normalizada]] = valor.strip()
    return dados


def chat_autorizado(chat_id: int) -> bool:
    if not CHAT_ID_AUTORIZADO:
        return True  # sem restrição configurada
    return str(chat_id) == CHAT_ID_AUTORIZADO


@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    if request.content_type != "application/json":
        abort(403)
    update = telebot.types.Update.de_json(request.get_data(as_text=True))
    bot.process_new_updates([update])
    return "OK", 200


@bot.message_handler(commands=["start", "ajuda"])
def handle_ajuda(message):
    bot.send_message(
        message.chat.id,
        "Olá! Envie os dados da NF no seguinte formato:\n\n" + FORMATO_ESPERADO,
    )


@bot.message_handler(func=lambda m: True)
def handle_message(message):
    chat_id = message.chat.id

    if not chat_autorizado(chat_id):
        bot.send_message(chat_id, "Acesso não autorizado.")
        return

    texto = message.text or ""
    dados = parse_mensagem(texto)

    campos_obrigatorios = ["cnpj", "valor", "descricao"]
    faltando = [c for c in campos_obrigatorios if c not in dados]

    if faltando:
        bot.send_message(
            chat_id,
            f"Não consegui identificar: {', '.join(faltando)}.\n\n" + FORMATO_ESPERADO,
        )
        return

    bot.send_message(
        chat_id,
        f"Recebi os dados:\n"
        f"• CNPJ: {dados['cnpj']}\n"
        f"• Valor: R$ {dados['valor']}\n"
        f"• Descrição: {dados['descricao']}\n\n"
        "Iniciando automação...",
    )

    thread = threading.Thread(
        target=rodar_automacao,
        args=(chat_id, dados),
        daemon=True,
    )
    thread.start()


def rodar_automacao(chat_id: int, dados: dict):
    from automacao import executar

    def callback(msg: str):
        bot.send_message(chat_id, msg, parse_mode="Markdown")

    try:
        executar(dados, callback=callback)
    except Exception as e:
        bot.send_message(chat_id, f"Erro na automação: {e}")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
