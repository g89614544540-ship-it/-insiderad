from flask import Flask, request, jsonify, render_template
import requests
import uuid
import base64
import telebot
from telebot import types as tg_types

app = Flask(__name__)

SUPABASE_URL = "https://kjschhxyiobwlrpeoqwp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtqc2NoaHh5aW9id2xycGVvcXdwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM5MTc2MjIsImV4cCI6MjA4OTQ5MzYyMn0.sgBW5rOkv8hKvoWYUCKi4eAKBENLUwNsvnhPGne8irk"
CRYPTOBOT_TOKEN = "553650:AAcouqrFimQutC95FSQtp0vNP5lElj5iPDI"
CRYPTOBOT_URL = "https://pay.crypt.bot/api"
BOT_TOKEN = "8734788678:AAHNXaFd7VZsQtITaXblhJTyBRs6bVRkLfE"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

tgbot = telebot.TeleBot(BOT_TOKEN)

PRICES_TON = {'standard': 6.49, 'pro': 8.72}
PRICES_GRAM_EQ = {'standard': 5.90, 'pro': 8.30}
PRICES_USDT_EQ = {'standard': 5.77, 'pro': 8.51}


def sb_get(table, params=""):
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/{table}?{params}", headers=HEADERS)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return []


def sb_insert(table, data):
    try:
        r = requests.post(f"{SUPABASE_URL}/rest/v1/{table}", json=data, headers=HEADERS)
        if r.status_code in [200, 201]:
            return r.json()
    except:
        pass
    return []


def sb_update(table, params, data):
    try:
        r = requests.patch(f"{SUPABASE_URL}/rest/v1/{table}?{params}", json=data, headers=HEADERS)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return []


def extract_channel(link):
    c = link.strip().rstrip('/')
    if '/t.me/' in c:
        c = c.split('/t.me/')[-1]
    elif 't.me/' in c:
        c = c.split('t.me/')[-1]
    if '?' in c:
        c = c.split('?')[0]
    if '/' in c:
        c = c.split('/')[0]
    if not c.startswith('@'):
        c = '@' + c
    return c


def check_bot_admin(link):
    try:
        ch = extract_channel(link)
        bot_id = tgbot.get_me().id
        r = requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember",
            params={'chat_id': ch, 'user_id': bot_id}
        )
        resp = r.json()
        if resp.get('ok') and resp.get('result'):
            st = resp['result'].get('status', '')
            return {'is_admin': st in ['administrator', 'creator'], 'status': st, 'channel': ch}
        return {'is_admin': False, 'error': resp.get('description', 'Unknown')}
    except Exception as e:
        return {'is_admin': False, 'error': str(e)}


def notify_ad_finished(ad):
    try:
        cid = ad.get('creator_telegram_id')
        if not cid:
            return
        tgbot.send_message(cid,
            f"\U0001f6d1 <b>Ad finished!</b>\n\n"
            f"\U0001f4cc {ad.get('title','')}\n"
            f"\U0001f441 Views: {ad.get('views_ordered',0)}\n"
            f"\U0001f4ce Tariff: {(ad.get('tariff','standard')).upper()}\n\n"
            f"\u2705 All views done!\n"
            f"\U0001f916 You can now remove bot from channel admins.",
            parse_mode='HTML')
    except:
        pass


def get_crypto_rates():
    rates = {'GRAM': None, 'USDT': None}
    try:
        r = requests.get(f"{CRYPTOBOT_URL}/getExchangeRates",
                         headers={'Crypto-Pay-API-Token': CRYPTOBOT_TOKEN})
        resp = r.json()
        if resp.get('ok') and resp.get('result'):
            ton_usd = gram_usd = usdt_usd = None
            for item in resp['result']:
                s, t = item.get('source'), item.get('target')
                if s == 'TON' and t == 'USD' and item.get('is_valid'):
                    ton_usd = float(item['rate'])
                if s == 'GRAM' and t == 'USD':
                    gram_usd = float(item['rate'])
                if s == 'USDT' and t == 'USD' and item.get('is_valid'):
                    usdt_usd = float(item['rate'])
            if gram_usd and ton_usd:
                rates['GRAM'] = gram_usd / ton_usd
            if usdt_usd and ton_usd:
                rates['USDT'] = ton_usd / usdt_usd
    except:
        pass
    return rates


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/ads')
def api_ads():
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/ads?is_active=eq.true&select=*", headers=HEADERS)
        if r.status_code == 200:
            return jsonify(r.json())
    except:
        pass
    return jsonify([])


@app.route('/api/ads/create', methods=['POST'])
def api_ads_create():
    try:
        d = request.json
        ad = {
            'title': d.get('title', ''),
            'description': d.get('description', ''),
            'link': d.get('link', ''),
            'media_url': d.get('media_url', ''),
            'media_type': d.get('media_type', 'text'),
            'views_ordered': int(d.get('views_ordered', 100)),
            'views_done': 0,
            'price_paid': float(d.get('price_paid', 0)),
            'tariff': d.get('tariff', 'standard'),
            'is_active': False,
            'creator_telegram_id': d.get('creator_telegram_id')
        }
        if ad['tariff'] == 'pro':
            chk = check_bot_admin(ad['link'])
            if not chk.get('is_admin'):
                return jsonify({'error': 'Bot not admin', 'need_admin': True, 'details': chk.get('error', '')}), 400
        res = sb_insert('ads', ad)
        if res and len(res) > 0:
            return jsonify(res[0])
        return jsonify({'error': 'Failed'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/check_bot_admin', methods=['POST'])
def api_check_bot_admin():
    try:
        d = request.json
        link = d.get('channel_link', '')
        if not link:
            return jsonify({'is_admin': False, 'error': 'No link'}), 400
        return jsonify(check_bot_admin(link))
    except Exception as e:
        return jsonify({'is_admin': False, 'error': str(e)}), 500


@app.route('/api/check_subscription', methods=['POST'])
def api_check_subscription():
    try:
        d = request.json
        tid = d.get('telegram_id')
        link = d.get('channel_link', '')
        if not tid or not link:
            return jsonify({'subscribed': False, 'error': 'Missing'}), 400
        ch = extract_channel(link)
        r = requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember",
            params={'chat_id': ch, 'user_id': tid}
        )
        resp = r.json()
        if resp.get('ok') and resp.get('result'):
            st = resp['result'].get('status', '')
            return jsonify({'subscribed': st in ['member', 'administrator', 'creator'], 'status': st})
        return jsonify({'subscribed': False, 'error': resp.get('description', '')})
    except Exception as e:
        return jsonify({'subscribed': False, 'error': str(e)}), 500


@app.route('/api/user', methods=['POST'])
def api_user():
    try:
        d = request.json
        tid = d.get('telegram_id')
        uname = d.get('username', '')
        rcode = d.get('referrer_code')
        if not tid:
            return jsonify({'error': 'No telegram_id'}), 400
        ex = sb_get('users', f'telegram_id=eq.{tid}')
        if ex and len(ex) > 0:
            u = ex[0]
            if uname and uname != u.get('username', ''):
                sb_update('users', f"id=eq.{u['id']}", {'username': uname})
            refs = sb_get('users', f"referred_by=eq.{u['id']}&select=id")
            return jsonify({
                'id': u['id'], 'telegram_id': u['telegram_id'],
                'username': u.get('username', ''),
                'balance': float(u.get('balance', 0) or 0),
                'total_watched': u.get('total_watched', 0) or 0,
                'ref_code': u.get('ref_code', ''),
                'ref_count': len(refs) if refs else 0,
                'ref_earned': float(u.get('ref_earned', 0) or 0)
            })
        rc = uuid.uuid4().hex[:8]
        rb = None
        if rcode:
            rr = sb_get('users', f'ref_code=eq.{rcode}&select=id')
            if rr and len(rr) > 0:
                rb = rr[0]['id']
        nu = {'telegram_id': tid, 'username': uname, 'balance': 0,
              'total_watched': 0, 'ref_code': rc, 'referred_by': rb, 'ref_earned': 0}
        res = sb_insert('users', nu)
        if res and len(res) > 0:
            return jsonify({
                'id': res[0]['id'], 'telegram_id': tid, 'username': uname,
                'balance': 0, 'total_watched': 0, 'ref_code': rc,
                'ref_count': 0, 'ref_earned': 0
            })
        return jsonify({'error': 'Failed'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/watch', methods=['POST'])
def api_watch():
    try:
        d = request.json
        uid, aid = d.get('user_id'), d.get('ad_id')
        if not uid or not aid:
            return jsonify({'error': 'Missing'}), 400
        ads = sb_get('ads', f'id=eq.{aid}')
        tariff = 'standard'
        finished = False
        if ads and len(ads) > 0:
            a = ads[0]
            tariff = a.get('tariff', 'standard')
            nv = (a.get('views_done', 0) or 0) + 1
            ud = {'views_done': nv}
            if nv >= (a.get('views_ordered', 0) or 0):
                ud['is_active'] = False
                finished = True
            sb_update('ads', f'id=eq.{aid}', ud)
            if finished:
                a['views_done'] = nv
                notify_ad_finished(a)
        rw = 0.06 if tariff == 'pro' else 0.04
        users = sb_get('users', f'id=eq.{uid}')
        rb = 0
        if users and len(users) > 0:
            u = users[0]
            nb = float(u.get('balance', 0) or 0) + rw
            nw = (u.get('total_watched', 0) or 0) + 1
            sb_update('users', f'id=eq.{uid}', {'balance': nb, 'total_watched': nw})
            rby = u.get('referred_by')
            if rby:
                rb = round(rw * 0.10, 4)
                refs = sb_get('users', f'id=eq.{rby}')
                if refs and len(refs) > 0:
                    nre = float(refs[0].get('ref_earned', 0) or 0) + rb
                    sb_update('users', f'id=eq.{rby}', {'ref_earned': nre})
        return jsonify({'success': True, 'reward': rw, 'ref_bonus': rb})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/claim_ref', methods=['POST'])
def api_claim_ref():
    try:
        uid = request.json.get('user_id')
        if not uid:
            return jsonify({'error': 'Missing'}), 400
        users = sb_get('users', f'id=eq.{uid}')
        if not users:
            return jsonify({'error': 'Not found'}), 404
        u = users[0]
        re = float(u.get('ref_earned', 0) or 0)
        if re < 1.0:
            return jsonify({'error': 'Min 1 TON'}), 400
        nb = round(float(u.get('balance', 0) or 0) + re, 4)
        sb_update('users', f'id=eq.{uid}', {'balance': nb, 'ref_earned': 0})
        return jsonify({'success': True, 'claimed': re, 'new_balance': nb})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload', methods=['POST'])
def api_upload():
    try:
        d = request.json
        fd = d.get('file_data')
        fn = d.get('file_name', 'file')
        ct = d.get('content_type', 'image/jpeg')
        if not fd:
            return jsonify({'error': 'No file'}), 400
        fb = base64.b64decode(fd)
        path = f"ads/{uuid.uuid4().hex}_{fn}"
        requests.post(f"{SUPABASE_URL}/storage/v1/object/media/{path}",
                      data=fb, headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": ct})
        return jsonify({'url': f"{SUPABASE_URL}/storage/v1/object/public/media/{path}"})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/get_prices')
def api_get_prices():
    try:
        tf = request.args.get('tariff', 'standard')
        v = max(100, int(request.args.get('views', 100)))
        m = v / 100.0
        rates = get_crypto_rates()
        result = {
            'ton': {'amount': round(PRICES_TON.get(tf, 6.49) * m, 2), 'currency': 'TON'},
            'gram': None, 'usdt': None
        }
        ge = PRICES_GRAM_EQ.get(tf, 5.90) * m
        ue = PRICES_USDT_EQ.get(tf, 5.77) * m
        if rates['GRAM'] and rates['GRAM'] > 0:
            result['gram'] = {'amount': round(ge / rates['GRAM'], 2), 'currency': 'GRAM', 'ton_equivalent': round(ge, 2)}
        if rates['USDT'] and rates['USDT'] > 0:
            result['usdt'] = {'amount': round(ue * rates['USDT'], 2), 'currency': 'USDT', 'ton_equivalent': round(ue, 2)}
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/create_invoice', methods=['POST'])
def api_create_invoice():
    try:
        d = request.json
        aid, amt, cur = d.get('ad_id'), d.get('amount'), d.get('currency', 'TON')
        if not aid or not amt:
            return jsonify({'error': 'Missing'}), 400
        asset = cur.upper() if cur.upper() in ['TON', 'GRAM', 'USDT'] else 'TON'
        r = requests.post(f"{CRYPTOBOT_URL}/createInvoice",
                          json={'currency_type': 'crypto', 'asset': asset,
                                'amount': str(round(float(amt), 2)),
                                'description': 'Mytonads ad', 'payload': str(aid)},
                          headers={'Crypto-Pay-API-Token': CRYPTOBOT_TOKEN})
        resp = r.json()
        if resp.get('ok') and resp.get('result'):
            inv = resp['result']
            return jsonify({'invoice_id': inv.get('invoice_id'), 'pay_url': inv.get('pay_url')})
        return jsonify({'error': 'Invoice failed', 'details': resp}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/check_payment')
def api_check_payment():
    try:
        aid = request.args.get('ad_id')
        if not aid:
            return jsonify({'paid': False})
        r = requests.get(f"{CRYPTOBOT_URL}/getInvoices",
                         headers={'Crypto-Pay-API-Token': CRYPTOBOT_TOKEN})
        resp = r.json()
        if resp.get('ok') and resp.get('result'):
            for inv in resp['result'].get('items', []):
                if inv.get('payload') == str(aid) and inv.get('status') == 'paid':
                    sb_update('ads', f'id=eq.{aid}', {'is_active': True})
                    return jsonify({'paid': True})
        return jsonify({'paid': False})
    except:
        return jsonify({'paid': False})


@app.route('/api/withdraw', methods=['POST'])
def api_withdraw():
    try:
        d = request.json
        uid, w = d.get('user_id'), d.get('wallet_address')
        if not uid or not w:
            return jsonify({'error': 'Missing'}), 400
        users = sb_get('users', f'id=eq.{uid}')
        if not users:
            return jsonify({'error': 'Not found'}), 404
        bal = float(users[0].get('balance', 0) or 0)
        if bal < 1.5:
            return jsonify({'error': 'Min 1.5 TON'}), 400
        amt = round(bal, 2)
        bot_bal = {}
        try:
            br = requests.get(f"{CRYPTOBOT_URL}/getBalance",
                              headers={'Crypto-Pay-API-Token': CRYPTOBOT_TOKEN})
            bresp = br.json()
            if bresp.get('ok'):
                for b in bresp['result']:
                    av = float(b.get('available', 0))
                    if av > 0:
                        bot_bal[b['currency_code']] = av
        except:
            pass
        rates = get_crypto_rates()
        wa, wm = None, None
        if rates.get('GRAM') and rates['GRAM'] > 0:
            ga = round(amt / rates['GRAM'], 2)
            if bot_bal.get('GRAM', 0) >= ga:
                wa, wm = 'GRAM', ga
        if not wa and rates.get('USDT') and rates['USDT'] > 0:
            ua = round(amt * rates['USDT'], 2)
            if bot_bal.get('USDT', 0) >= ua:
                wa, wm = 'USDT', ua
        if not wa and bot_bal.get('TON', 0) >= amt:
            wa, wm = 'TON', amt
        if not wa:
            return jsonify({'error': 'Insufficient bot balance'}), 400
        r2 = requests.post(f"{CRYPTOBOT_URL}/createCheck",
                           json={'asset': wa, 'amount': str(wm)},
                           headers={'Crypto-Pay-API-Token': CRYPTOBOT_TOKEN})
        resp2 = r2.json()
        if not (resp2.get('ok') and resp2.get('result')):
            return jsonify({'error': 'Check failed'}), 500
        cu = resp2['result'].get('bot_check_url', '')
        sb_update('users', f'id=eq.{uid}', {'balance': 0})
        return jsonify({'success': True, 'amount': wm, 'currency': wa, 'ton_equivalent': amt, 'check_url': cu})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/my_ads')
def api_my_ads():
    try:
        tid = request.args.get('telegram_id')
        if not tid:
            return jsonify([])
        ads = sb_get('ads', f'creator_telegram_id=eq.{tid}&select=*&order=created_at.desc')
        return jsonify(ads if ads else [])
    except:
        return jsonify([])


@app.route('/api/debug_rates')
def debug_rates():
    try:
        r = requests.get(f"{CRYPTOBOT_URL}/getExchangeRates",
                         headers={'Crypto-Pay-API-Token': CRYPTOBOT_TOKEN})
        return jsonify(r.json())
    except Exception as e:
        return jsonify({'error': str(e)})


@tgbot.message_handler(commands=['start'])
def cmd_start(message):
    args = message.text.split()
    ref = args[1] if len(args) > 1 else ''
    url = 'https://insiderad.vercel.app'
    if ref:
        url += '?ref=' + ref
    mk = tg_types.InlineKeyboardMarkup()
    mk.add(tg_types.InlineKeyboardButton(
        text='\U0001f48e Open Mytonads',
        web_app=tg_types.WebAppInfo(url=url)))
    tgbot.send_message(message.chat.id,
        '\U0001f48e <b>Mytonads</b>\n\n'
        '\U0001f441 Watch ads \u2014 earn TON\n'
        '\U0001f4e2 Create ads\n\n'
        'Tap button \U0001f447',
        parse_mode='HTML', reply_markup=mk)


@tgbot.message_handler(commands=['endads'])
def cmd_endads(message):
    tid = message.from_user.id
    ads = sb_get('ads', f'creator_telegram_id=eq.{tid}&is_active=eq.true&select=*')
    if not ads:
        tgbot.send_message(message.chat.id, '\U0001f4ed No active ads', parse_mode='HTML')
        return
    mk = tg_types.InlineKeyboardMarkup()
    for a in ads:
        mk.add(tg_types.InlineKeyboardButton(
            text=f"\U0001f4cc {a.get('title','')[:30]}",
            callback_data=f"adinfo_{a.get('id')}"))
    tgbot.send_message(message.chat.id,
        '\U0001f4cb <b>Your active ads:</b>', parse_mode='HTML', reply_markup=mk)


@tgbot.callback_query_handler(func=lambda c: c.data.startswith('adinfo_'))
def cb_adinfo(call):
    aid = call.data.replace('adinfo_', '')
    ads = sb_get('ads', f'id=eq.{aid}&select=*')
    if not ads:
        tgbot.answer_callback_query(call.id, 'Not found')
        return
    a = ads[0]
    vd = a.get('views_done', 0) or 0
    vo = a.get('views_ordered', 0) or 0
    pr = int(vd / vo * 100) if vo > 0 else 0
    fl = int(10 * pr / 100)
    bar = '\u2588' * fl + '\u2591' * (10 - fl)
    tgbot.edit_message_text(
        f"\U0001f4ca <b>Ad stats</b>\n\n"
        f"\U0001f4cc {a.get('title','')}\n"
        f"\U0001f4ce {(a.get('tariff','standard')).upper()}\n"
        f"\U0001f441 {vd}/{vo} views\n\n[{bar}] {pr}%",
        call.message.chat.id, call.message.message_id, parse_mode='HTML')
    tgbot.answer_callback_query(call.id)


@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        j = request.get_json()
        if j:
            tgbot.process_new_updates([telebot.types.Update.de_json(j)])
    except:
        pass
    return 'ok'


@app.route('/set_webhook')
def set_webhook():
    try:
        tgbot.remove_webhook()
        u = 'https://insiderad.vercel.app/webhook'
        tgbot.set_webhook(url=u)
        return f'Webhook set to {u}'
    except Exception as e:
        return f'Error: {e}'


if __name__ == '__main__':
    app.run(debug=True)
