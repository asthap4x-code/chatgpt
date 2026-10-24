STRINGS={
'en':{'welcome':'🤖 STM PRO BOT\nSignals and results are informational, not financial advice. Risk is possible; no accuracy or profit is guaranteed.','join':'Join Channel','verify':'Verify / Joined','get_signal':'Get Signal','risk':'⚠️ Risk notice: fixed-time trading is high risk. Use only money you can afford to lose. No martingale or recovery is guaranteed.'},
'bn':{'welcome':'🤖 STM PRO BOT\nসিগন্যাল তথ্যভিত্তিক; আর্থিক পরামর্শ নয়। ঝুঁকি আছে—লাভ বা নির্ভুলতার নিশ্চয়তা নেই।','join':'চ্যানেলে যোগ দিন','verify':'যাচাই করুন / যোগ দিয়েছি','get_signal':'সিগন্যাল নিন','risk':'⚠️ ঝুঁকি: স্বল্প-মেয়াদি ট্রেডিংয়ে ক্ষতি হতে পারে। হারালে সমস্যা হবে এমন অর্থ ব্যবহার করবেন না।'} }
def tr(lang,key):return STRINGS.get(lang,STRINGS['en']).get(key,STRINGS['en'].get(key,key))
