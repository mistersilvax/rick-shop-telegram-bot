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

# TOKEN DO SEU BOT - JÁ INSERIDO!
TOKEN = os.getenv('TOKEN', '8252613179:AAFbdap-56zMBw4glJk_MBj7bnEWk3F1Ido')
ORDER_GROUP_ID = os.getenv('ORDER_GROUP_ID', '-1003565140066')

logger.info(f"✅ Bot {BOT_USERNAME} iniciando...")
logger.info(f"✅ Token configurado")
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
        
        'need_personalized': """📝 *SERVIÇO PERSONALIZADO*

Descreva detalhadamente o que precisa:

• Tipo de serviço específico
• Quantidade/volume necessário
• Prazo desejado
• Orçamento disponível

💰 *Condições:*
• 60% pagamento antecipado
• 40% na conclusão do serviço
• Apenas USDT TRC20""",
        
        'ask_telegram': "📲 *Informe seu @ do Telegram (ex: @seunome):*",
        
        'ask_observations': """📌 *OBSERVAÇÕES ADICIONAIS*

Alguma informação extra? (opcional)
• Especificações técnicas
• Prazo urgente
• Formato desejado
• Outras necessidades""",
        
        'confirmation': f"""✅ *PEDIDO CONFIRMADO!*

📞 Nossa equipe entrará em contato via {BOT_USERNAME} em até 24h.

💰 *INSTRUÇÕES DE PAGAMENTO:*
• Token: USDT (TRC20)
• Rede: TRON
• Confirme sempre o endereço da carteira""",
        
        'error': f"❌ Erro. Use /start no {BOT_USERNAME} para recomeçar.",
        'cancel': "❌ Operação cancelada.",
        'invalid_username': "❌ @ inválido. Deve começar com @ (ex: @seunome)"
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
        
        'need_personalized': """📝 *PERSONALIZED SERVICE*

Describe in detail what you need:

• Specific service type
• Quantity/volume needed
• Desired deadline
• Available budget

💰 *Conditions:*
• 60% payment upfront
• 40% upon service completion
• Only USDT TRC20""",
        
        'ask_telegram': "📲 *Provide your Telegram @ (ex: @yourname):*",
        
        'ask_observations': """📌 *ADDITIONAL OBSERVATIONS*

Any extra information? (optional)
• Technical specifications
• Urgent deadline
• Desired format
• Other requirements""",
        
        'confirmation': f"""✅ *ORDER CONFIRMED!*

📞 Our team will contact via {BOT_USERNAME} within 24h.

💰 *PAYMENT INSTRUCTIONS:*
• Token: USDT (TRC20)
• Network: TRON
• Always confirm wallet address""",
        
        'error': f"❌ Error. Use /start on {BOT_USERNAME} to restart.",
        'cancel': "❌ Operation cancelled.",
        'invalid_username': "❌ Invalid @. Must start with @ (ex: @username)"
    }
}

# ========== SERVIÇOS ==========
SERVICES = {
    1: {'key': 'phone_lists', 'name_pt': '📋 Listas Telefônicas', 'name_en': '📋 Phone Lists'},
    2: {'key': 'sms_numbers', 'name_pt': '📞 Números SMS', 'name_en': '📞 SMS Numbers'},
    3: {'key': 'instagram_accounts', 'name_pt': '📱 Contas Instagram', 'name_en': '📱 Instagram Accounts'},
    4: {'key': 'tiktok_likes', 'name_pt': '👍 Curtidas TikTok', 'name_en': '👍 TikTok Likes'},
    5: {'key': 'profile_setup', 'name_pt': '🎨 Perfil Profissional', 'name_en': '🎨 Profile Setup'},
    6: {'key': 'data_panel', 'name_pt': '🔍 Painel de Dados', 'name_en': '🔍 Data Panel'},
    7: {'key': 'international_lists', 'name_pt': '🌍 Listas Internacionais', 'name_en': '🌍 International Lists'},
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
    
    cancel_text = "❌ Cancel" if language == 'english' else "❌ Cancelar"
    keyboard.append([InlineKeyboardButton(cancel_text, callback_data="cancel")])
    
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
    
    confirmation_text = TEXTS[language]['confirmation']
    
    confirm_text = "✅ Confirm Order" if language == 'english' else "✅ Confirmar Pedido"
    cancel_text = "❌ Cancel" if language == 'english' else "❌ Cancelar"
    
    keyboard = [
        [InlineKeyboardButton(confirm_text, callback_data="confirm_order")],
        [InlineKeyboardButton(cancel_text, callback_data="cancel")]
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
        await query.edit_message_text(f"❌ Dados perdidos. Use /start no {BOT_USERNAME}")
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

💰 *CONDIÇÕES DE PAGAMENTO:*
• Serviços normais: 100% antecipado
• Serviços personalizados: 60% antecipado + 40% conclusão
• Moeda: Apenas USDT TRC20

🚨 *AÇÃO REQUERIDA:*
Entrar em contato com @{order_data['telegram_username']} em até 24 horas!

⚡ *Via bot: {BOT_USERNAME}*"""
    
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

📬 Seu pedido foi enviado para nossa equipe administrativa.
📞 Nossa equipe entrará em contato através do {order_data['telegram_username']} em até 24 horas.

💰 *INSTRUÇÕES DE PAGAMENTO:*
• Token: USDT (TRC20)
• Rede: TRON (TRC20)
• Valor: Será informado pelo atendente
• Prazo: Pagamento antecipado

⚠️ *ATENÇÃO IMPORTANTE:*
• Não aceitamos outros métodos de pagamento
• Confirme sempre o endereço da carteira
• Aguarde confirmação antes de enviar qualquer valor
• Todos os pagamentos são em crypto USDT TRC20

💎 *RICK SHOP - QUALIDADE E CONFIABILIDADE GARANTIDA!*

🛡️ *Para fazer um novo pedido, acesse: {BOT_USERNAME}*

⚡ *Tempo de resposta: menos de 24 horas*"""
        else:
            final_message = f"""✅ *ORDER SUCCESSFULLY REGISTERED!*

📬 Your order has been sent to our administrative team.
📞 Our team will contact you through {order_data['telegram_username']} within 24 hours.

💰 *PAYMENT INSTRUCTIONS:*
• Token: USDT (TRC20)
• Network: TRON (TRC20)
• Amount: Will be informed by support
• Deadline: Upfront payment

⚠️ *IMPORTANT ATTENTION:*
• We don't accept other payment methods
• Always confirm the wallet address
• Wait for confirmation before sending any amount
• All payments are in crypto USDT TRC20

💎 *RICK SHOP - GUARANTEED QUALITY AND RELIABILITY!*

🛡️ *To make a new order, visit: {BOT_USERNAME}*

⚡ *Response time: less than 24 hours*"""
        
        await query.edit_message_text(
            text=final_message,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"❌ Erro ao enviar para grupo: {e}")
        
        if language == 'portugues':
            error_msg = f"""✅ Pedido recebido com sucesso!

📬 Seu pedido foi registrado em nosso sistema.
📞 Nossa equipe será notificada e entrará em contato em breve.

⚠️ *Erro técnico:* O sistema de notificação automática apresentou uma falha, mas seu pedido está seguro.

💰 *Pagamento:* Apenas USDT TRC20
⚡ *Entrega:* Rápida e segura

💎 *Rick Shop - Sua confiança é nossa prioridade!*

Para acompanhamento: {BOT_USERNAME}"""
        else:
            error_msg = f"""✅ Order successfully received!

📬 Your order has been registered in our system.
📞 Our team will be notified and will contact you soon.

⚠️ *Technical error:* The automatic notification system had a failure, but your order is safe.

💰 *Payment:* Only USDT TRC20
⚡ *Delivery:* Fast and secure

💎 *Rick Shop - Your trust is our priority!*

For follow-up: {BOT_USERNAME}"""
        
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
    
    cancel_text = "❌ Cancel" if language == 'english' else "❌ Cancelar"
    keyboard.append([InlineKeyboardButton(cancel_text, callback_data="cancel")])
    
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
    
    message = f"❌ Operação cancelada. Use /start no {BOT_USERNAME} para recomeçar."
    
    if update.callback_query:
        await query.edit_message_text(message)
    else:
        await update.message.reply_text(message)
    
    return ConversationHandler.END

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Erro no bot {BOT_USERNAME}: {context.error}")

# ========== COMANDOS ADICIONAIS ==========
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /help"""
    help_text = f"""🤖 *COMANDOS DISPONÍVEIS {BOT_USERNAME}:*
    
/start - Iniciar o bot e fazer pedido
/help - Ver esta mensagem de ajuda
/services - Ver lista completa de serviços
/contact - Informações de contato

🏪 *RICK SHOP - ESPECIALISTA EM MATERIAIS PREMIUM*
💳 Pagamentos em USDT TRC20 apenas
⚡ Entrega rápida e segura
⏰ Suporte 24/7"""
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def services_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /services"""
    services_text = f"""🛒 *SERVIÇOS DISPONÍVEIS {BOT_USERNAME}:*

• 📋 *Listas Telefônicas Brasileiras* - Dados completos
• 📞 *Números para SMS/Redes Sociais* - WhatsApp, Telegram, Tinder
• 📱 *Contas de Instagram* - Brasileiras e internacionais
• 👍 *Curtidas e Visualizações TikTok* - Aumento de engajamento
• 🎨 *Montagem de Perfil Profissional* - Instagram corporativo
• 🔍 *Painel de Dados Brasileiros* - Assinatura mensal
• 🌍 *Listas Internacionais* - Dados de diversos países
• 💡 *Ideias para Empresa* - Projetos completos
• 🛠️ *Serviços Personalizados* - Soluções sob medida

💰 *CONDIÇÕES COMERCIAIS:*
• Pagamento: Apenas USDT TRC20
• Entrega: Rápida conforme serviço
• Qualidade: Premium garantida
• Suporte: 24 horas por dia

⚡ *Para fazer pedido:* Use /start no {BOT_USERNAME}"""
    
    await update.message.reply_text(services_text, parse_mode='Markdown')

async def contact_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /contact"""
    contact_text = f"""📞 *INFORMAÇÕES DE CONTATO {BOT_USERNAME}:*

🤖 *Bot Oficial:* {BOT_USERNAME}
⏰ *Horário de Atendimento:* 24 horas por dia, 7 dias por semana
⚡ *Tempo de Resposta:* Até 24 horas para pedidos
💰 *Forma de Pagamento:* Exclusivamente USDT TRC20

📋 *PARA FAZER PEDIDOS:*
1. Acesse {BOT_USERNAME}
2. Use o comando /start
3. Siga o fluxo de pedido
4. Aguarde contato da equipe

🔧 *PROBLEMAS TÉCNICOS:*
• Verifique sua conexão com a internet
• Certifique-se de estar usando a versão mais recente do Telegram
• Se o problema persistir, tente reiniciar o Telegram

🏪 *RICK SHOP - SEU PARCEIRO EM MATERIAIS PREMIUM PARA TRABALHO BRASILEIRO E INTERNACIONAL!*

💎 *Qualidade garantida | Entrega rápida | Suporte especializado*"""
    
    await update.message.reply_text(contact_text, parse_mode='Markdown')

# ========== MAIN ==========
def main() -> None:
    """Executa o bot."""
    try:
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
        logger.info(f"✅ Token: {TOKEN[:15]}...")
        logger.info(f"✅ Grupo de pedidos: {ORDER_GROUP_ID}")
        logger.info("🟢 Aguardando mensagens...")
        
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"❌ Erro fatal no bot {BOT_USERNAME}: {e}")
        raise

if __name__ == '__main__':
    main()
