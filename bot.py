import logging
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# ========== CONFIGURAÇÃO ==========
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== CONFIGURAÇÕES DO BOT ==========
TOKEN = "8252613179:AAFbdap-56zMBw4glJk_MBj7bnEWk3F1Ido"
ORDER_GROUP_ID = "-1003565140066"
BOT_USERNAME = "@Rick_shoppbot"
WEBHOOK_URL = "https://rick-shop-telegram-bot-production.up.railway.app"  # SEU DOMÍNIO!

# ========== ESTADOS ==========
CHOOSING_LANGUAGE, MAIN_MENU, CHOOSING_SERVICE, TELEGRAM_USERNAME, OBSERVATIONS, CONFIRMATION = range(6)

# ========== DADOS ==========
user_data = {}

# ========== FUNÇÕES PRINCIPAIS ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Inicia o bot."""
    user_id = str(update.effective_user.id)
    user_data[user_id] = {'language': 'portugues'}
    
    keyboard = [[InlineKeyboardButton("🇺🇸 English", callback_data="english")]]
    await update.message.reply_text(
        f"🌐 *BEM-VINDO AO {BOT_USERNAME}*\n\nEscolha idioma:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    return CHOOSING_LANGUAGE

async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Escolhe idioma."""
    query = update.callback_query
    await query.answer()
    
    user_id = str(query.from_user.id)
    language = query.data
    user_data[user_id]['language'] = language
    
    # Menu principal
    services = [
        ["📋 Listas Telefônicas", "📞 Números SMS"],
        ["📱 Contas Instagram", "👍 Curtidas TikTok"],
        ["🎨 Perfil Profissional", "🔍 Painel Dados"],
        ["🌍 Listas Internacionais", "💡 Ideias Empresa"],
        ["🛠️ Serviço Personalizado"]
    ]
    
    keyboard = []
    for row in services:
        keyboard_row = []
        for service in row:
            if "Listas Telefônicas" in service:
                keyboard_row.append(InlineKeyboardButton(service, callback_data="service_1"))
            elif "Números SMS" in service:
                keyboard_row.append(InlineKeyboardButton(service, callback_data="service_2"))
            elif "Contas Instagram" in service:
                keyboard_row.append(InlineKeyboardButton(service, callback_data="service_3"))
            elif "Curtidas TikTok" in service:
                keyboard_row.append(InlineKeyboardButton(service, callback_data="service_4"))
            elif "Perfil Profissional" in service:
                keyboard_row.append(InlineKeyboardButton(service, callback_data="service_5"))
            elif "Painel Dados" in service:
                keyboard_row.append(InlineKeyboardButton(service, callback_data="service_6"))
            elif "Listas Internacionais" in service:
                keyboard_row.append(InlineKeyboardButton(service, callback_data="service_7"))
            elif "Ideias Empresa" in service:
                keyboard_row.append(InlineKeyboardButton(service, callback_data="service_8"))
            else:
                keyboard_row.append(InlineKeyboardButton(service, callback_data="service_9"))
        keyboard.append(keyboard_row)
    
    keyboard.append([InlineKeyboardButton("❌ Cancelar", callback_data="cancel")])
    
    await query.edit_message_text(
        f"""🏪 *RICK SHOP - PREMIUM QUALITY* 🏪

Escolha um serviço:

💰 *Pagamento:* USDT TRC20 apenas
⚡ *Entrega:* Rápida
🛡️ *Qualidade:* Garantida""",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    return MAIN_MENU

async def choose_service(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Escolhe serviço."""
    query = update.callback_query
    await query.answer()
    
    user_id = str(query.from_user.id)
    service_num = int(query.data.replace('service_', ''))
    
    services_map = {
        1: "📋 Listas Telefônicas Brasileiras",
        2: "📞 Números para SMS/Redes Sociais", 
        3: "📱 Contas de Instagram",
        4: "👍 Curtidas e Visualizações TikTok",
        5: "🎨 Montagem de Perfil Profissional",
        6: "🔍 Painel de Dados Brasileiros",
        7: "🌍 Listas de Informações Internacionais",
        8: "💡 Ideias Completas para Empresa",
        9: "🛠️ Serviço Personalizado"
    }
    
    user_data[user_id]['service'] = services_map[service_num]
    user_data[user_id]['service_num'] = service_num
    
    prices = {
        1: "💰 *Preço:* A partir de $200\n⚡ *Entrega:* 24h",
        2: "💰 *Preço:* $15-30/número\n⚡ *Ativação:* Imediata",
        3: "💰 *Preço:* $50-2.500\n⚡ *Entrega:* 1-2 horas",
        4: "💰 *Preço:* $10-50\n🚀 *Resultados:* 24-48h",
        5: "💰 *Preço:* $300-800\n⏱️ *Prazo:* 3-5 dias",
        6: "💰 *Assinatura:* $1.500/mês\n📊 *Dados:* Milhões",
        7: "💰 *Preço:* $200-800\n🌎 *Países:* +50",
        8: "💰 *Preço:* $500-1.500\n📅 *Prazo:* 5-10 dias",
        9: "💰 *Pagamento:* 60% antecipado + 40% conclusão\n💬 *Descreva sua necessidade*"
    }
    
    keyboard = [[
        InlineKeyboardButton("✅ Selecionar", callback_data="select_service"),
        InlineKeyboardButton("🔙 Voltar", callback_data="back")
    ]]
    
    await query.edit_message_text(
        f"{services_map[service_num]}\n\n{prices[service_num]}",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    return CHOOSING_SERVICE

async def select_service(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Seleciona serviço."""
    query = update.callback_query
    await query.answer()
    
    user_id = str(query.from_user.id)
    
    if user_data[user_id]['service_num'] == 9:
        await query.edit_message_text(
            "📝 *DESCREVA SEU SERVIÇO PERSONALIZADO:*\n\nO que você precisa? Detalhe:\n• Tipo de serviço\n• Quantidade/volume\n• Prazo\n• Orçamento\n\n💰 *Condições:* 60% antecipado, 40% conclusão",
            parse_mode='Markdown'
        )
        return TELEGRAM_USERNAME
    
    await query.edit_message_text(
        "📲 *INFORME SEU @ DO TELEGRAM:*\n\nExemplo: @seunome\n\n*Este será nosso canal de comunicação.*",
        parse_mode='Markdown'
    )
    return TELEGRAM_USERNAME

async def get_telegram_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Pega username do Telegram."""
    user_id = str(update.message.from_user.id)
    username = update.message.text.strip()
    
    if not username.startswith('@'):
        await update.message.reply_text("❌ @ inválido. Deve começar com @. Ex: @seunome")
        return TELEGRAM_USERNAME
    
    user_data[user_id]['telegram_username'] = username
    
    await update.message.reply_text(
        "📌 *OBSERVAÇÕES ADICIONAIS:*\n\nAlguma informação extra? (opcional)\n\nEx: Prazo urgente, formato específico, etc.",
        parse_mode='Markdown'
    )
    return OBSERVATIONS

async def get_observations(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Pega observações."""
    user_id = str(update.message.from_user.id)
    observations = update.message.text
    user_data[user_id]['observations'] = observations
    
    service = user_data[user_id]['service']
    username = user_data[user_id]['telegram_username']
    
    keyboard = [[
        InlineKeyboardButton("✅ CONFIRMAR PEDIDO", callback_data="confirm_order")
    ]]
    
    await update.message.reply_text(
        f"""✅ *PEDIDO PRONTO PARA ENVIAR!*

*Resumo:*
• Serviço: {service}
• Telegram: {username}
• Observações: {observations or 'Nenhuma'}

💰 *Pagamento:* USDT TRC20 apenas
⚡ *Entrega:* Rápida após pagamento
🛡️ *Qualidade:* Premium garantida""",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    return CONFIRMATION

async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Confirma pedido."""
    query = update.callback_query
    await query.answer()
    
    user_id = str(query.from_user.id)
    user_info = user_data.get(user_id, {})
    
    if not user_info:
        await query.edit_message_text("❌ Erro. Use /start novamente.")
        return ConversationHandler.END
    
    # Enviar para grupo
    try:
        group_message = f"""📋 *NOVO PEDIDO - RICK SHOP*

👤 *Cliente:*
• Telegram: {user_info.get('telegram_username', 'N/A')}
• Serviço: {user_info.get('service', 'N/A')}
• Observações: {user_info.get('observations', 'Nenhuma')}
• Data: {datetime.now().strftime("%d/%m/%Y %H:%M")}

🚨 *CONTATAR EM 24H!*"""
        
        await context.bot.send_message(
            chat_id=ORDER_GROUP_ID,
            text=group_message,
            parse_mode='Markdown'
        )
        
        logger.info(f"✅ Pedido enviado para grupo {ORDER_GROUP_ID}")
        
        # Mensagem final para cliente
        await query.edit_message_text(
            f"""✅ *PEDIDO CONFIRMADO COM SUCESSO!*

📬 Seu pedido foi enviado para nossa equipe.
📞 Entraremos em contato via {user_info.get('telegram_username')} em até 24h.

💰 *PAGAMENTO:*
• Token: USDT (TRC20)
• Rede: TRON
• Valor: Informado pelo atendente

⚠️ *Apenas USDT TRC20 aceito!*

🛡️ *RICK SHOP - QUALIDADE PREMIUM*

Para novo pedido: {BOT_USERNAME}""",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        await query.edit_message_text(
            f"""✅ *PEDIDO RECEBIDO!*

📬 Registrado em nosso sistema.
📞 Nossa equipe será notificada.

💰 Pagamento: Apenas USDT TRC20
⚡ Entrega: Rápida

Para acompanhamento: {BOT_USERNAME}""",
            parse_mode='Markdown'
        )
    
    # Limpar dados
    if user_id in user_data:
        del user_data[user_id]
    
    return ConversationHandler.END

async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Volta ao menu."""
    query = update.callback_query
    await query.answer()
    
    user_id = str(query.from_user.id)
    
    # Recriar menu
    services = [
        ["📋 Listas Telefônicas", "📞 Números SMS"],
        ["📱 Contas Instagram", "👍 Curtidas TikTok"],
        ["🎨 Perfil Profissional", "🔍 Painel Dados"],
        ["🌍 Listas Internacionais", "💡 Ideias Empresa"],
        ["🛠️ Serviço Personalizado"]
    ]
    
    keyboard = []
    for row in services:
        keyboard_row = []
        for service in row:
            if "Listas Telefônicas" in service:
                keyboard_row.append(InlineKeyboardButton(service, callback_data="service_1"))
            elif "Números SMS" in service:
                keyboard_row.append(InlineKeyboardButton(service, callback_data="service_2"))
            elif "Contas Instagram" in service:
                keyboard_row.append(InlineKeyboardButton(service, callback_data="service_3"))
            elif "Curtidas TikTok" in service:
                keyboard_row.append(InlineKeyboardButton(service, callback_data="service_4"))
            elif "Perfil Profissional" in service:
                keyboard_row.append(InlineKeyboardButton(service, callback_data="service_5"))
            elif "Painel Dados" in service:
                keyboard_row.append(InlineKeyboardButton(service, callback_data="service_6"))
            elif "Listas Internacionais" in service:
                keyboard_row.append(InlineKeyboardButton(service, callback_data="service_7"))
            elif "Ideias Empresa" in service:
                keyboard_row.append(InlineKeyboardButton(service, callback_data="service_8"))
            else:
                keyboard_row.append(InlineKeyboardButton(service, callback_data="service_9"))
        keyboard.append(keyboard_row)
    
    keyboard.append([InlineKeyboardButton("❌ Cancelar", callback_data="cancel")])
    
    await query.edit_message_text(
        f"""🏪 *RICK SHOP - PREMIUM QUALITY* 🏪

Escolha um serviço:

💰 *Pagamento:* USDT TRC20 apenas
⚡ *Entrega:* Rápida
🛡️ *Qualidade:* Garantida""",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    return MAIN_MENU

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancela operação."""
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        user_id = str(query.from_user.id)
        await query.edit_message_text(f"❌ Cancelado. Use /start no {BOT_USERNAME}")
    else:
        user_id = str(update.message.from_user.id)
        await update.message.reply_text(f"❌ Cancelado. Use /start no {BOT_USERNAME}")
    
    if user_id in user_data:
        del user_data[user_id]
    
    return ConversationHandler.END

# ========== MAIN COM WEBHOOK ==========
def main():
    """Função principal - usa WEBHOOK."""
    app = Application.builder().token(TOKEN).build()
    
    # Configurar conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING_LANGUAGE: [CallbackQueryHandler(choose_language, pattern='^(english|portugues)$')],
            MAIN_MENU: [
                CallbackQueryHandler(choose_service, pattern='^service_'),
                CallbackQueryHandler(cancel, pattern='^cancel$')
            ],
            CHOOSING_SERVICE: [
                CallbackQueryHandler(select_service, pattern='^select_service$'),
                CallbackQueryHandler(back_to_menu, pattern='^back$')
            ],
            TELEGRAM_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_telegram_username)],
            OBSERVATIONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_observations)],
            CONFIRMATION: [CallbackQueryHandler(confirm_order, pattern='^confirm_order$')]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    app.add_handler(conv_handler)
    
    # Comandos extras
    async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(f"🤖 *{BOT_USERNAME}*\n\n/start - Fazer pedido\n/help - Ajuda\n/services - Ver serviços\n\n🏪 Rick Shop - Premium Quality")
    
    async def services_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🛒 *SERVIÇOS RICK SHOP:*\n\n• 📋 Listas Telefônicas\n• 📞 Números SMS\n• 📱 Contas Instagram\n• 👍 Curtidas TikTok\n• 🎨 Perfil Profissional\n• 🔍 Painel de Dados\n• 🌍 Listas Internacionais\n• 💡 Ideias para Empresa\n• 🛠️ Serviços Personalizados\n\n💰 Pagamento: USDT TRC20 apenas")
    
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("services", services_cmd))
    
    logger.info(f"✅ Bot {BOT_USERNAME} INICIANDO...")
    logger.info(f"✅ Token: {TOKEN[:10]}...")
    logger.info(f"✅ Domínio: {WEBHOOK_URL}")
    
    # ========== CONFIGURAR WEBHOOK ==========
    PORT = 8080
    
    logger.info(f"🌐 Configurando webhook para: {WEBHOOK_URL}")
    
    # Configurar webhook
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{TOKEN}",
        drop_pending_updates=True
    )

if __name__ == '__main__':
    main()
