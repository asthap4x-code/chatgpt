import pytest
from telegram_bot.membership import is_member
class Member:status='member'
class Bot:
 async def get_chat_member(self,chat_id,user_id):return Member()
@pytest.mark.asyncio
async def test_member():assert await is_member(Bot(),'@channel',123)
