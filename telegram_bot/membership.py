from telegram.error import TelegramError
async def is_member(bot,channel_id,user_id):
 if not channel_id:return True
 try:
  m=await bot.get_chat_member(chat_id=channel_id,user_id=user_id)
  return m.status in ('member','administrator','creator') or (m.status=='restricted' and getattr(m,'is_member',False))
 except TelegramError:return False
