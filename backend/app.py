from flask import Flask, request, jsonify, render_template
import requests
import uuid
import os
import base64
import telebot
from telebot import types as tg_types

app = Flask(__name__)

SUPABASE_URL = "https://kjschhxyiobwlrpeoqwp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtqc2NoaHh5aW9id2xycGVvcXdwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDIzMzIzMzcsImV4cCI6MjA1NzkwODMzN30.Z-pDfjKSaWFMgFhIaOPxkdmfGMF8xz-0n0grOOmPjPY"
CRYPTOBOT_TOKEN = "337016:AA1cTpnyuwn6XrS8sHxhSjpJ9gY9wVtriP2"
BOT_TOKEN = "8734788678:AAHNXaFd7VZsQtITaXblhJTyBRs6bVRkLfE"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

tgbot = telebot.TeleBot(BOT_TOKEN)


def sb_get(table, params=""):
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/{table}?{params}", headers=HEADERS)
        if r.status_code == 200:
            return r.json()
        return []
    except:
        return []


def sb_insert(table, data):
    try:
        r = requests.post(f"{SUPABASE_URL}/rest/v1/{table}", json=data, headers=HEADERS)
        if r.status_code in [200, 201]:
            return r.json()
        return []
    except:
        return []


def sb_update(table, params, data):
    try:
        r = requests.patch(f"{SUPABASE_URL}/rest/v1/{table}?{params}", json=data, headers=HEADERS)
        if r.status_code == 200:
            return r.json()
        return []
    except:
        return []


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/debug')
def api_debug():
    try:
        url = f"{SUPABASE_URL}/rest/v1/ads?select=id,is_active&limit=3"
        r = requests.get(url, headers=HEADERS)
        return jsonify({
            'status_code': r.status_code,
            'response': r.text[:500],
            'headers_sent': {
                'apikey': SUPABASE_KEY[:20] + '...',
                'url': url
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/api/ads')
def api_ads():
    try:
        url = f"{SUPABASE_URL}/rest/v1/ads?is_active=eq.true&select=*"
        r = requests.get(url, headers=HEADERS)
        if r.status_code == 200:
            data = r.json()
            return jsonify(data)
        else:
            return jsonify({'error': r.text, 'status': r.status_code}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/user', methods=['POST'])
def api_user():
    data = request.json
    telegram_id = data.get('telegram_id')
    username = data.get('username', '')
    referrer_code = data.get('referrer_code', None)

    if not telegram_id:
        return jsonify({'error': 'No telegram_id'}), 400

    existing = sb_get('users', f'telegram_id=eq.{telegram_id}')

    if existing and len(existing) > 0:
        user = existing[0]
        if username and username != user.get('username', ''):
            sb_update('users', f"id=eq.{user['id']}", {'username': username})
            user['username'] = username

        refs = sb_get('users', f"referred_by=eq.{user['id']}&select=id")
        ref_count = len(refs) if refs else 0

        return jsonify({
            'id': user['id'],
            'telegram_id': user['telegram_id'],
            'username': user.get('username', ''),
            'balance': float(user.get('balance', 0) or 0),
            'total_watched': user.get('total_watched', 0) or 0,
            'ref_code': user.get('ref_code', ''),
            'ref_count': ref_count,
            'ref_earned': float(user.get('ref_earned', 0) or 0)
        })

    ref_code = uuid.uuid4().hex[:8]

    referred_by = None
    if referrer_code:
        referrer = sb_get('users', f'ref_code=eq.{referrer_code}&select=id')
        if referrer and len(referrer) > 0:
            referred_by = referrer[0]['id']

    new_user = {
        'telegram_id': telegram_id,
        'username': username,
        'balance': 0,
        'total_watched': 0,
        'ref_code': ref_code,
        'referred_by': referred_by,
        'ref_earned': 0
    }

    result = sb_insert('users', new_user)

    if result and len(result) > 0:
        user = result[0]
        return jsonify({
            'id': user['id'],
            'telegram_id': user['telegram_id'],
            'username': user.get('username', ''),
            'balance': 0,
            'total_watched': 0,
            'ref_code': ref_code,
            'ref_count': 0,
            'ref_earned': 0
        })

    return jsonify({'error': 'Failed to create user'}), 500


@app.route('/api/ads/create', methods=['POST'])
def api_ads_create():
    data = request.json
    ad = {
        'title': data.get('title', ''),
        'description': data.get('description', ''),
        'link': data.get('link', ''),
        'media_url': data.get('media_url', ''),
        'media_type': data.get('media_type', 'text'),
        'views_ordered': data.get('views_ordered', 100),
        'views_done': 0,
        'price_paid': data.get('price_paid', 0),
        'tariff': data.get('tariff', 'standard'),
        'is_active': False
    }
    result = sb_insert('ads', ad)
    if result and len(result) > 0:
        return jsonify(result[0])
    return jsonify({'error': 'Failed to create ad'}), 500


@app.route('/api/watch', methods=['POST'])
def api_watch():
    data = request.json
    user_id = data.get('user_id')
    ad_id = data.get('ad_id')

    if not user_id or not ad_id:
        return jsonify({'error': 'Missing data'}), 400

    ads = sb_get('ads', f'id=eq.{ad_id}')
    if ads and len(ads) > 0:
        ad_data = ads[0]
        new_views = (ad_data.get('views_done', 0) or 0) + 1
        update_data = {'views_done': new_views}
        if new_views >= (ad_data.get('views_ordered', 0) or 0):
            update_data['is_active'] = False
        sb_update('ads', f'id=eq.{ad_id}', update_data)

    tariff = 'standard'
    if ads and len(ads) > 0:
        tariff = ads[0].get('tariff', 'standard')

    reward = 0.06 if tariff == 'pro' else 0.04

    users = sb_get('users', f'id=eq.{user_id}')
    ref_bonus = 0

    if users and len(users) > 0:
        u = users[0]
        new_balance = float(u.get('balance', 0) or 0) + reward
        new_watched = (u.get('total_watched', 0) or 0) + 1
        sb_update('users', f'id=eq.{user_id}', {
            'balance': new_balance,
            'total_watched': new_watched
        })

        referred_by = u.get('referred_by')
        if referred_by:
            ref_bonus = round(reward * 0.10, 4)
            referrers = sb_get('users', f'id=eq.{referred_by}')
            if referrers and len(referrers) > 0:
                r_user = referrers[0]
                new_ref_balance = float(r_user.get('balance', 0) or 0) + ref_bonus
                new_ref_earned = float(r_user.get('ref_earned', 0) or 0) + ref_bonus
                sb_update('users', f'id=eq.{referred_by}', {
                    'balance': new_ref_balance,
                    'ref_earned': new_ref_earned
                })

    return jsonify({'success': True, 'reward': reward, 'ref_bonus': ref_bonus})


@app.route('/api/upload', methods=['POST'])
def api_upload():
    data = request.json
    file_data = data.get('file_data')
    file_name = data.get('file_name', 'file')
    content_type = data.get('content_type', 'image/jpeg')

    if not file_data:
        return jsonify({'error': 'No file'}), 400

    file_bytes = base64.b64decode(file_data)
    path = f"ads/{uuid.uuid4().hex}_{file_name}"

    upload_headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": content_type
    }
    requests.post(
        f"{SUPABASE_URL}/storage/v1/object/media/{path}",
        data=file_bytes,
        headers=upload_headers
    )

    public_url = f"{SUPABASE_URL}/storage/v1/object/public/media/{path}"
    return jsonify({'url': public_url})


@app.route('/api/create_invoice', methods=['POST'])
def api_create_invoice():
    data = request.json
    ad_id = data.get('ad_id')
    amount = data.get('amount')

    if not ad_id or not amount:
        return jsonify({'error': 'Missing data'}), 400

    try:
        resp = requests.post('https://pay.crypt.bot/api/createInvoice', json={
            'currency_type': 'crypto',
            'asset': 'TON',
            'amount': str(round(float(amount), 2)),
            'description': f'Mytonads ad payment',
            'payload': str(ad_id)
        }, headers={
            'Crypto-Pay-API-Token': CRYPTOBOT_TOKEN
        })
        result = resp.json()
        if result.get('ok'):
            invoice = result['result']
            sb_update('ads', f'id=eq.{ad_id}', {'invoice_id': invoice['invoice_id']})
            return jsonify({'pay_url': invoice['pay_url'], 'invoice_id': invoice['invoice_id']})
        return jsonify({'error': 'Invoice creation failed', 'details': result}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/check_payment')
def api_check_payment():
    ad_id = request.args.get('ad_id')
    if not ad_id:
        return jsonify({'error': 'No ad_id'}), 400

    ads = sb_get('ads', f'id=eq.{ad_id}')
    if not ads or len(ads) == 0:
        return jsonify({'error': 'Ad not found'}), 404

    ad_data = ads[0]
    invoice_id = ad_data.get('invoice_id')

    if not invoice_id:
        return jsonify({'paid': False})

    try:
        resp = requests.get('https://pay.crypt.bot/api/getInvoices', params={
            'invoice_ids': str(invoice_id)
        }, headers={
            'Crypto-Pay-API-Token': CRYPTOBOT_TOKEN
        })
        result = resp.json()
        if result.get('ok') and result['result']['items']:
            status = result['result']['items'][0]['status']
            if status == 'paid':
                sb_update('ads', f'id=eq.{ad_id}', {'is_active': True})
                return jsonify({'paid': True})
        return jsonify({'paid': False})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/withdraw', methods=['POST'])
def api_withdraw():
    data = request.json
    user_id = data.get('user_id')
    wallet = data.get('wallet_address')

    if not user_id or not wallet:
        return jsonify({'error': 'Missing data'}), 400

    users = sb_get('users', f'id=eq.{user_id}')
    if not users or len(users) == 0:
        return jsonify({'error': 'User not found'}), 404

    balance = float(users[0].get('balance', 0) or 0)
    if balance < 1.5:
        return jsonify({'error': 'Minimum 1.5 TON'}), 400

    try:
        resp = requests.post('https://pay.crypt.bot/api/transfer', json={
            'user_id': users[0]['telegram_id'],
            'asset': 'TON',
            'amount': str(round(balance, 2)),
            'spend_id': uuid.uuid4().hex
        }, headers={
            'Crypto-Pay-API-Token': CRYPTOBOT_TOKEN
        })
        result = resp.json()

        sb_insert('withdrawals', {
            'user_id': user_id,
            'amount': balance,
            'wallet_address': wallet,
            'status': 'completed' if result.get('ok') else 'failed'
        })

        if result.get('ok'):
            sb_update('users', f'id=eq.{user_id}', {'balance': 0})
            return jsonify({'success': True, 'amount': round(balance, 2)})
        else:
            return jsonify({'error': result.get('error', {}).get('name', 'Transfer failed')}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/bot_webhook', methods=['POST'])
def bot_webhook():
    update = telebot.types.Update.de_json(request.get_json(force=True))
    tgbot.process_new_updates([update])
    return 'ok'


@tgbot.message_handler(commands=['start'])
def cmd_start(message):
    args = message.text.split()
    ref = args[1] if len(args) > 1 else ''
    url = 'https://insiderad.vercel.app'
    if ref:
        url += '?ref=' + ref
    markup = tg_types.InlineKeyboardMarkup()
    markup.add(tg_types.InlineKeyboardButton(
        text='💎 Открыть Mytonads',
        web_app=tg_types.WebAppInfo(url=url)
    ))
    tgbot.send_message(
        message.chat.id,
        '💎 <b>Mytonads</b>\n\n👁 Смотри рекламу — зарабатывай TON\n📢 Размещай рекламу\n\nНажми кнопку 👇',
        parse_mode='HTML',
        reply_markup=markup
    )


@app.route('/set_webhook')
def set_webhook():
    tgbot.remove_webhook()
    tgbot.set_webhook(url='https://insiderad.vercel.app/bot_webhook')
    return 'Webhook set!'


if __name__ == '__main__':
    app.run(debug=True)
