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

# ========== CONFIGURAÇÕES DO BOT ==========
BOT_USERNAME = "@Rick_shoppbot"  # SEU BOT CORRETO
TOKEN = os.getenv('TOKEN')
ORDER_GROUP_ID = os.getenv('ORDER_GROUP_ID', '-1003565140066')

if not TOKEN:
    logger.error("❌ TOKEN não configurado!")
    logger.error("Configure a variável TOKEN no Railway")
    exit(1)

logger.info(f"✅ Bot {BOT_USERNAME} iniciando...")
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
        'welcome': f"🌐 *SELECIONE SEU IDIOMA*\n\nBem-vindo ao {BOT_USERNAME}! Escolha idioma:",
        
        'main_menu': f"""🏪 *BEM-VINDO À RICK SHOP* 🏪

*SERVIÇOS PREMIUM {BOT_USERNAME}:*
• 📋 Listas telefônicas brasileiras
• 📞 Números para SMS/Redes Sociais
• 📱 Contas de Instagram
• 👍 Curtidas TikTok
• 🎨 Perfil profissional
• 🔍 Painel de dados
• 🌍 Listas internacionais
• 💡 Ideias para empresa
• 🛠️ Serviços personalizados

💰 *PAGAMENTO:* USDT TRC20
⚡ *ENTREGA:* Rápida e segura

Escolha um serviço:""",
        
        'service_details': {
            'phone_lists': """📋 *LISTAS TELEFÔNICAS BRASILEIRAS*
💰 Preço: A partir de $200
⚡ Entrega: 24h após pagamento""",
            
            'sms_numbers': """📞 *NÚMEROS PARA SMS/REDES SOCIAIS*
💰 Preço: $15-30/número
⚡ Ativação: Imediata""",
            
            'instagram_accounts': """📱 *CONTAS DE INSTAGRAM*
💰 Preço: $50-2.500
⚡ Entrega: 1-2 horas""",
            
            'tiktok_likes': """👍 *CURTIDAS TIKTOK*
💰 Preço: $10-50
🚀 Resultados: 24-48h""",
            
            'profile_setup': """🎨 *MONTAGEM DE PERFIL PROFISSIONAL*
💰 Preço: $300-800
⏱️ Prazo: 3-5 dias""",
            
            'data_panel': """🔍 *PAINEL DE DADOS BRASILEIROS*
💰 Assinatura: $1.500/mês
📊 Dados: Milhões de registros""",
            
            'international_lists': """🌍 *LISTAS INTERNACIONAIS*
💰 Preço: $200-800
🌎 Países: +50 disponíveis""",
            
            'business_ideas': """💡 *IDEIAS PARA EMPRESA*
💰 Preço: $500-1.500
📅 Prazo: 5-10 dias""",
            
            'personalized': """🛠️ *SERVIÇO PERSONALIZADO*
💰 Pagamento: 60% antecipado + 40% conclusão
💬 Descreva sua necessidade:"""
        },
        
        'need_personalized': "📝 *Descreva detalhadamente o que precisa:*",
        'ask_telegram': "📲 *Informe seu @ do Telegram (ex: @seunome):*",
        'ask_observations': "📌 *Observações adicionais (opcional):*",
        'confirmation': f"✅ *Pedido confirmado!* Entraremos em contato via {BOT_USERNAME} em 24h.",
        'error': f"❌ Erro. Use /start no {BOT_USERNAME} para recomeçar.",
        'cancel': "❌ Operação cancelada.",
        'invalid_username': "❌ @ inválido. Deve ser como @seunome"
    },
    
    'english': {
        'welcome': f"🌐 *SELECT YOUR LANGUAGE*\n\nWelcome to {BOT_USERNAME}! Choose language:",
        
        'main_menu': f"""🏪 *WELCOME TO RICK SHOP* 🏪

*PREMIUM SERVICES {BOT_USERNAME}:*
• 📋 Brazilian phone lists
• 📞 SMS/Social media numbers
• 📱 Instagram accounts
• 👍 TikTok likes
• 🎨 Professional profile
• 🔍 Data panel
• 🌍 International lists
• 💡 Business ideas
• 🛠️ Personalized services

💰 *PAYMENT:* USDT TRC20
⚡ *DELIVERY:* Fast and secure

Choose a service:""",
        
        'service_details': {
            'phone_lists': """📋 *BRAZILIAN PHONE LISTS*
💰 Price: From $200
⚡ Delivery: 24h after payment""",
            
            'sms_numbers': """📞 *SMS/SOCIAL MEDIA NUMBERS*
💰 Price: $15-30/number
⚡ Activation: Immediate""",
            
            'instagram_accounts': """📱 *INSTAGRAM ACCOUNTS*
💰 Price: $50-2,500
⚡ Delivery: 1-2 hours""",
            
            'tiktok_likes': """👍 *TIKTOK LIKES*
💰 Price: $10-50
🚀 Results: 24-48h""",
            
            'profile_setup': """🎨 *PROFESSIONAL PROFILE SETUP*
💰 Price: $300-800
⏱️ Deadline: 3-5 days""",
            
            'data_panel': """🔍 *BRAZILIAN DATA PANEL*
💰 Subscription: $1,500/month
📊 Data: Millions of records""",
            
            'international_lists': """🌍 *INTERNATIONAL LISTS*
💰 Price: $200-800
🌎 Countries: +50 available""",
            
            'business_ideas': """💡 *BUSINESS IDEAS*
💰 Price: $500-1,500
📅 Deadline: 5-10 days""",
            
            'personalized': """🛠️ *PERSONALIZED SERVICE*
💰 Payment: 60% upfront + 40% completion
💬 Describe your need:"""
        },
        
        'need_personalized': "📝 *Describe in detail what you need:*",
        'ask_telegram': "📲 *Provide your Telegram @ (ex: @yourname):*",
        'ask_observations': "📌 *Additional observations (optional):*",
        'confirmation': f"✅ *Order confirmed!* We'll contact via {BOT_USERNAME} within 24h.",
        'error': f"❌ Error. Use /start on {BOT_USERNAME} to restart.",
        'cancel': "❌ Operation cancelled.",
        'invalid_username': "❌ Invalid @. Must be like @username"
    }
}

# ========== SERVIÇOS ==========
SERVICES = {
    1: {'key': 'phone_lists', 'name_pt': '📋 Listas Telefônicas', 'name_en': '📋 Phone Lists'},
    2: {'key': 'sms_numbers', 'name_pt': '📞 Números SMS', 'name_en': '📞 SMS Numbers'},
    3: {'key': 'instagram_accounts', 'name_pt': '📱 Contas Instagram', 'name_en': '📱 Instagram'},
    4: {'key': 'tiktok_likes', 'name_pt': '👍 Curtidas TikTok', 'name_en': '👍 TikTok Likes'},
    5: {'key': 'profile_setup', 'name_pt': '🎨 Perfil Profissional', 'name_en': '🎨 Profile Setup'},
    6: {'key': 'data_panel', 'name_pt': '🔍 Painel de Dados', 'name_en': '🔍 Data Panel'},
    7: {'key': 'international_lists', 'name_pt': '🌍 Listas Internacionais', 'name_en': '🌍 International'},
    8: {'key': 'business_ideas', 'name_pt': '💡 Ideias Empresa', 'name_en': '💡 Business Ideas'},
    9: {'key': 'personalized', 'name_pt': '🛠️ Personalizado', 'name_en': '🛠️ Personalized'},
}

# ========== DADOS ==========
user_data = {}

# ========== FUNÇÕES ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    logger.info(f"Usuário {user.id} iniciou {BOT_USERNAME}")
    
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
    language = 'english' if 'english' in query.data else 'portugues'
    user_data[user_id] = {'language': language}
    
    service_names = SERVICES
    keyboard = []
    for i in range(1, 10, 2):
        row = []
        for j in range(i, min(i+2, 10)):
            name_key = 'name_en' if language == 'english' else 'name_pt'
            row.append(InlineKeyboardButton(
                service_names[j][name_key], 
                callback_data=f"service_{j}"
            ))
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton(
        "❌ Cancel" if language == 'english' else "❌ Cancelar", 
        callback_data="cancel"
    )])
    
    await query.edit_message_text(
        text=TEXTS[language]['main_menu'],
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
    
    language = user_data[user_id]['language']
    name_key = 'name_en' if language == 'english' else 'name_pt'
    user_data[user_id]['service_name'] = service_info[name_key]
    
    service_text = TEXTS[language]['service_details'][service_info['key']]
    
    select_text = "✅ Select" if language == 'english' else "✅ Selecionar"
    back_text = "🔙 Back" if language == 'english' else "🔙 Voltar"
    
    keyboard = [[
        InlineKeyboardButton(select_text, callback_data="proceed"),
        InlineKeyboardButton(back_text, callback_data="back_to_menu")
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
    language = user_data[user_id]['language']
    
    if user_data[user_id]['service_key'] == 'personalized':
        await query.edit_message_text(
            text=TEXTS[language]['need_personalized'],
            parse_mode='Markdown'
        )
        return States.PERSONALIZED_SERVICE
    
    await query.edit_message_text(
        text=TEXTS[language]['ask_telegram'],
        parse_mode='Markdown'
    )
    return States.TELEGRAM_USERNAME

async def personalized_service(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = str(update.message.from_user.id)
    user_data[user_id]['personalized_description'] = update.message.text
    
    language = user_data[user_id]['language']
    await update.message.reply_text(
        text=TEXTS[language]['ask_telegram'],
        parse_mode='Markdown'
    )
    return States.TELEGRAM_USERNAME

async def process_telegram_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = str(update.message.from_user.id)
    language = user_data[user_id]['language']
    username = update.message.text.strip()
    
    if not username.startswith('@') or len(username) < 2:
        await update.message.reply_text(
            text=TEXTS[language]['invalid_username'],
            parse_mode='Markdown'
        )
        return States.TELEGRAM_USERNAME
    
    user_data[user_id]['telegram_username'] = username
    
    await update.message.reply_text(
        text=TEXTS[language]['ask_observations'],
        parse_mode='Markdown'
    )
    return States.OBSERVATIONS

async def process_observations(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = str(update.message.from_user.id)
    language = user_data[user_id]['language']
    observations = update.message.text
    user_data[user_id]['observations'] = observations
    
    service_name = user_data[user_id]['service_name']
    telegram_username = user_data[user_id]['telegram_username']
    
    if user_data[user_id].get('personalized_description'):
        service_name = f"{service_name}: {user_data[user_id]['personalized_description']}"
    
    confirmation_text = f"""✅ *ORDER CONFIRMED!* ✅

📋 *Summary:*
• Service: {service_name}
• Telegram: @{telegram_username}
• Observations: {observations}

📞 *Next Steps:*
1. Our team will contact within 24h
2. Payment instructions will be sent
3. Delivery after confirmation

💰 *Payment: USDT TRC20 only*
⚡ *Fast delivery guaranteed*

🛡️ *RICK SHOP - PREMIUM QUALITY!*"""
    
    keyboard = [
        [InlineKeyboardButton("✅ Confirm Order", callback_data="confirm_order")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
    ]
    
    if language == 'portugues':
        confirmation_text = f"""✅ *PEDIDO CONFIRMADO!* ✅

📋 *Resumo:*
• Serviço: {service_name}
• Telegram: @{telegram_username}
• Observações: {observations}

📞 *Próximos Passos:*
1. Nossa equipe entrará em contato em 24h
2. Instruções de pagamento serão enviadas
3. Entrega após confirmação

💰 *Pagamento: Apenas USDT TRC20*
⚡ *Entrega rápida garantida*

🛡️ *RICK SHOP - QUALIDADE PREMIUM!*"""
        
        keyboard = [
            [InlineKeyboardButton("✅ Confirmar Pedido", callback_data="confirm_order")],
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
        await query.edit_message_text(f"❌ Data lost. Use /start on {BOT_USERNAME}")
        return ConversationHandler.END
    
    language = user_info.get('language', 'portugues')
    
    # Preparar dados
    order_data = {
        'user_id': query.from_user.id,
        'username': query.from_user.username,
        'full_name': query.from_user.full_name,
        'service': user_info['service_name'],
        'telegram_username': user_info.get('telegram_username', ''),
        'observations': user_info.get('observations', ''),
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'personalized_desc': user_info.get('personalized_description', ''),
        'language': language
    }
    
    # Mensagem para o grupo
    group_message = f"""📋 *NOVO PEDIDO - RICK SHOP* 📋

👤 *CLIENTE:*
• ID: {order_data['user_id']}
• Nome: {order_data['full_name']}
• Username: @{order_data['username'] or 'N/A'}
• Telegram: {order_data['telegram_username']}

🛒 *SERVIÇO:*
{order_data['service']}

📝 *OBSERVAÇÕES:*
{order_data['observations']}

🌐 *IDIOMA:*
{language.upper()}

⏰ *DATA/HORA:*
{order_data['timestamp']}

{'✍️ *DESCRIÇÃO PERSONALIZADA:*' if order_data['personalized_desc'] else ''}
{order_data['personalized_desc'] if order_data['personalized_desc'] else ''}

💰 *PAGAMENTO:*
• Normal: 100% antecipado
• Personalizado: 60% + 40%
• Moeda: USDT TRC20

🚨 *CONTATAR: @{order_data['telegram_username']} EM 24H!*"""
    
    try:
        # Enviar para grupo
        await context.bot.send_message(
            chat_id=ORDER_GROUP_ID,
            text=group_message,
            parse_mode='Markdown'
        )
        
        logger.info(f"✅ Pedido enviado para grupo {ORDER_GROUP_ID}")
        
        # Mensagem final para usuário
        if language == 'portugues':
            final_message = f"""✅ *PEDIDO REGISTRADO COM SUCESSO!*

📬 Enviado para nossa equipe no grupo privado.
📞 Entraremos em contato via {order_data['telegram_username']} em até 24h.

💰 *INSTRUÇÕES DE PAGAMENTO:*
• Token: USDT (TRC20)
• Rede: TRON (TRC20)
• Valor: Informado pelo atendente
• Prazo: Pagamento antecipado

⚠️ *ATENÇÃO:*
• Não aceitamos outros métodos
• Confirme sempre o endereço da carteira
• Aguarde confirmação antes de enviar

💎 *RICK SHOP - QUALIDADE E CONFIABILIDADE!*

🛡️ *Para novo pedido, acesse: {BOT_USERNAME}*"""
        else:
            final_message = f"""✅ *ORDER SUCCESSFULLY REGISTERED!*

📬 Sent to our team in private group.
📞 We'll contact via {order_data['telegram_username']} within 24h.

💰 *PAYMENT INSTRUCTIONS:*
• Token: USDT (TRC20)
• Network: TRON (TRC20)
• Amount: Provided by support
• Deadline: Upfront payment

⚠️ *ATTENTION:*
• We don't accept other methods
• Always confirm wallet address
• Wait for confirmation before sending

💎 *RICK SHOP - QUALITY AND RELIABILITY!*

🛡️ *For new order, visit: {BOT_USERNAME}*"""
        
        await query.edit_message_text(
            text=final_message,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"❌ Erro ao enviar para grupo: {e}")
        error_msg = f"✅ Order received!\n\nTechnical error: {str(e)[:100]}...\n\nOur team will be notified."
        if language == 'portugues':
            error_msg = f"✅ Pedido recebido!\n\nErro técnico: {str(e)[:100]}...\n\nNossa equipe será notificada."
        
        await query.edit_message_text(
            text=error_msg,
            parse_mode='Markdown'
        )
    
    # Limpar dados
    if user_id in user_data:
        del user_data[user_id]
    
    return ConversationHandler.END

async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    user_id = str(query.from_user.id)
    language = user_data[user_id]['language']
    
    service_names = SERVICES
    keyboard = []
    for i in range(1, 10, 2):
        row = []
        for j in range(i, min(i+2, 10)):
            name_key = 'name_en' if language == 'english' else 'name_pt'
            row.append(InlineKeyboardButton(
                service_names[j][name_key], 
                callback_data=f"service_{j}"
            ))
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton(
        "❌ Cancel" if language == 'english' else "❌ Cancelar", 
        callback_data="cancel"
    )])
    
    await query.edit_message_text(
        text=TEXTS[language]['main_menu'],
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    return States.MAIN_MENU

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        user_id = str(query.from_user.id)
    else:
        user_id = str(update.message.from_user.id)
    
    if user_id in user_data:
        del user_data[user_id]
    
    message = f"❌ Operation cancelled. Use /start on {BOT_USERNAME} to restart."
    if update.callback_query:
        await query.edit_message_text(message)
    else:
        await update.message.reply_text(message)
    
    return ConversationHandler.END

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Erro no bot: {context.error}")

# ========== COMANDOS ADICIONAIS ==========
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /help"""
    help_text = f"""🤖 *COMANDOS DISPONÍVEIS {BOT_USERNAME}:*
    
/start - Iniciar o bot
/help - Ver esta mensagem de ajuda
/services - Lista de serviços
/contact - Falar com suporte

🏪 *RICK SHOP - QUALIDADE PREMIUM!*
💳 Pagamentos em USDT TRC20 apenas"""
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def services_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /services"""
    services_text = f"""🛒 *SERVIÇOS {BOT_USERNAME}:*

• 📋 Listas Telefônicas Brasileiras
• 📞 Números para SMS/Redes Sociais
• 📱 Contas de Instagram
• 👍 Curtidas e Visualizações TikTok
• 🎨 Montagem de Perfil Profissional
• 🔍 Painel de Dados Brasileiros
• 🌍 Listas Internacionais
• 💡 Ideias para Empresa
• 🛠️ Serviços Personalizados

💰 *Pagamento:* USDT TRC20 apenas
⚡ *Entrega:* Rápida e Segura
⏰ *Suporte:* 24/7"""
    
    await update.message.reply_text(services_text, parse_mode='Markdown')

async def contact_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /contact"""
    contact_text = f"""📞 *CONTATO E SUPORTE {BOT_USERNAME}:*

• Bot: {BOT_USERNAME}
• ⏰ Horário: 24/7
• ⚡ Resposta: Até 24h
• 💰 Pagamento: Apenas USDT TRC20

💬 *Para pedidos:* Use /start no bot
🔧 *Problemas técnicos:* Verifique conexão

🏪 *RICK SHOP - SEU PARCEIRO EM MATERIAIS PREMIUM!*"""
    
    await update.message.reply_text(contact_text, parse_mode='Markdown')

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
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True
    )
    
    application.add_handler(conv_handler)
    
    # Adicionar comandos extras
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("services", services_command))
    application.add_handler(CommandHandler("contact", contact_command))
    
    application.add_error_handler(error_handler)
    
    logger.info(f"✅ Bot {BOT_USERNAME} iniciado com sucesso!")
    logger.info("🟢 Aguardando mensagens...")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
