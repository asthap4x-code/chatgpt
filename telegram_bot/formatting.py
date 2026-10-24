from zoneinfo import ZoneInfo
from datetime import datetime

def local_time(iso,tz):return datetime.fromisoformat(iso).astimezone(ZoneInfo(tz)).strftime('%Y-%m-%d %H:%M:%S %Z')
def signal_text(s,cfg):
 score=max(0,min(100,int(s['confidence'])));filled=round(score/10)
 return (f"🤖 STM PRO BOT\n━━━━━━━━━━━━━━━━━━━━━\n💱 Pair: {s['pair']}\n⏱️ Trade at: {local_time(s['entry_at'],cfg.timezone)}\n🔮 Direction: {s['direction']}\n💰 Payout: {s['payout']:.0f}%\n━━━━━━━━━━━━━━━━━━━━━\n🎯 SIGNAL CONFLUENCE SCORE: {score}%\n{'█'*filled}{'░'*(10-filled)}\n━━━━━━━━━━━━━━━━━━━━━\n⏳ Expiry: 1 minute\n⚠️ Risk is possible; no accuracy or profit is guaranteed.\nStrategy: {s['strategy']}\nReason: {s.get('reason','')}")
def result_text(s,stats,cfg):
 op='UNAVAILABLE' if s.get('open_price') is None else str(s['open_price']);cp='UNAVAILABLE' if s.get('close_price') is None else str(s['close_price'])
 return (f"📊 STM PRO BOT RESULT\n━━━━━━━━━━━━━━━━━━━━━\n💱 Pair: {s['pair']}\n⏱️ Entry time: {local_time(s['entry_at'],cfg.timezone)}\n🔮 Direction: {s['direction']}\n📈 Opening price: {op}\n📉 Closing price: {cp}\n🏁 Result: {s.get('result') or 'PENDING'}\n━━━━━━━━━━━━━━━━━━━━━\n🔥 Wins: {stats['wins']} | Losses: {stats['losses']}\n💎 Pair record: {stats['wins']}-{stats['losses']}\n📊 Verified accuracy: {stats['accuracy']}%\n📩 Feedback: {cfg.feedback_contact}")
