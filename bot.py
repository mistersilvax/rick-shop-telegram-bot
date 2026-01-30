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

# ========== ESTADOS ==========
CHOOSING_LANGUAGE, MAIN_MENU, CHOOSING_SERVICE, TELEGRAM_USERNAME, OBSERVATIONS, CONFIRMATION = range(6)

# ========== DADOS ==========
user_data = {}

# ========== TEXTO MULTILÍNGUA ==========
TEXTS = {
    'english': {
        'welcome': f"🌐 *WELCOME TO {BOT_USERNAME}*\n\nChoose your language:",
        'choose_language': "🌐 *SELECT LANGUAGE*",
        'main_menu': """🏪 *RICK SHOP - PREMIUM QUALITY* 🏪

Choose a service:

💰 *Payment:* USDT TRC20 only
⚡ *Delivery:* Fast
🛡️ *Quality:* Guaranteed""",
        'service_selected': "✅ *SERVICE SELECTED*",
        'telegram_prompt': "📲 *ENTER YOUR TELEGRAM @:*\n\nExample: @yourname\n\n*This will be our communication channel.*",
        'observations_prompt': "📌 *ADDITIONAL OBSERVATIONS:*\n\nAny extra information? (optional)\n\nEx: Urgent deadline, specific format, etc.",
        'order_summary': """✅ *ORDER READY TO SEND!*

*Summary:*
• Service: {service}
• Telegram: {username}
• Observations: {observations}

💰 *Payment:* USDT TRC20 only
⚡ *Delivery:* Fast after payment
🛡️ *Quality:* Premium guaranteed""",
        'order_confirmed': """✅ *ORDER SENT SUCCESSFULLY!*

📬 Your order has been sent to our team.
📞 We will contact you via {telegram_username} within 24 hours.

💰 *PAYMENT INSTRUCTIONS:*
• Token: USDT (TRC20)
• Network: TRON network
• Amount: Will be informed by our team

⚠️ *Only USDT TRC20 accepted!*

🛡️ *RICK SHOP - PREMIUM QUALITY*

For a new order: {bot_username}""",
        'order_received': """✅ *ORDER RECEIVED!*

📬 Registered in our system.
📞 Our team has been notified.

💰 Payment: USDT TRC20 only
⚡ Delivery: Fast

For follow-up: {bot_username}""",
        'cancelled': f"❌ Cancelled. Use /start on {BOT_USERNAME}",
        'invalid_username': "❌ Invalid @. Must start with @. Ex: @yourname",
        'services_list': """🛒 *RICK SHOP SERVICES:*

• 📋 Phone Lists
• 📞 SMS Numbers
• 📱 Instagram Accounts
• 👍 TikTok Likes
• 🎨 Professional Profile Setup
• 🔍 Data Panel
• 🌍 International Lists
• 💡 Business Ideas
• 🛠️ Custom Services

💰 Payment: USDT TRC20 only""",
        'help': f"🤖 *{BOT_USERNAME}*\n\n/start - Make an order\n/help - Help\n/services - View services\n\n🏪 Rick Shop - Premium Quality",
        'custom_service': "📝 *DESCRIBE YOUR CUSTOM SERVICE:*\n\nWhat do you need? Detail:\n• Service type\n• Quantity/volume\n• Deadline\n• Budget\n\n💰 *Conditions:* 60% upfront, 40% upon completion",
        'order_sent': """✅ *ORDER SENT SUCCESSFULLY!*

📬 Your order has been sent to our team.
📞 We will contact you via {telegram_username} within 24 hours.

💰 *PAYMENT:*
• Token: USDT (TRC20)
• Network: TRON
• Amount: Informed by our staff

⚠️ *Only USDT TRC20 accepted!*

🛡️ *RICK SHOP - PREMIUM QUALITY*

For a new order: {bot_username}"""
    },
    'portugues': {
        'welcome': f"🌐 *BEM-VINDO AO {BOT_USERNAME}*\n\nEscolha seu idioma:",
        'choose_language': "🌐 *SELECIONE O IDIOMA*",
        'main_menu': """🏪 *RICK SHOP - QUALIDADE PREMIUM* 🏪

Escolha um serviço:

💰 *Pagamento:* Apenas USDT TRC20
⚡ *Entrega:* Rápida
🛡️ *Qualidade:* Garantida""",
        'service_selected': "✅ *SERVIÇO SELECIONADO*",
        'telegram_prompt': "📲 *INFORME SEU @ DO TELEGRAM:*\n\nExemplo: @seunome\n\n*Este será nosso canal de comunicação.*",
        'observations_prompt': "📌 *OBSERVAÇÕES ADICIONAIS:*\n\nAlguma informação extra? (opcional)\n\nEx: Prazo urgente, formato específico, etc.",
        'order_summary': """✅ *PEDIDO PRONTO PARA ENVIAR!*

*Resumo:*
• Serviço: {service}
• Telegram: {username}
• Observações: {observations}

💰 *Pagamento:* Apenas USDT TRC20
⚡ *Entrega:* Rápida após pagamento
🛡️ *Qualidade:* Premium garantida""",
        'order_confirmed': """✅ *PEDIDO ENVIADO COM SUCESSO!*

📬 Seu pedido foi enviado para nossa equipe.
📞 Entraremos em contato via {telegram_username} em até 24h.

💰 *PAGAMENTO:*
• Token: USDT (TRC20)
• Rede: TRON
• Valor: Informado pelo atendente

⚠️ *Apenas USDT TRC20 aceito!*

🛡️ *RICK SHOP - QUALIDADE PREMIUM*

Para novo pedido: {bot_username}""",
        'order_received': """✅ *PEDIDO RECEBIDO!*

📬 Registrado em nosso sistema.
📞 Nossa equipe foi notificada.

💰 Pagamento: Apenas USDT TRC20
⚡ Entrega: Rápida

Para acompanhamento: {bot_username}""",
        'cancelled': f"❌ Cancelado. Use /start no {BOT_USERNAME}",
        'invalid_username': "❌ @ inválido. Deve começar com @. Ex: @seunome",
        'services_list': """🛒 *SERVIÇOS RICK SHOP:*

• 📋 Listas Telefônicas
• 📞 Números SMS
• 📱 Contas Instagram
• 👍 Curtidas TikTok
• 🎨 Perfil Profissional
• 🔍 Painel de Dados
• 🌍 Listas Internacionais
• 💡 Ideias para Empresa
• 🛠️ Serviços Personalizados

💰 Pagamento: Apenas USDT TRC20""",
        'help': f"🤖 *{BOT_USERNAME}*\n\n/start - Fazer pedido\n/help - Ajuda\n/services - Ver serviços\n\n🏪 Rick Shop - Qualidade Premium",
        'custom_service': "📝 *DESCREVA SEU SERVIÇO PERSONALIZADO:*\n\nO que você precisa? Detalhe:\n• Tipo de serviço\n• Quantidade/volume\n• Prazo\n• Orçamento\n\n💰 *Condições:* 60% antecipado, 40% conclusão",
        'order_sent': """✅ *PEDIDO ENVIADO COM SUCESSO!*

📬 Seu pedido foi enviado para nossa equipe.
📞 Entraremos em contato via {telegram_username} em até 24h.

💰 *PAGAMENTO:*
• Token: USDT (TRC20)
• Rede: TRON
• Valor: Informado pelo atendente

⚠️ *Apenas USDT TRC20 aceito!*

🛡️ *RICK SHOP - QUALIDADE PREMIUM*

Para novo pedido: {bot_username}"""
    },
    'chinese': {
        'welcome': f"🌐 *欢迎来到 {BOT_USERNAME}*\n\n选择您的语言:",
        'choose_language': "🌐 *选择语言*",
        'main_menu': """🏪 *RICK SHOP - 优质品质* 🏪

选择服务:

💰 *付款:* 仅限 USDT TRC20
⚡ *交付:* 快速
🛡️ *质量:* 保证""",
        'service_selected': "✅ *服务已选择*",
        'telegram_prompt': "📲 *输入您的 TELEGRAM @:*\n\n例子: @您的名字\n\n*这将是我们的沟通渠道。*",
        'observations_prompt': "📌 *附加说明:*\n\n任何额外信息? (可选)\n\n例如: 紧急期限, 特定格式等",
        'order_summary': """✅ *订单准备发送!*

*摘要:*
• 服务: {service}
• Telegram: {username}
• 说明: {observations}

💰 *付款:* 仅限 USDT TRC20
⚡ *交付:* 付款后快速
🛡️ *质量:* 优质保证""",
        'order_confirmed': """✅ *订单发送成功!*

📬 您的订单已发送给我们的团队。
📞 我们将在24小时内通过 {telegram_username} 联系您。

💰 *付款:*
• 代币: USDT (TRC20)
• 网络: TRON
• 金额: 由客服告知

⚠️ *仅接受 USDT TRC20!*

🛡️ *RICK SHOP - 优质品质*

新订单: {bot_username}""",
        'order_received': """✅ *订单已收到!*

📬 已注册到我们的系统。
📞 我们的团队已收到通知。

💰 付款: 仅限 USDT TRC20
⚡ 交付: 快速

跟进: {bot_username}""",
        'cancelled': f"❌ 已取消。使用 /start 在 {BOT_USERNAME}",
        'invalid_username': "❌ 无效的 @。必须以 @ 开头。例如: @您的名字",
        'services_list': """🛒 *RICK SHOP 服务:*

• 📋 电话列表
• 📞 短信号码
• 📱 Instagram 账户
• 👍 TikTok 点赞
• 🎨 专业个人资料设置
• 🔍 数据面板
• 🌍 国际列表
• 💡 商业想法
• 🛠️ 定制服务

💰 付款: 仅限 USDT TRC20""",
        'help': f"🤖 *{BOT_USERNAME}*\n\n/start - 下订单\n/help - 帮助\n/services - 查看服务\n\n🏪 Rick Shop - 优质品质",
        'custom_service': "📝 *描述您的定制服务:*\n\n您需要什么? 详细说明:\n• 服务类型\n• 数量/容量\n• 截止日期\n• 预算\n\n💰 *条件:* 60% 预付款, 40% 完成时付款",
        'order_sent': """✅ *订单发送成功!*

📬 您的订单已发送给我们的团队。
📞 我们将在24小时内通过 {telegram_username} 联系您。

💰 *付款:*
• 代币: USDT (TRC20)
• 网络: TRON
• 金额: 由客服告知

⚠️ *仅接受 USDT TRC20!*

🛡️ *RICK SHOP - 优质品质*

新订单: {bot_username}"""
    }
}

# ========== SERVIÇOS ==========
SERVICES = {
    'english': {
        1: "📋 Brazilian Phone Lists",
        2: "📞 Numbers for SMS/Social Media", 
        3: "📱 Instagram Accounts",
        4: "👍 TikTok Likes and Views",
        5: "🎨 Professional Profile Setup",
        6: "🔍 Brazilian Data Panel",
        7: "🌍 International Information Lists",
        8: "💡 Complete Business Ideas",
        9: "🛠️ Custom Service"
    },
    'portugues': {
        1: "📋 Listas Telefônicas Brasileiras",
        2: "📞 Números para SMS/Redes Sociais",
        3: "📱 Contas de Instagram",
        4: "👍 Curtidas e Visualizações TikTok",
        5: "🎨 Montagem de Perfil Profissional",
        6: "🔍 Painel de Dados Brasileiros",
        7: "🌍 Listas de Informações Internacionais",
        8: "💡 Ideias Completas para Empresa",
        9: "🛠️ Serviço Personalizado"
    },
    'chinese': {
        1: "📋 巴西电话列表",
        2: "📞 短信/社交媒体号码",
        3: "📱 Instagram 账户",
        4: "👍 TikTok 点赞和观看",
        5: "🎨 专业个人资料设置",
        6: "🔍 巴西数据面板",
        7: "🌍 国际信息列表",
        8: "💡 完整商业想法",
        9: "🛠️ 定制服务"
    }
}

# ========== PREÇOS COMPLETOS ==========
PRICES = {
    'english': {
        1: """💰 *Price:* Starting from $200
⚡ *Delivery:* 24 hours
📊 *Database:* 100K+ Brazilian numbers
🔄 *Update:* Monthly refreshed
🎯 *Target:* Specific states/cities available""",
        2: """💰 *Price:* $15-30 per number
⚡ *Activation:* Immediate
📱 *Type:* SMS/WhatsApp/Telegram verification
🔒 *Guarantee:* Working numbers
🔄 *Replacement:* 48h if not working""",
        3: """💰 *Price:* $50 - $2,500
⚡ *Delivery:* 1-2 hours
👥 *Type:* Old accounts, business, verified
📈 *Followers:* 1K - 100K options
🔒 *Security:* With email recovery""",
        4: """💰 *Price:* $10 - $50
🚀 *Results:* 24-48 hours
👍 *Likes:* 1K - 100K packages
👁️ *Views:* 10K - 1M packages
📈 *Real:* High retention rate""",
        5: """💰 *Price:* $300 - $800
⏱️ *Deadline:* 3-5 days
🎨 *Includes:* Logo, banner, bio optimization
📱 *Platforms:* Instagram, LinkedIn, Twitter
📊 *Analytics:* Monthly report""",
        6: """💰 *Subscription:* $1,500/month
📊 *Data:* Millions of Brazilian records
🔍 *Filters:* Age, location, income
📈 *Real-time:* Updated daily
💼 *Business:* Companies database""",
        7: """💰 *Price:* $200 - $800
🌎 *Countries:* +50 countries
📋 *Types:* Phone, email, business
⚡ *Delivery:* 48-72 hours
🎯 *Specific:* Per country/region""",
        8: """💰 *Price:* $500 - $1,500
📅 *Deadline:* 5-10 days
📋 *Includes:* Business plan, marketing strategy
💼 *Industries:* Various sectors
📈 *Feasibility:* Market analysis""",
        9: """💰 *Payment:* 60% upfront + 40% upon completion
💬 *Describe your need*
⚡ *Quote:* Within 24 hours
🛠️ *Development:* Custom solutions
🔒 *Confidentiality:* 100% guaranteed"""
    },
    'portugues': {
        1: """💰 *Preço:* A partir de $200
⚡ *Entrega:* 24 horas
📊 *Database:* 100K+ números brasileiros
🔄 *Atualização:* Mensalmente renovada
🎯 *Segmentação:* Estados/cidades específicas disponíveis""",
        2: """💰 *Preço:* $15-30 por número
⚡ *Ativação:* Imediata
📱 *Tipo:* Verificação SMS/WhatsApp/Telegram
🔒 *Garantia:* Números funcionando
🔄 *Substituição:* 48h se não funcionar""",
        3: """💰 *Preço:* $50 - $2.500
⚡ *Entrega:* 1-2 horas
👥 *Tipo:* Contas antigas, business, verificadas
📈 *Seguidores:* Opções de 1K - 100K
🔒 *Segurança:* Com email de recuperação""",
        4: """💰 *Preço:* $10 - $50
🚀 *Resultados:* 24-48 horas
👍 *Curtidas:* Pacotes de 1K - 100K
👁️ *Visualizações:* Pacotes de 10K - 1M
📈 *Reais:* Alta taxa de retenção""",
        5: """💰 *Preço:* $300 - $800
⏱️ *Prazo:* 3-5 dias
🎨 *Inclui:* Logo, banner, otimização de bio
📱 *Plataformas:* Instagram, LinkedIn, Twitter
📊 *Analytics:* Relatório mensal""",
        6: """💰 *Assinatura:* $1.500/mês
📊 *Dados:* Milhões de registros brasileiros
🔍 *Filtros:* Idade, localização, renda
📈 *Tempo real:* Atualizado diariamente
💼 *Empresas:* Database de companhias""",
        7: """💰 *Preço:* $200 - $800
🌎 *Países:* +50 países
📋 *Tipos:* Telefone, email, negócios
⚡ *Entrega:* 48-72 horas
🎯 *Específico:* Por país/região""",
        8: """💰 *Preço:* $500 - $1.500
📅 *Prazo:* 5-10 dias
📋 *Inclui:* Plano de negócios, estratégia de marketing
💼 *Indústrias:* Vários setores
📈 *Viabilidade:* Análise de mercado""",
        9: """💰 *Pagamento:* 60% antecipado + 40% conclusão
💬 *Descreva sua necessidade*
⚡ *Orçamento:* Em até 24 horas
🛠️ *Desenvolvimento:* Soluções personalizadas
🔒 *Confidencialidade:* 100% garantida"""
    },
    'chinese': {
        1: """💰 *价格:* 从 $200 起
⚡ *交付:* 24 小时
📊 *数据库:* 100K+ 巴西号码
🔄 *更新:* 每月刷新
🎯 *目标:* 可用特定州/城市""",
        2: """💰 *价格:* $15-30/号码
⚡ *激活:* 立即
📱 *类型:* SMS/WhatsApp/Telegram 验证
🔒 *保证:* 工作号码
🔄 *更换:* 48小时内如果不工作""",
        3: """💰 *价格:* $50 - $2,500
⚡ *交付:* 1-2 小时
👥 *类型:* 旧账户, 商业, 已验证
📈 *粉丝:* 1K - 100K 选项
🔒 *安全:* 带邮箱恢复""",
        4: """💰 *价格:* $10 - $50
🚀 *结果:* 24-48 小时
👍 *点赞:* 1K - 100K 套餐
👁️ *观看:* 10K - 1M 套餐
📈 *真实:* 高保留率""",
        5: """💰 *价格:* $300 - $800
⏱️ *期限:* 3-5 天
🎨 *包括:* 标志, 横幅, 简介优化
📱 *平台:* Instagram, LinkedIn, Twitter
📊 *分析:* 月度报告""",
        6: """💰 *订阅:* $1,500/月
📊 *数据:* 数百万巴西记录
🔍 *过滤器:* 年龄, 位置, 收入
📈 *实时:* 每日更新
💼 *商业:* 公司数据库""",
        7: """💰 *价格:* $200 - $800
🌎 *国家:* +50 国家
📋 *类型:* 电话, 电子邮件, 商业
⚡ *交付:* 48-72 小时
🎯 *特定:* 按国家/地区""",
        8: """💰 *价格:* $500 - $1,500
📅 *期限:* 5-10 天
📋 *包括:* 商业计划, 营销策略
💼 *行业:* 各种领域
📈 *可行性:* 市场分析""",
        9: """💰 *付款:* 60% 预付款 + 40% 完成时付款
💬 *描述您的需求*
⚡ *报价:* 24小时内
🛠️ *开发:* 定制解决方案
🔒 *保密性:* 100% 保证"""
    }
}

# ========== FUNÇÕES PRINCIPAIS ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Inicia o bot."""
    user_id = str(update.effective_user.id)
    user_data[user_id] = {'language': 'english'}  # Idioma padrão em inglês
    
    keyboard = [
        [InlineKeyboardButton("🇺🇸 English", callback_data="english")],
        [InlineKeyboardButton("🇵🇹 Português", callback_data="portugues")],
        [InlineKeyboardButton("🇨🇳 中文", callback_data="chinese")]
    ]
    
    await update.message.reply_text(
        f"🌐 *WELCOME TO {BOT_USERNAME}*\n\nChoose your language:",
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
    
    texts = TEXTS[language]
    
    # Menu principal com serviços
    services = SERVICES[language]
    
    keyboard = [
        [
            InlineKeyboardButton(services[1], callback_data="service_1"),
            InlineKeyboardButton(services[2], callback_data="service_2")
        ],
        [
            InlineKeyboardButton(services[3], callback_data="service_3"),
            InlineKeyboardButton(services[4], callback_data="service_4")
        ],
        [
            InlineKeyboardButton(services[5], callback_data="service_5"),
            InlineKeyboardButton(services[6], callback_data="service_6")
        ],
        [
            InlineKeyboardButton(services[7], callback_data="service_7"),
            InlineKeyboardButton(services[8], callback_data="service_8")
        ],
        [
            InlineKeyboardButton(services[9], callback_data="service_9")
        ],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
    ]
    
    await query.edit_message_text(
        texts['main_menu'],
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
    language = user_data[user_id]['language']
    
    user_data[user_id]['service'] = SERVICES[language][service_num]
    user_data[user_id]['service_num'] = service_num
    
    service_text = SERVICES[language][service_num]
    price_text = PRICES[language][service_num]
    
    texts = TEXTS[language]
    
    keyboard = [[
        InlineKeyboardButton("✅ Select", callback_data="select_service"),
        InlineKeyboardButton("🔙 Back", callback_data="back")
    ]]
    
    await query.edit_message_text(
        f"*{service_text}*\n\n{price_text}",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    return CHOOSING_SERVICE

async def select_service(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Seleciona serviço."""
    query = update.callback_query
    await query.answer()
    
    user_id = str(query.from_user.id)
    language = user_data[user_id]['language']
    texts = TEXTS[language]
    
    if user_data[user_id]['service_num'] == 9:
        await query.edit_message_text(
            texts['custom_service'],
            parse_mode='Markdown'
        )
        return TELEGRAM_USERNAME
    
    await query.edit_message_text(
        texts['telegram_prompt'],
        parse_mode='Markdown'
    )
    return TELEGRAM_USERNAME

async def get_telegram_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Pega username do Telegram."""
    user_id = str(update.message.from_user.id)
    username = update.message.text.strip()
    language = user_data[user_id]['language']
    texts = TEXTS[language]
    
    if not username.startswith('@'):
        await update.message.reply_text(texts['invalid_username'])
        return TELEGRAM_USERNAME
    
    user_data[user_id]['telegram_username'] = username
    
    await update.message.reply_text(
        texts['observations_prompt'],
        parse_mode='Markdown'
    )
    return OBSERVATIONS

async def get_observations(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Pega observações."""
    user_id = str(update.message.from_user.id)
    observations = update.message.text
    user_data[user_id]['observations'] = observations
    
    language = user_data[user_id]['language']
    texts = TEXTS[language]
    service = user_data[user_id]['service']
    username = user_data[user_id]['telegram_username']
    
    # Definir texto para observações vazias
    if language == 'english':
        observations_text = observations or 'None'
    elif language == 'portugues':
        observations_text = observations or 'Nenhuma'
    else:  # chinese
        observations_text = observations or '无'
    
    keyboard = [[
        InlineKeyboardButton("✅ CONFIRM ORDER", callback_data="confirm_order")
    ]]
    
    await update.message.reply_text(
        texts['order_summary'].format(
            service=service,
            username=username,
            observations=observations_text
        ),
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
        await query.edit_message_text("❌ Error. Use /start again.")
        return ConversationHandler.END
    
    language = user_info.get('language', 'english')
    texts = TEXTS[language]
    
    # Enviar para grupo
    try:
        # Definir texto para observações vazias no grupo
        if language == 'english':
            obs_text = user_info.get('observations', 'None')
        elif language == 'portugues':
            obs_text = user_info.get('observations', 'Nenhuma')
        else:  # chinese
            obs_text = user_info.get('observations', '无')
        
        group_message = f"""📋 *NEW ORDER - RICK SHOP*

👤 *Customer:*
• Telegram: {user_info.get('telegram_username', 'N/A')}
• Service: {user_info.get('service', 'N/A')}
• Observations: {obs_text}
• Language: {language.upper()}
• Date: {datetime.now().strftime("%d/%m/%Y %H:%M")}

🚨 *CONTACT WITHIN 24H!*"""
        
        await context.bot.send_message(
            chat_id=ORDER_GROUP_ID,
            text=group_message,
            parse_mode='Markdown'
        )
        
        logger.info(f"✅ Order sent to group {ORDER_GROUP_ID}")
        
        # Mensagem final para cliente - CORRIGIDA AQUI
        await query.edit_message_text(
            texts['order_sent'].format(
                telegram_username=user_info.get('telegram_username', ''),
                bot_username=BOT_USERNAME
            ),
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"❌ Error sending to group: {e}")
        # Se falhar ao enviar para o grupo, ainda mostrar mensagem ao cliente
        await query.edit_message_text(
            texts['order_sent'].format(
                telegram_username=user_info.get('telegram_username', ''),
                bot_username=BOT_USERNAME
            ),
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
    language = user_data[user_id]['language']
    texts = TEXTS[language]
    services = SERVICES[language]
    
    keyboard = [
        [
            InlineKeyboardButton(services[1], callback_data="service_1"),
            InlineKeyboardButton(services[2], callback_data="service_2")
        ],
        [
            InlineKeyboardButton(services[3], callback_data="service_3"),
            InlineKeyboardButton(services[4], callback_data="service_4")
        ],
        [
            InlineKeyboardButton(services[5], callback_data="service_5"),
            InlineKeyboardButton(services[6], callback_data="service_6")
        ],
        [
            InlineKeyboardButton(services[7], callback_data="service_7"),
            InlineKeyboardButton(services[8], callback_data="service_8")
        ],
        [
            InlineKeyboardButton(services[9], callback_data="service_9")
        ],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
    ]
    
    await query.edit_message_text(
        texts['main_menu'],
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
        if user_id in user_data:
            language = user_data[user_id].get('language', 'english')
            texts = TEXTS[language]
            await query.edit_message_text(texts['cancelled'])
        else:
            await query.edit_message_text(f"❌ Cancelled. Use /start on {BOT_USERNAME}")
    else:
        user_id = str(update.message.from_user.id)
        if user_id in user_data:
            language = user_data[user_id].get('language', 'english')
            texts = TEXTS[language]
            await update.message.reply_text(texts['cancelled'])
        else:
            await update.message.reply_text(f"❌ Cancelled. Use /start on {BOT_USERNAME}")
    
    if user_id in user_data:
        del user_data[user_id]
    
    return ConversationHandler.END

# ========== COMANDOS ADICIONAIS ==========
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    language = user_data.get(user_id, {}).get('language', 'english')
    texts = TEXTS[language]
    await update.message.reply_text(texts['help'], parse_mode='Markdown')

async def services_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    language = user_data.get(user_id, {}).get('language', 'english')
    texts = TEXTS[language]
    await update.message.reply_text(texts['services_list'], parse_mode='Markdown')

# ========== MAIN COM WEBHOOK CORRIGIDO ==========
def main():
    """Função principal - usa WEBHOOK com pacote correto."""
    app = Application.builder().token(TOKEN).build()
    
    # Configurar conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING_LANGUAGE: [CallbackQueryHandler(choose_language, pattern='^(english|portugues|chinese)$')],
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
        fallbacks=[CommandHandler('cancel', cancel)],
        per_message=False
    )
    
    app.add_handler(conv_handler)
    
    # Adicionar handlers para comandos extras
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("services", services_cmd))
    
    logger.info(f"✅ Bot {BOT_USERNAME} STARTING...")
    logger.info(f"✅ Token: {TOKEN[:10]}...")
    
    # ========== CONFIGURAR WEBHOOK ==========
    PORT = int(os.environ.get('PORT', 8080))
    WEBHOOK_URL = "https://rick-shop-telegram-bot-production.up.railway.app"
    
    logger.info(f"🌐 Configuring webhook for: {WEBHOOK_URL}")
    logger.info(f"🔧 Port: {PORT}")
    
    # URL completa do webhook
    webhook_url = f"{WEBHOOK_URL}/{TOKEN}"
    logger.info(f"🔗 Webhook URL: {webhook_url}")
    
    # Configurar webhook
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=
