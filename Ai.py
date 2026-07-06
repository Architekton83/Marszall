import os
import logging
import numpy as np
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from pneuma_heptada_swarm import PneumaSwarm

TELEGRAM_TOKEN = "8760591381:AAH0n0ipqS0EHPRFDWTET4VzgGpnPNvMkOY"
GROQ_API_KEY = "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"
swarm = PneumaSwarm(num_agents=32)

def question_to_vec(text: str) -> np.ndarray:
    vec = np.zeros(19, dtype=float)
    for i, ch in enumerate(text.encode("utf-8")):
        vec[i % 19] += (ch % 31) / 31.0
    n = np.linalg.norm(vec)
    return vec / n if n > 1e-12 else np.random.randn(19)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Pneuma bot działa. Napisz wiadomość.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rep = swarm.report()
    await update.message.reply_text(
        f"Gen: {rep['generation']}\n"
        f"Coherence: {rep['global_coherence']:.4f}\n"
        f"Stabilna: {rep['phases']['STABILNA']}\n"
        f"Krytyczna: {rep['phases']['KRYTYCZNA']}\n"
        f"Kolaps: {rep['phases']['KOLAPS']}"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.message.text
    vec = question_to_vec(q)
    for _ in range(5):
        swarm.tick(vec)
    rep = swarm.report()
    msg = (
        f"Gen: {rep['generation']}\n"
        f"Coherence: {rep['global_coherence']:.4f}\n"
        f"Stabilna: {rep['phases']['STABILNA']}\n"
        f"Krytyczna: {rep['phases']['KRYTYCZNA']}\n"
        f"Kolaps: {rep['phases']['KOLAPS']}"
    )
    await update.message.reply_text(msg[:4000])

def main():
    logging.basicConfig(level=logging.INFO)
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
