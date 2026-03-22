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
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/{table}?{params}",
            headers=HEADERS
        )
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return []


def sb_insert(table, data):
    try:
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/{table}",
            json=data, headers=HEADERS
        )
        if r.status_code in [200, 201]:
            return r.json()
    except:
        pass
    return []


def sb_update(table, params, data):
    try:
        r = requests.patch(
            f"{SUPABASE_URL}/rest/v1/{table}?{params}",
            json=data, headers=HEADERS
        )
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return []


def notify_ad_finished(ad):
    try:
        cid = ad.get('creator_telegram_id')
        if not cid:
            return
        t = ad.get('title', 'Без названия')
        v = ad.get('views_ordered', 0)
        tf = ad.get('tariff', 'standard').upper()
        tgbot.send_message(cid,
            f"\U0001f6d1 <b>Реклама завершена!</b>\n\n"
            f"\U0001f4cc Название: <b>{t}</b>\n"
            f"\U0001f441 Просмотров: <b>{v}</b>\n"
            f"\U0001f4ce Тариф: <b>{tf}</b>\n\n"
            f"\u2705 Все просмотры выполнены!",
            parse_mode='HTML')
    except:
        pass


def get_crypto_rates():
    rates = {'GRAM': None, 'USDT': None}
    try:
        r = requests.get(
            f"{CRYPTOBOT_URL}/getExchangeRates",
            headers={'Crypto-Pay-API-Token': CRYPTOBOT_TOKEN}
        )
        resp = r.json()
        if resp.get('ok') and resp.get('result'):
            ton_usd = None
            gram_usd = None
            usdt_usd = None

            for item in resp['result']:
                if item.get('source') == 'TON' and item.get('target') == 'USD':
                    if item.get('is_valid'):
                        ton_usd = float(item['rate'])
                if item.get('source') == 'GRAM' and item.get('target') == 'USD':
                    gram_usd = float(item['rate'])
                if item.get('source') == 'USDT' and item.get('target') == 'USD':
                    if item.get('is_valid'):
                        usdt_usd = float(item['rate'])

            if gram_usd and ton_usd and gram_usd > 0 and ton_usd > 0:
                rates['GRAM'] = gram_usd / ton_usd

            if usdt_usd and ton_usd and usdt_usd > 0 and ton_usd > 0:
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
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/ads?is_active=eq.true&select=*",
            headers=HEADERS
        )
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
        res = sb_insert('ads', ad)
        if res and len(res) > 0:
            return jsonify(res[0])
        return jsonify({'error': 'Failed'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/user', methods=['POST'])
def api_user():
    try:
        d = request.json
        tid = d.get('telegram_id')
        uname = d.get('username', '')
        rcode = d.get('referrer_code', None)
        if not tid:
            return jsonify({'error': 'No telegram_id'}), 400
        ex = sb_get('users', f'telegram_id=eq.{tid}')
        if ex and len(ex) > 0:
            u = ex[0]
            if uname and uname != u.get('username', ''):
                sb_update('users', f"id=eq.{u['id']}", {'username': uname})
            refs = sb_get('users', f"referred_by=eq.{u['id']}&select=id")
            return jsonify({
                'id': u['id'],
                'telegram_id': u['telegram_id'],
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
        nu = {
            'telegram_id': tid, 'username': uname,
            'balance': 0, 'total_watched': 0,
            'ref_code': rc, 'referred_by': rb, 'ref_earned': 0
        }
        res = sb_insert('users', nu)
        if res and len(res) > 0:
            return jsonify({
                'id': res[0]['id'], 'telegram_id': tid,
                'username': uname, 'balance': 0,
                'total_watched': 0, 'ref_code': rc,
                'ref_count': 0, 'ref_earned': 0
            })
        return jsonify({'error': 'Failed'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/watch', methods=['POST'])
def api_watch():
    try:
        d = request.json
        uid = d.get('user_id')
        aid = d.get('ad_id')
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
            sb_update('users', f'id=eq.{uid}', {
                'balance': nb, 'total_watched': nw
            })
            rby = u.get('referred_by')
            if rby:
                rb = round(rw * 0.10, 4)
                refs = sb_get('users', f'id=eq.{rby}')
                if refs and len(refs) > 0:
                    ru = refs[0]
                    nre = float(ru.get('ref_earned', 0) or 0) + rb
                    sb_update('users', f'id=eq.{rby}', {
                        'ref_earned': nre
                    })
        return jsonify({'success': True, 'reward': rw, 'ref_bonus': rb})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/claim_ref', methods=['POST'])
def api_claim_ref():
    try:
        d = request.json
        uid = d.get('user_id')
        if not uid:
            return jsonify({'error': 'Missing'}), 400
        users = sb_get('users', f'id=eq.{uid}')
        if not users:
            return jsonify({'error': 'Not found'}), 404
        u = users[0]
        ref_earned = float(u.get('ref_earned', 0) or 0)
        if ref_earned < 1.0:
            return jsonify({'error': 'Min 1 TON', 'ref_earned': ref_earned}), 400
        bal = float(u.get('balance', 0) or 0)
        new_bal = round(bal + ref_earned, 4)
        sb_update('users', f'id=eq.{uid}', {
            'balance': new_bal,
            'ref_earned': 0
        })
        return jsonify({
            'success': True,
            'claimed': ref_earned,
            'new_balance': new_bal
        })
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
        uh = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": ct
        }
        requests.post(
            f"{SUPABASE_URL}/storage/v1/object/media/{path}",
            data=fb, headers=uh
        )
        url = f"{SUPABASE_URL}/storage/v1/object/public/media/{path}"
        return jsonify({'url': url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/get_prices', methods=['GET'])
def api_get_prices():
    try:
        tariff = request.args.get('tariff', 'standard')
        views = max(100, int(request.args.get('views', 100)))
        multiplier = views / 100.0

        ton_price = PRICES_TON.get(tariff, 6.49) * multiplier
        gram_eq = PRICES_GRAM_EQ.get(tariff, 5.90) * multiplier
        usdt_eq = PRICES_USDT_EQ.get(tariff, 5.77) * multiplier

        rates = get_crypto_rates()

        result = {
            'ton': {'amount': round(ton_price, 2), 'currency': 'TON'},
            'gram': None,
            'usdt': None,
            'rates_debug': rates,
            'discounts': {
                'gram': {'standard': 10, 'pro': 5},
                'usdt': {'standard': 5, 'pro': 2.5}
            }
        }

        if rates['GRAM'] and rates['GRAM'] > 0:
            gram_amount = round(gram_eq / rates['GRAM'], 2)
            result['gram'] = {
                'amount': gram_amount,
                'currency': 'GRAM',
                'ton_equivalent': round(gram_eq, 2),
                'rate': rates['GRAM']
            }

        if rates['USDT'] and rates['USDT'] > 0:
            usdt_amount = round(usdt_eq * rates['USDT'], 2)
            result['usdt'] = {
                'amount': usdt_amount,
                'currency': 'USDT',
                'ton_equivalent': round(usdt_eq, 2),
                'rate': rates['USDT']
            }

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/create_invoice', methods=['POST'])
def api_create_invoice():
    try:
        d = request.json
        aid = d.get('ad_id')
        amt = d.get('amount')
        currency = d.get('currency', 'TON')
        if not aid or not amt:
            return jsonify({'error': 'Missing'}), 400

        asset = currency.upper()
        if asset not in ['TON', 'GRAM', 'USDT']:
            asset = 'TON'

        p = {
            'currency_type': 'crypto',
            'asset': asset,
            'amount': str(round(float(amt), 2)),
            'description': 'Mytonads ad payment',
            'payload': str(aid)
        }
        r = requests.post(
            f"{CRYPTOBOT_URL}/createInvoice",
            json=p,
            headers={'Crypto-Pay-API-Token': CRYPTOBOT_TOKEN}
        )
        resp = r.json()
        if resp.get('ok') and resp.get('result'):
            inv = resp['result']
            return jsonify({
                'invoice_id': inv.get('invoice_id'),
                'pay_url': inv.get('pay_url')
            })
        return jsonify({'error': 'Invoice failed', 'details': resp}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/check_payment')
def api_check_payment():
    try:
        aid = request.args.get('ad_id')
        if not aid:
            return jsonify({'paid': False})
        r = requests.get(
            f"{CRYPTOBOT_URL}/getInvoices",
            headers={'Crypto-Pay-API-Token': CRYPTOBOT_TOKEN}
        )
        resp = r.json()
        if resp.get('ok') and resp.get('result'):
            items = resp['result'].get('items', [])
            for inv in items:
                if inv.get('payload') == str(aid) and inv.get('status') == 'paid':
                    sb_update('ads', f'id=eq.{aid}', {'is_active': True})
                    return jsonify({'paid': True})
        return jsonify({'paid': False})
    except:
        return jsonify({'paid': False})


@app.route('/api/check_subscription', methods=['POST'])
def api_check_subscription():
    try:
        d = request.json
        telegram_id = d.get('telegram_id')
        channel_link = d.get('channel_link', '')

        if not telegram_id or not channel_link:
            return jsonify({'subscribed': False, 'error': 'Missing data'}), 400

        # Extract channel username from link
        channel = channel_link.strip().rstrip('/')
        if '/t.me/' in channel:
            channel = channel.split('/t.me/')[-1]
        elif 't.me/' in channel:
            channel = channel.split('t.me/')[-1]
        if '?' in channel:
            channel = channel.split('?')[0]
        if not channel.startswith('@'):
            channel = '@' + channel

        # Check via Telegram Bot API
        r = requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember",
            params={'chat_id': channel, 'user_id': telegram_id}
        )
        resp = r.json()

        if resp.get('ok') and resp.get('result'):
            status = resp['result'].get('status', '')
            if status in ['member', 'administrator', 'creator']:
                return jsonify({'subscribed': True, 'status': status})
            else:
                return jsonify({'subscribed': False, 'status': status})
        else:
            desc = resp.get('description', '')
            return jsonify({
                'subscribed': False,
                'error': 'Cannot check. Bot must be admin in channel.',
                'details': desc
            })
    except Exception as e:
        return jsonify({'subscribed': False, 'error': str(e)}), 500


@app.route('/api/withdraw', methods=['POST'])
def api_withdraw():
    try:
        d = request.json
        uid = d.get('user_id')
        w = d.get('wallet_address')
        if not uid or not w:
            return jsonify({'error': 'Missing'}), 400
        users = sb_get('users', f'id=eq.{uid}')
        if not users:
            return jsonify({'error': 'Not found'}), 404
        u = users[0]
        bal = float(u.get('balance', 0) or 0)
        if bal < 1.5:
            return jsonify({'error': 'Min 1.5 TON'}), 400
        amt_ton = round(bal, 2)

        bot_balances = {}
        try:
            br = requests.get(
                f"{CRYPTOBOT_URL}/getBalance",
                headers={'Crypto-Pay-API-Token': CRYPTOBOT_TOKEN}
            )
            bresp = br.json()
            if bresp.get('ok') and bresp.get('result'):
                for b in bresp['result']:
                    available = float(b.get('available', 0))
                    if available > 0:
                        bot_balances[b['currency_code']] = available
        except:
            pass

        rates = get_crypto_rates()
        withdraw_asset = None
        withdraw_amount = None

        # 1. Try GRAM first
        if rates.get('GRAM') and rates['GRAM'] > 0:
            gram_amount = round(amt_ton / rates['GRAM'], 2)
            if bot_balances.get('GRAM', 0) >= gram_amount:
                withdraw_asset = 'GRAM'
                withdraw_amount = gram_amount

        # 2. Try USDT
        if not withdraw_asset:
            if rates.get('USDT') and rates['USDT'] > 0:
                usdt_amount = round(amt_ton * rates['USDT'], 2)
                if bot_balances.get('USDT', 0) >= usdt_amount:
                    withdraw_asset = 'USDT'
                    withdraw_amount = usdt_amount

        # 3. Try TON
        if not withdraw_asset:
            if bot_balances.get('TON', 0) >= amt_ton:
                withdraw_asset = 'TON'
                withdraw_amount = amt_ton

        if not withdraw_asset:
            return jsonify({
                'error': 'Insufficient bot balance. Try later.',
                'bot_balances': bot_balances
            }), 400

        r2 = requests.post(
            f"{CRYPTOBOT_URL}/createCheck",
            json={'asset': withdraw_asset, 'amount': str(withdraw_amount)},
            headers={'Crypto-Pay-API-Token': CRYPTOBOT_TOKEN}
        )
        resp2 = r2.json()
        cu = ''
        if resp2.get('ok') and resp2.get('result'):
            cu = resp2['result'].get('bot_check_url', '')
        else:
            return jsonify({
                'error': 'Check creation failed',
                'details': resp2
            }), 500

        sb_update('users', f'id=eq.{uid}', {'balance': 0})
        return jsonify({
            'success': True,
            'amount': withdraw_amount,
            'currency': withdraw_asset,
            'ton_equivalent': amt_ton,
            'check_url': cu
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/my_ads')
def api_my_ads():
    try:
        tid = request.args.get('telegram_id')
        if not tid:
            return jsonify([])
        ads = sb_get('ads',
            f'creator_telegram_id=eq.{tid}&select=*&order=created_at.desc')
        return jsonify(ads if ads else [])
    except:
        return jsonify([])


@app.route('/api/debug_rates')
def debug_rates():
    try:
        r = requests.get(
            f"{CRYPTOBOT_URL}/getExchangeRates",
            headers={'Crypto-Pay-API-Token': CRYPTOBOT_TOKEN}
        )
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
        text='\U0001f48e Открыть Mytonads',
        web_app=tg_types.WebAppInfo(url=url)
    ))
    tgbot.send_message(message.chat.id,
        '\U0001f48e <b>Mytonads</b>\n\n'
        '\U0001f441 Смотри рекламу \u2014 зарабатывай TON\n'
        '\U0001f4e2 Размещай рекламу\n\n'
        'Нажми кнопку \U0001f447',
        parse_mode='HTML', reply_markup=mk)


@tgbot.message_handler(commands=['endads'])
def cmd_endads(message):
    tid = message.from_user.id
    ads = sb_get('ads',
        f'creator_telegram_id=eq.{tid}&is_active=eq.true&select=*')
    if not ads or len(ads) == 0:
        tgbot.send_message(message.chat.id,
            '\U0001f4ed <b>У вас нет активной рекламы</b>',
            parse_mode='HTML')
        return
    mk = tg_types.InlineKeyboardMarkup()
    for a in ads:
        t = a.get('title', 'Без названия')[:30]
        mk.add(tg_types.InlineKeyboardButton(
            text=f"\U0001f4cc {t}",
            callback_data=f"adinfo_{a.get('id')}"
        ))
    tgbot.send_message(message.chat.id,
        '\U0001f4cb <b>Ваши активные рекламы:</b>\n\n'
        'Выберите для просмотра статистики:',
        parse_mode='HTML', reply_markup=mk)


@tgbot.callback_query_handler(func=lambda c: c.data.startswith('adinfo_'))
def cb_adinfo(call):
    aid = call.data.replace('adinfo_', '')
    ads = sb_get('ads', f'id=eq.{aid}&select=*')
    if not ads or len(ads) == 0:
        tgbot.answer_callback_query(call.id, 'Не найдена')
        return
    a = ads[0]
    t = a.get('title', 'Без названия')
    vd = a.get('views_done', 0) or 0
    vo = a.get('views_ordered', 0) or 0
    vl = max(0, vo - vd)
    tf = (a.get('tariff', 'standard') or 'standard').upper()
    st = '\u2705 Активна' if a.get('is_active') else '\U0001f6d1 Завершена'
    pr = int(vd / vo * 100) if vo > 0 else 0
    fl = int(10 * pr / 100)
    bar = '\u2588' * fl + '\u2591' * (10 - fl)
    txt = (
        f"\U0001f4ca <b>Статистика рекламы</b>\n\n"
        f"\U0001f4cc Название: <b>{t}</b>\n"
        f"\U0001f4ce Тариф: <b>{tf}</b>\n"
        f"\U0001f4c8 Статус: {st}\n\n"
        f"\U0001f441 Просмотров: <b>{vd}/{vo}</b>\n"
        f"\u23f3 Осталось: <b>{vl}</b>\n\n"
        f"[{bar}] {pr}%"
    )
    tgbot.edit_message_text(txt, call.message.chat.id,
        call.message.message_id, parse_mode='HTML')
    tgbot.answer_callback_query(call.id)


@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        j = request.get_json()
        if j:
            upd = telebot.types.Update.de_json(j)
            tgbot.process_new_updates([upd])
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
