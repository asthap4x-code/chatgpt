import asyncio,logging,os
from telegram.ext import ApplicationBuilder
import config
settings = config.from_env()
from logging_config import configure_logging
from database import Database
from data_provider import MockProvider,PyQuotexAdapter
from signal_engine import SignalEngine
from result_engine import ResultEngine
from market_scanner import MarketScanner
from scheduler import Scheduler
from telegram_bot.handlers import register

async def post_init(app):
 cfg=app.bot_data['cfg'];provider=app.bot_data['provider']
 await provider.connect()
 if cfg.provider_mode=='mock':logging.getLogger(__name__).warning('MOCK MODE: all prices/payouts are synthetic; do not present as live performance.')
 if cfg.database_path:os.makedirs(os.path.dirname(cfg.database_path) or '.',exist_ok=True)
 await app.bot_data['scheduler'].start()
async def post_shutdown(app):
 scheduler=app.bot_data.get('scheduler')
 if scheduler:await scheduler.stop()
 provider=app.bot_data.get('provider')
 if provider:await provider.close()
def main():
 configure_logging();log=logging.getLogger(__name__)
 try:cfg=config.from_env()
 except Exception as e:raise SystemExit(f'Configuration error: {e}')
 db=Database(cfg.database_path);provider=MockProvider() if cfg.provider_mode=='mock' else PyQuotexAdapter(cfg.quotex_email,cfg.quotex_password)
 engine=SignalEngine(cfg,db,provider);results=ResultEngine(db,provider,cfg);scanner=MarketScanner(provider,engine,cfg)
 async def on_signal(s):
  from telegram_bot.formatting import signal_text
  log.info('Persisted eligible signal id=%s pair=%s strategy=%s direction=%s',s['id'],s['pair'],s['strategy'],s['direction'])
  if cfg.signal_channel_id:
   try:
    await app.bot.send_message(chat_id=cfg.signal_channel_id,text=signal_text(s,cfg))
   except Exception:
    log.exception('Could not publish signal to configured channel; signal remains persisted')
 scheduler=Scheduler(scanner,results,db,cfg,on_signal)
 app=ApplicationBuilder().token(cfg.bot_token).post_init(post_init).post_shutdown(post_shutdown).build()
 app.bot_data.update(cfg=cfg,db=db,provider=provider,engine=engine,results=results,scanner=scanner,scheduler=scheduler)
 register(app)
 log.info('Starting STM PRO BOT; provider_mode=%s; enabled_strategies=%s',cfg.provider_mode,','.join(sorted(cfg.enabled_strategies)))
 app.run_polling(allowed_updates=['message','callback_query'])
if __name__=='__main__':main()
