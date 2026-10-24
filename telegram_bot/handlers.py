import logging
from telegram import Update
from telegram.ext import ContextTypes,CommandHandler,CallbackQueryHandler
from .keyboards import welcome_kb,get_kb,categories_kb,pairs_kb,strategies_kb,uto_kb
from .membership import is_member
from .admin import is_admin
from .formatting import signal_text
from localization import tr
log=logging.getLogger(__name__)
async def start(update:Update,ctx:ContextTypes.DEFAULT_TYPE):
 c=ctx.application.bot_data['cfg'];db=ctx.application.bot_data['db'];u=update.effective_user;db.save_user(u.id)
 msg=f"{tr(c.language,'welcome')}\nChannel: {c.channel_username or 'not configured'}\nAdmin: @{c.admin_username}\nReferral: {c.referral_url}\n\nMembership verification does not prove referral registration."
 await update.effective_message.reply_text(msg,reply_markup=welcome_kb(c))
async def callback(update:Update,ctx:ContextTypes.DEFAULT_TYPE):
 q=update.callback_query;await q.answer();c=ctx.application.bot_data['cfg'];db=ctx.application.bot_data['db'];provider=ctx.application.bot_data['provider'];u=q.from_user;data=q.data or ''
 if data=='verify':
  ok=await is_member(ctx.bot,c.channel_id,u.id)
  if not ok:await q.edit_message_text('Membership not verified. Join the channel and retry.',reply_markup=welcome_kb(c));return
  db.save_user(u.id,verified=True);await q.edit_message_text(tr(c.language,'risk'),reply_markup=get_kb());return
 if data=='categories':
  if not db.user(u.id)['verified']:await q.edit_message_text('Please verify channel membership first.',reply_markup=welcome_kb(c));return
  await q.edit_message_text('Choose market categories:',reply_markup=categories_kb());return
 if data.startswith('cat:'):
  cats=db.user(u.id)['categories'];v=data[4:];cats=['FOREX','CURRENCY','CRYPTO','COMMODITIES'] if v=='ALL' else (cats+[v] if v not in cats else [x for x in cats if x!=v]);db.save_user(u.id,categories=cats);await q.edit_message_text('Choose categories, then select pairs:',reply_markup=categories_kb());return
 if data.startswith('pair:') or data.startswith('page:') or data=='pairs:ALL':
  user=db.user(u.id);pairs=[p for p in await provider.pairs() if not user['categories'] or p.get('category') in user['categories']];selected=user['pairs'];page=0
  if data.startswith('pair:'):
   v=data[5:];selected=selected+[v] if v not in selected else [x for x in selected if x!=v];db.save_user(u.id,pairs=selected)
  elif data.startswith('page:'):page=max(0,int(data[5:]))
  elif data=='pairs:ALL':selected=[p['pair'] for p in pairs];db.save_user(u.id,pairs=selected)
  await q.edit_message_text('Select pairs:',reply_markup=pairs_kb(pairs,selected,page));return
 if data.startswith('strat:'):
  selected=db.user(u.id)['strategies'];v=data[6:];selected=['AI','STM','RANDOM','BLACK4X','OPX4O'] if v=='ALL' else (selected+[v] if v not in selected else [x for x in selected if x!=v]);db.save_user(u.id,strategies=selected);await q.edit_message_text('Choose strategies:',reply_markup=strategies_kb(selected));return
 if data=='strategies':await q.edit_message_text('Choose strategies:',reply_markup=strategies_kb(db.user(u.id)['strategies']));return
 if data=='run':
  user=db.user(u.id);engine=ctx.application.bot_data['engine'];sent=[]
  for p in await provider.pairs():
   if user['pairs'] and p['pair'] not in user['pairs']:continue
   for st in user['strategies']:
    r=await engine.candidate(p['pair'],p.get('category','FOREX'),st)
    if r:sent.append(r)
    if len(sent)>=5:break
   if len(sent)>=5:break
  if not sent:await q.edit_message_text('No eligible signal. Payout, closed candles, data quality or strategy filters may have rejected all candidates.');return
  await q.edit_message_text('Eligible signals found: '+str(len(sent)))
  for s in sent:await ctx.bot.send_message(chat_id=u.id,text=signal_text(s,c))
  return
 if data.startswith('uto:'):
  if not is_admin(u.id,c):await q.edit_message_text('Unauthorized');return
  n=int(data[4:]);db.log_admin(u.id,'UTO '+str(n));await ctx.application.bot_data['scheduler'].run_n(n);await q.edit_message_text(f'Limited scan started: {n} eligible persisted signals. Skipped candidates do not count; no guarantee that {n} will be found.')
async def admin_guard(update,ctx):
 if not is_admin(update.effective_user.id if update.effective_user else None,ctx.application.bot_data['cfg']):
  if update.effective_message:await update.effective_message.reply_text('Unauthorized.');return False
 return True
async def stmop(update,ctx):
 if not await admin_guard(update,ctx):return
 db=ctx.application.bot_data['db'];db.log_admin(update.effective_user.id,'STMOP');await ctx.application.bot_data['scheduler'].stop();await update.effective_message.reply_text('Stopped new signal generation. Open signals remain persisted and will be retried on next start.')
async def stmon(update,ctx):
 if not await admin_guard(update,ctx):return
 ctx.application.bot_data['db'].log_admin(update.effective_user.id,'STMON');await ctx.application.bot_data['scheduler'].start();await update.effective_message.reply_text('Signal scheduler started.')
async def status(update,ctx):
 db=ctx.application.bot_data['db'];await update.effective_message.reply_text(f"Running: {ctx.application.bot_data['scheduler'].running}\nOpen signals: {len(db.open_signals())}\nStats: {db.get_stats()}")
async def pause(update,ctx):
 if not await admin_guard(update,ctx):return
 await ctx.application.bot_data['scheduler'].stop();ctx.application.bot_data['db'].log_admin(update.effective_user.id,'PAUSE');await update.effective_message.reply_text('Paused.')
async def resume(update,ctx):await stmon(update,ctx)
async def stats(update,ctx):await update.effective_message.reply_text(str(ctx.application.bot_data['db'].get_stats())+'\nAccuracy includes resolved WIN/TIE and MTG WIN outcomes; recovery remains separately tracked.')
async def help_cmd(update,ctx):await update.effective_message.reply_text('/start /help /status /stats. Admin: /STMON /STMOP /STMUTO /pause /resume. Signal-only; no trades are placed.')
async def uto(update,ctx):
 if not await admin_guard(update,ctx):return
 await update.effective_message.reply_text('Select the number of eligible persisted signal attempts:',reply_markup=uto_kb())
def register(app):
 for cmd,fn in [('start',start),('help',help_cmd),('status',status),('stats',stats),('STMON',stmon),('STMOP',stmop),('STMUTO',uto),('pause',pause),('resume',resume)]:app.add_handler(CommandHandler(cmd,fn))
 app.add_handler(CallbackQueryHandler(callback))
