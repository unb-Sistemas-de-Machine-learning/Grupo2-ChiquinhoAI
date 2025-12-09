import os
import logging
import requests
from pathlib import Path
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

ENV_PATH = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=True)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = os.getenv("API_URL", "http://localhost:55555/response")

PORT = int(os.environ.get('PORT', 8443))
WEBHOOK_URL = os.getenv("WEBHOOK_URL") 


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    welcome_message = """
*Olá! Eu sou o ChiquinhoAI!*

Sou um assistente virtual da UnB especializado em responder perguntas sobre:

• 📚 PIBID e programas de ensino
• 🎓 Editais e oportunidades
• 📖 Licenciaturas e cursos
• 🏫 Estágios e bolsas
• 📋 Processos acadêmicos

*Como usar:*
Basta me enviar sua pergunta e eu vou buscar as informações mais relevantes!

*Exemplos:*
• "O que é o PIBID?"
• "Como funciona a monitoria?"
• "Quais são os editais abertos?"

Pode perguntar! 
    """
    await update.message.reply_text(welcome_message, parse_mode='Markdown')


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa as mensagens dos usuários"""
    user_message = update.message.text
    user_name = update.effective_user.first_name
    
    logger.info(f"Pergunta de {user_name}: {user_message}")
    
    await update.message.chat.send_action(action="typing")
    
    try:
        response = requests.get(
            API_URL,
            params={"pergunta": user_message},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            resposta = data.get("resposta", "Desculpe, não consegui processar sua pergunta.")
            
            await update.message.reply_text(resposta)
            logger.info(f"Resposta enviada para {user_name}")
        else:
            await update.message.reply_text(
                "Desculpe, tive um problema ao processar sua pergunta. Tente novamente!"
            )
            logger.error(f"Erro na API: Status {response.status_code}")
            
    except requests.exceptions.Timeout:
        await update.message.reply_text(
            "consulta está demorando muito. Tente uma pergunta mais específica!"
        )
    except Exception as e:
        await update.message.reply_text(
            " Ocorreu um erro ao processar sua pergunta. Por favor, tente novamente!"
        )
        logger.error(f"Erro: {e}", exc_info=True)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Trata erros"""
    logger.error(f"Update {update} causou erro {context.error}")


def main():
    """Inicia o bot"""
    if not TELEGRAM_TOKEN:
        logger.error(" Configure o TELEGRAM_BOT_TOKEN no arquivo .env antes de rodar!")
        return
    
    logger.info(" Iniciando ChiquinhoAI Bot")
    

    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
    
    
    if WEBHOOK_URL:
        logger.info(f"MODO WEBHOOK ATIVADO - Rodando na porta {PORT}")
        logger.info(f"URL Base: {WEBHOOK_URL}")
        
        application.run_webhook(
            listen="0.0.0.0",       
            port=PORT,             
            url_path=TELEGRAM_TOKEN, 
            webhook_url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}" 
        )
        
    else:
        logger.info(" MODO LOCAL (POLLING) ATIVADO")
        logger.info(" Para modo produção, configure a variável WEBHOOK_URL")
        application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()