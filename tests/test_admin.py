from telegram_bot.admin import is_admin
class C:admin_ids=frozenset({123})
def test_numeric_admin_check():assert is_admin(123,C());assert not is_admin(124,C());assert not is_admin(None,C())
