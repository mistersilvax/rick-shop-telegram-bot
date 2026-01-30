async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Confirma pedido - PRIMEIRO MOSTRA A MENSAGEM DE 'PEDIDO ENVIADO', DEPOIS ENVIA PARA O GRUPO."""
    query = update.callback_query
    await query.answer()
    
    user_id = str(query.from_user.id)
    user_info = user_data.get(user_id, {})
    
    if not user_info:
        await query.edit_message_text("❌ Error. Use /start again.")
        return ConversationHandler.END
    
    language = user_info.get('language', 'english')
    texts = TEXTS[language]
    
    # ========== PRIMEIRO: MOSTRAR MENSAGEM "PEDIDO ENVIADO" ==========
    # Mensagem EXATAMENTE como na imagem
    if language == 'english':
        waiting_message = """✅ *ORDER SENT!*

🔄 **Processing...** Please wait while we confirm your order.
📞 Our support team will contact you shortly via your Telegram @."""
    elif language == 'portugues':
        waiting_message = """✅ *PEDIDO ENVIADO!*

🔄 **Processando...** Aguarde enquanto confirmamos seu pedido.
📞 Nossa equipe de suporte entrará em contato em breve via seu Telegram @."""
    else:  # chinese
        waiting_message = """✅ *订单已发送!*

🔄 **处理中...** 请稍候，我们正在确认您的订单。
📞 我们的支持团队将通过您的Telegram @与您联系。"""
    
    # Editar a mensagem atual com a mensagem de "aguarde"
    await query.edit_message_text(
        waiting_message,
        parse_mode='Markdown'
    )
    
    # ========== SEGUNDO: ENVIAR PARA O GRUPO ==========
    try:
        service = user_info.get('service', 'N/A')
        observations = user_info.get('observations', '')
        
        # Se o cliente usou outro idioma, mostramos a tradução também
        if language != 'portugues':
            lang_note = f" (Idioma original: {language})"
        else:
            lang_note = ""
        
        # Processar observações
        if observations:
            obs_text = f"{observations}{lang_note}"
        else:
            obs_text = f"Nenhuma{lang_note}"
        
        # MENSAGEM PARA O GRUPO - SEMPRE EM PORTUGUÊS
        group_message = f"""📋 *NOVO PEDIDO - RICK SHOP*

👤 *Cliente:*
• Telegram: {user_info.get('telegram_username', 'N/A')}
• ID: {user_id}
• Serviço: {service}
• Observações: {obs_text}
• Data: {datetime.now().strftime("%d/%m/%Y %H:%M")}

🚨 *ENTRAR EM CONTATO EM 24H!*"""
        
        await context.bot.send_message(
            chat_id=ORDER_GROUP_ID,
            text=group_message,
            parse_mode='Markdown'
        )
        
        logger.info(f"✅ Pedido enviado para grupo {ORDER_GROUP_ID}")
        
    except Exception as e:
        logger.error(f"❌ Erro ao enviar para grupo: {e}")
        # Mesmo se falhar ao enviar para o grupo, continuamos o fluxo
    
    # ========== TERCEIRO: MENSAGEM FINAL PARA O CLIENTE ==========
    # (APÓS processar o envio para o grupo)
    final_message = texts['order_sent'].format(
        telegram_username=user_info.get('telegram_username', 'you' if language == 'english' else 'você' if language == 'portugues' else '您'),
        bot_username=BOT_USERNAME
    )
    
    # Esperar um pouco para simular processamento
    import asyncio
    await asyncio.sleep(1)  # Pequena pausa
    
    # Agora mostrar a mensagem final com instruções de pagamento
    await query.edit_message_text(
        final_message,
        parse_mode='Markdown'
    )
    
    # ========== QUARTO: ENVIAR MENSAGEM ADICIONAL ==========
    # Se quiser, pode enviar uma mensagem separada também
    await context.bot.send_message(
        chat_id=user_id,
        text=f"📞 *Lembrete:* Nossa equipe entrará em contato via {user_info.get('telegram_username', 'seu Telegram')} em até 24 horas.\n\nPara um novo pedido: /start",
        parse_mode='Markdown'
    )
    
    # Limpar dados
    if user_id in user_data:
        del user_data[user_id]
    
    return ConversationHandler.END
