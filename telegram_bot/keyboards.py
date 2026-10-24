from telegram import InlineKeyboardButton,InlineKeyboardMarkup
CATEGORIES=['FOREX','CURRENCY','CRYPTO','COMMODITIES']
STRATEGIES=['AI','STM','RANDOM','BLACK4X','OPX4O']
def welcome_kb(config):return InlineKeyboardMarkup([[InlineKeyboardButton('Join Channel',url=config.channel_url)],[InlineKeyboardButton('Verify / Joined',callback_data='verify')]])
def get_kb():return InlineKeyboardMarkup([[InlineKeyboardButton('🎯 Get Signal',callback_data='categories')]])
def categories_kb():return InlineKeyboardMarkup([[InlineKeyboardButton(c,callback_data='cat:'+c) for c in CATEGORIES[:2]],[InlineKeyboardButton(c,callback_data='cat:'+c) for c in CATEGORIES[2:]],[InlineKeyboardButton('SELECT ALL',callback_data='cat:ALL')]])
def pairs_kb(pairs,selected,page=0,page_size=8):
 start=page*page_size; chunk=pairs[start:start+page_size]; rows=[]
 for p in chunk: rows.append([InlineKeyboardButton(('✅ ' if p['pair'] in selected else '')+p['pair'],callback_data='pair:'+p['pair'])])
 nav=[]
 if page>0:nav.append(InlineKeyboardButton('◀ Prev',callback_data=f'page:{page-1}'))
 if start+page_size<len(pairs):nav.append(InlineKeyboardButton('Next ▶',callback_data=f'page:{page+1}'))
 if nav:rows.append(nav)
 rows.append([InlineKeyboardButton('SELECT ALL',callback_data='pairs:ALL'),InlineKeyboardButton('Continue',callback_data='strategies')]);return InlineKeyboardMarkup(rows)
def strategies_kb(selected):
 rows=[[InlineKeyboardButton(('✅ ' if s in selected else '')+s+' STRATEGY',callback_data='strat:'+s)] for s in STRATEGIES]
 rows.append([InlineKeyboardButton('SELECT ALL',callback_data='strat:ALL'),InlineKeyboardButton('Run selected',callback_data='run')]);return InlineKeyboardMarkup(rows)
def uto_kb():return InlineKeyboardMarkup([[InlineKeyboardButton(str(n),callback_data='uto:'+str(n)) for n in (10,20,25,30,40)]])
