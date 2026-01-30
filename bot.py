import logging
import os
from datetime import datetime
from typing import Dict
from enum import Enum

from telegram import (
    Update, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup
)
from telegram.ext import (
    Application, 
    CommandHandler, 
    CallbackQueryHandler, 
    MessageHandler, 
    filters, 
    ContextTypes, 
    ConversationHandler
)

# ========== CONFIGURAÇÃO ==========
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Tokens (serão configurados no Railway)
TOKEN = os.getenv('TOKEN')
ORDER_GROUP_ID = os.getenv('ORDER_GROUP_ID', '-1003565140066')

if not TOKEN:
    logger.error("❌ TOKEN não configurado!")
    logger.error("Configure a variável TOKEN no Railway")
    exit(1)

logger.info(f"✅ Bot iniciando...")
logger.info(f"✅ Grupo: {ORDER_GROUP_ID}")

# ========== ESTADOS ==========
class States(Enum):
    CHOOSING_LANGUAGE = 1
    MAIN_MENU = 2
    CHOOSING_SERVICE = 3
    PERSONALIZED_SERVICE = 4
    TELEGRAM_USERNAME = 5
    OBSERVATIONS = 6
    CONFIRMATION = 7

# ========== TEXTOS ==========
TEXTS = {
    'portugues': {
        'welcome': "🌐 *SELECIONE SEU IDIOMA*\n\nEscolha idioma:",
        
        'main_menu': """🏪 *BEM-VINDO À RICK SHOP* 🏪

*SERVIÇOS:*
• 📋 Listas telefônicas
• 📞 Números para SMS
• 📱 Contas de Instagram  
• 👍 Curtidas TikTok
• 🎨 Perfil profissional
• 🔍 Painel de dados
• 🌍 Listas internacionais
• 💡 Ideias para empresa
• 🛠️ Serviços personalizados

💰 *PAGAMENTO:* USDT TRC20
⚡ *ENTREGA:* Rápida

Escolha:""",
        
        'service_details': {
            'phone_lists': """📋 *LISTAS TELEFÔNICAS*
💰 De $200
⚡ 24h após pagamento""",
            
            'sms_numbers': """📞 *NÚMEROS SMS*
💰 $15-30/número
⚡ Imediato""",
            
            'instagram_accounts': """📱 *INSTAGRAM*
💰 $50-2.500
⚡ 1-2 horas""",
            
            'tiktok_likes': """👍 *TIKTOK*
💰 $10-50
🚀 24-48h""",
            
            'profile_setup': """🎨 *PERFIL*
💰 $300-800
⏱️ 3-5 dias""",
            
            'data_panel': """🔍 *PAINEL*
💰 $1.500/mês
📊 Milhões""",
            
            'international_lists': """🌍 *INTERNACIONAL*
💰 $200-800
🌎 +50 países""",
            
            'business_ideas': """💡 *IDEIAS*
💰 $500-1.500
📅 5-10 dias""",
            
            'personalized': """🛠️ *PERSONALIZADO*
💰 60% + 40%
💬 Descreva:"""
        },
        
        'need_personalized': "📝 *Descreva:*",
        'ask_telegram': "📲 *Seu @:*",
        'ask_observations': "📌 *Observações:*",
        'confirmation': "✅ *Confirmado!* 24h.",
        'error': "❌ Erro. /start",
        'cancel': "❌ Cancelado.",
        'invalid_username': "❌ @ inválido."
    }
}

# ========== SERVIÇOS ==========
SERVICES = {
    1: {'key': 'phone_lists', 'name': '📋 Listas'},
    2: {'key': 'sms_numbers', 'name': '📞 SMS'},
    3: {'key': 'instagram_accounts', 'name': '📱 Instagram'},
    4: {'key': 'tiktok_likes', 'name': '👍 TikTok'},
    5: {'key': 'profile_setup', 'name': '🎨 Perfil'},
    6: {'key': 'data_panel', 'name': '🔍 Painel'},
    7: {'key': 'international_lists', 'name': '🌍 Internacional'},
    8: {'key': 'business_ideas', 'name': '💡 Ideias'},
    9: {'key': 'personalized', 'name': '🛠️ Personalizado'},
}

# ========== DADOS ==========
user_data = {}

# ========== FUNÇÕES ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    logger.info(f"Usuário {user.id} iniciou")
    
    user_id = str(user.id)
    if user_id in user_data:
        del user_data[user_id]
    
    keyboard = [[InlineKeyboardButton("🇺🇸 English", callback_data="lang_english")]]
    await update.message.reply_text(
        text=TEXTS['portugues']['welcome'],
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    return States.CHOOSING_LANGUAGE

async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    user_id = str(query.from_user.id)
    user_data[user_id] = {'language': 'portugues'}
    
    keyboard = []
    for i in range(1, 10, 2):
        row = [
            InlineKeyboardButton(SERVICES[i]['name'], callback_data=f"service_{i}"),
            InlineKeyboardButton(SERVICES[i+1]['name'], callback_data=f"service_{i+1}") if i+1 <= 9 else None
        ]
        keyboard.append([b for b in row if b])
    
    keyboard.append([InlineKeyboardButton("❌ Cancelar", callback_data="cancel")])
    
    await query.edit_message_text(
        text=TEXTS['portugues']['main_menu'],
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    return States.MAIN_MENU

async def choose_service(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    user_id = str(query.from_user.id)
    service_number = int(query.data.replace('service_', ''))
    
    user_data[user_id]['service_number'] = service_number
    service_info = SERVICES[service_number]
    user_data[user_id]['service_key'] = service_info['key']
    user_data[user_id]['service_name'] = service_info['name']
    
    service_text = TEXTS['portugues']['service_details'][service_info['key']]
    
    keyboard = [[
        InlineKeyboardButton("✅ Selecionar", callback_data="proceed"),
        InlineKeyboardButton("🔙 Voltar", callback_data="back_to_menu")
    ]]
    
    await query.edit_message_text(
        text=service_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    return States.CHOOSING_SERVICE

async def proceed_service(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    user_id = str(query.from_user.id)
    
    if user_data[user_id]['service_key'] == 'personalized':
        await query.edit_message_text(
            text=TEXTS['portugues']['need_personalized'],
            parse_mode='Markdown'
        )
        return States.PERSONALIZED_SERVICE
    
    await query.edit_message_text(
        text=TEXTS['portugues']['ask_telegram'],
        parse_mode='Markdown'
    )
    return States.TELEGRAM_USERNAME

async def personalized_service(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = str(update.message.from_user.id)
    user_data[user_id]['personalized_description'] = update.message.text
    
    await update.message.reply_text(
        text=TEXTS['portugues']['ask_telegram'],
        parse_mode='Markdown'
    )
    return States.TELEGRAM_USERNAME

async def process_telegram_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = str(update.message.from_user.id)
    username = update.message.text.strip()
    
    if not username.startswith('@') or len(username) < 2:
        await update.message.reply_text(
            text=TEXTS['portugues']['invalid_username'],
            parse_mode='Markdown'
        )
        return States.TELEGRAM_USERNAME
    
    user_data[user_id]['telegram_username'] = username
    
    await update.message.reply_text(
        text=TEXTS['portugues']['ask_observations'],
        parse_mode='Markdown'
    )
    return States.OBSERVATIONS

async def process_observations(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = str(update.message.from_user.id)
    observations = update.message.text
    user_data[user_id]['observations'] = observations
    
    service_name = user_data[user_id]['service_name']
    telegram_username = user_data[user_id]['telegram_username']
    
    if user_data[user_id].get('personalized_description'):
        service_name = f"{service_name}: {user_data[user_id]['personalized_description']}"
    
    confirmation_text = f"""✅ *PEDIDO CONFIRMADO!*

📋 *Resumo:*
• Serviço: {service_name}
• Telegram: @{telegram_username}
• Observações: {observations}

📞 *Entraremos em contato em 24h!*
💰 *Pagamento: USDT TRC20*"""
    
    keyboard = [
        [InlineKeyboardButton("✅ Confirmar", callback_data="confirm_order")],
        [InlineKeyboardButton("❌ Cancelar", callback_data="cancel")]
    ]
    
    await update.message.reply_text(
        text=confirmation_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    return States.CONFIRMATION

async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    user_id = str(query.from_user.id)
    user_info = user_data.get(user_id, {})
    
    if not user_info:
        await query.edit_message_text("❌ Dados perdidos. /start")
        return ConversationHandler.END
    
    # Preparar dados
    order_data = {
        'user_id': query.from_user.id,
        'username': query.from_user.username,
        'full_name': query.from_user.full_name,
        'service': user_info['service_name'],
        'telegram_username': user_info.get('telegram_username', ''),
        'observations': user_info.get('observations', ''),
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'personalized_desc': user_info.get('personalized_description', '')
    }
    
    # Mensagem para o grupo
    group_message = f"""📋 *NOVO PEDIDO - RICK SHOP*

👤 *CLIENTE:*
• ID: {order_data['user_id']}
• Nome: {order_data['full_name']}
• Username: @{order_data['username'] or 'N/A'}
• Telegram: {order_data['telegram_username']}

🛒 *SERVIÇO:*
{order_data['service']}

📝 *OBSERVAÇÕES:*
{order_data['observations']}

⏰ *DATA:*
{order_data['timestamp']}

{'✍️ *DESCRIÇÃO PERSONALIZADA:*' if order_data['personalized_desc'] else ''}
{order_data['personalized_desc'] if order_data['personalized_desc'] else ''}

🚨 *CONTATAR EM 24H!*"""
    
    try:
        # ENVIAR PARA O GRUPO
        await context.bot.send_message(
            chat_id=ORDER_GROUP_ID,
            text=group_message,
            parse_mode='Markdown'
        )
        
        logger.info(f"✅ Pedido enviado para grupo!")
        
        # Mensagem final para usuário
        await query.edit_message_text(
            text="""✅ *PEDIDO REGISTRADO!*

📬 Enviado para nossa equipe.
📞 Entraremos em contato em até 24h.

💰 *PAGAMENTO:*
• Token: USDT (TRC20)
• Rede: TRON
• Valor: Informado pelo atendente

🛡️ *RICK SHOP - QUALIDADE!*

/start para novo pedido""",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        await query.edit_message_text(
            text=f"✅ Pedido recebido!\n\nErro técnico: {str(e)[:100]}...\n\nNossa equipe será notificada."
        )
    
    # Limpar dados
    if user_id in user_data:
        del user_data[user_id]
    
    return ConversationHandler.END

async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    user_id = str(query.from_user.id)
    
    keyboard = []
    for i in range(1, 10, 2):
        row = [
            InlineKeyboardButton(SERVICES[i]['name'], callback_data=f"service_{i}"),
            InlineKeyboardButton(SERVICES[i+1]['name'], callback_data=f"service_{i+1}") if i+1 <= 9 else None
        ]
        keyboard.append([b for b in row if b])
    
    keyboard.append([InlineKeyboardButton("❌ Cancelar", callback_data="cancel")])
    
    await query.edit_message_text(
        text=TEXTS['portugues']['main_menu'],
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    return States.MAIN_MENU

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    user_id = str(query.from_user.id)
    if user_id in user_data:
        del user_data[user_id]
    
    await query.edit_message_text("❌ Cancelado. /start para recomeçar.")
    return ConversationHandler.END

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Erro: {context.error}")

# ========== MAIN ==========
def main() -> None:
    """Executa o bot."""
    application = Application.builder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            States.CHOOSING_LANGUAGE: [
                CallbackQueryHandler(choose_language, pattern='^lang_')
            ],
            States.MAIN_MENU: [
                CallbackQueryHandler(choose_service, pattern='^service_'),
                CallbackQueryHandler(cancel, pattern='^cancel$')
            ],
            States.CHOOSING_SERVICE: [
                CallbackQueryHandler(proceed_service, pattern='^proceed$'),
                CallbackQueryHandler(back_to_menu, pattern='^back_to_menu$')
            ],
            States.PERSONALIZED_SERVICE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, personalized_service)
            ],
            States.TELEGRAM_USERNAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_telegram_username)
            ],
            States.OBSERVATIONS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_observations)
            ],
            States.CONFIRMATION: [
                CallbackQueryHandler(confirm_order, pattern='^confirm_order$'),
                CallbackQueryHandler(cancel, pattern='^cancel$')
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    application.add_handler(conv_handler)
    application.add_error_handler(error_handler)
    
    logger.info("✅ Bot iniciando...")
    application.run_polling()

if __name__ == '__main__':
    main()