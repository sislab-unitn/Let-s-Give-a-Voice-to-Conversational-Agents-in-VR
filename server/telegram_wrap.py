from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, ConversationHandler, MessageHandler
import requests

async def bot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = 'http://localhost:8080/text_converse?bot=movie_bot'
    response = requests.post(url, json={"sender": update.effective_user.first_name ,"message": update.message.text})
    dc = response.json()
    await update.message.reply_text(f'{dc["response"]}')
async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = 'http://localhost:8080/text_converse?bot=movie_bot'
    response = requests.post(url, json={"sender": update.effective_user.first_name ,"message": "/restart"})
    await update.message.reply_text('restarted')

app = ApplicationBuilder().token("6133668870:AAEQgq8kPCYM9IUbn3HoZJb8ktkATV_AwMY").build()

app.add_handler(CommandHandler('restart', restart))
app.add_handler(MessageHandler(None, bot))

app.run_polling()