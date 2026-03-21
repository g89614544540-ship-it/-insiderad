from flask import Flask, request, jsonify, render_template
from supabase import create_client
import requests
import uuid
import os
import telebot
from telebot import types as tg_types

app = Flask(__name__)

SUPABASE_URL = "https://kjschhxyiobwlrpeoqwp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtqc2NoaHh5aW9id2xycGVvcXdwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDIzMzIzMzcsImV4cCI6MjA1NzkwODMzN30.Z-pDfjKSaWFMgFhIaOPxkdmfGMF8xz-0n0grOOmPjPY"
CRYPTOBOT_TOKEN = "337016:AA1cTpnyuwn6XrS8sHxhSjpJ9gY9wVtriP2"
BOT_TOKEN = "8734788678:AAHNXaFd7VZsQtITaXblhJTyBRs6bVRkLfE"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
tgbot = telebot.TeleBot(BOT_TOKEN)

@app.route('/')
def index():
    return render_template('index.html')

# ==================== USER API ====================

@app.route('/api/user', methods=['POST'])
def api_user():
    data = request.json
    telegram_id = data.get('telegram_id')
    username = data.get('username', '')
    referrer_code = data.get('referrer_code', None)

    if not telegram_id:
        return jsonify({'error': 'No telegram_id'}), 400

    existing = supabase.table('users').select('*').eq('telegram_id', telegram_id).execute()

    if existing.data and len(existing.data) > 0:
        user = existing.data[0]
        if username and username != user.get('username', ''):
            supabase.table('users').update({'username': username}).eq('id', user['id']).execute()
            user['username'] = username

        ref_count = 0
        ref_earned = 0
        refs = supabase.table('users').select('id').eq('referred_by', user['id']).execute()
        if refs.data:
            ref_count = len(refs.data)
        ref_earned = float(user.get('ref_earned', 0) or 0)

        return jsonify({
            'id': user['id'],
            'telegram_id': user['telegram_id'],
            'username': user.get('username', ''),
            'balance': float(user.get('balance', 0) or 0),
            'total_watched': user.get('total_watched', 0) or 0,
            'ref_code': user.get('ref_code', ''),
            'ref_count': ref_count,
            'ref_earned': ref_earned
        })

    ref_code = uuid.uuid4().hex[:8]

    referred_by = None
    if referrer_code:
        referrer = supabase.table('users').select('id').eq('ref_code', referrer_code).execute()
        if referrer.data and len(referrer.data) > 0:
            referred_by = referrer.data[0]['id']

    new_user = {
        'telegram_id': telegram_id,
        'username': username,
        'balance': 0,
        'total_watched': 0,
        'ref_code': ref_code,
        'referred_by': referred_by,
        'ref_earned': 0
    }

    result = supabase.table('users').insert(new_user).execute()

    if result.data and len(result.data) > 0:
        user = result.data[0]
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

# ==================== ADS API ====================

@app.route('/api/ads')
def api_ads():
    result = supabase.table('ads').select('*').eq('is_active', True).execute()
    return jsonify(result.data or [])

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
    result = supabase.table('ads').insert(ad).execute()
    if result.data and len(result.data) > 0:
        return jsonify(result.data[0])
    return jsonify({'error': 'Failed'}), 500

# ==================== WATCH API ====================

@app.route('/api/watch', methods=['POST'])
def api_watch():
    data = request.json
    user_id = data.get('user_id')
    ad_id = data.get('ad_id')

    if not user_id or not ad_id:
        return jsonify({'error': 'Missing data'}), 400

    ad = supabase.table('ads').select('*').eq('id', ad_id).execute()
    if ad.data and len(ad.data) > 0:
        ad_data = ad.data[0]
        new_views = (ad_data.get('views_done', 0) or 0) + 1
        update_data = {'views_done': new_views}
        if new_views >= ad_data.get('views_ordered', 0):
            update_data['is_active'] = False
        supabase.table('ads').update(update_data).eq('id', ad_id).execute()

    tariff = 'standard'
    if ad.data and len(ad.data) > 0:
        tariff = ad.data[0].get('tariff', 'standard')

    reward = 0.06 if tariff == 'pro' else 0.04

    user = supabase.table('users').select('*').eq('id', user_id).execute()
    ref_bonus = 0

    if user.data and len(user.data) > 0:
        u = user.data[0]
        new_balance = float(u.get('balance', 0) or 0) + reward
        new_watched = (u.get('total_watched', 0) or 0) + 1
        supabase.table('users').update({
            'balance': new_balance,
            'total_watched': new_watched
        }).eq('id', user_id).execute()

        referred_by = u.get('referred_by')
        if referred_by:
            ref_bonus = round(reward * 0.10, 4)
            referrer = supabase.table('users').select('*').eq('id', referred_by).execute()
            if referrer.data and len(referrer.data) > 0:
                r = referrer.data[0]
                new_ref_balance = float(r.get('balance', 0) or 0) + ref_bonus
                new_ref_earned = float(r.get('ref_earned', 0) or 0) + ref_bonus
                supabase.table('users').update({
                    'balance': new_ref_balance,
                    'ref_earned': new_ref_earned
                }).eq('id', referred_by).execute()

    return jsonify({'success': True, 'reward': reward, 'ref_bonus': ref_bonus})

# ==================== UPLOAD API ====================

@app.route('/api/upload', methods=['POST'])
def api_upload():
    data = request.json
    file_data = data.get('file_data')
    file_name = data.get('file_name', 'file')
    content_type = data.get('content_type', 'image/jpeg')

    if not file_data:
        return jsonify({'error': 'No file'}), 400

    import base64
    file_bytes = base64.b64decode(file_data)
    path = f"ads/{uuid.uuid4().hex}_{file_name}"

    res = supabase.storage.from_('media').upload(path, file_bytes, {
        'content-type': content_type
    })

    public_url = f"{SUPABASE_URL}/storage/v1/object/public/media/{path}"
    return jsonify({'url': public_url})

# ==================== PAYMENT API ====================

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
            'amount': str(round(amount, 2)),
            'description': f'Mytonads ad #{ad_id}',
            'payload': str(ad_id)
        }, headers={
            'Crypto-Pay-API-Token': CRYPTOBOT_TOKEN
        })
        result = resp.json()
        if result.get('ok'):
            invoice = result['result']
            supabase.table('ads').update({
                'invoice_id': invoice['invoice_id']
            }).eq('id', ad_id).execute()
            return jsonify({'pay_url': invoice['pay_url'], 'invoice_id': invoice['invoice_id']})
        return jsonify({'error': 'Invoice failed'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/check_payment')
def api_check_payment():
    ad_id = request.args.get('ad_id')
    if not ad_id:
        return jsonify({'error': 'No ad_id'}), 400

    ad = supabase.table('ads').select('*').eq('id', ad_id).execute()
    if not ad.data or len(ad.data) == 0:
        return jsonify({'error': 'Ad not found'}), 404

    ad_data = ad.data[0]
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
                supabase.table('ads').update({'is_active': True}).eq('id', ad_id).execute()
                return jsonify({'paid': True})
        return jsonify({'paid': False})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== WITHDRAW API ====================

@app.route('/api/withdraw', methods=['POST'])
def api_withdraw():
    data = request.json
    user_id = data.get('user_id')
    wallet = data.get('wallet_address')

    if not user_id or not wallet:
        return jsonify({'error': 'Missing data'}), 400

    user = supabase.table('users').select('*').eq('id', user_id).execute()
    if not user.data or len(user.data) == 0:
        return jsonify({'error': 'User not found'}), 404

    balance = float(user.data[0].get('balance', 0) or 0)
    if balance < 1.5:
        return jsonify({'error': 'Minimum 1.5 TON'}), 400

    try:
        resp = requests.post('https://pay.crypt.bot/api/transfer', json={
            'user_id': user.data[0]['telegram_id'],
            'asset': 'TON',
            'amount': str(round(balance, 2)),
            'spend_id': uuid.uuid4().hex
        }, headers={
            'Crypto-Pay-API-Token': CRYPTOBOT_TOKEN
        })
        result = resp.json()

        supabase.table('withdrawals').insert({
            'user_id': user_id,
            'amount': balance,
            'wallet_address': wallet,
            'status': 'completed' if result.get('ok') else 'failed'
        }).execute()

        if result.get('ok'):
            supabase.table('users').update({'balance': 0}).eq('id', user_id).execute()
            return jsonify({'success': True, 'amount': round(balance, 2)})
        else:
            return jsonify({'error': result.get('error', {}).get('name', 'Transfer failed')}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== TELEGRAM BOT ====================

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

# ==================== RUN ====================

if __name__ == '__main__':
    app.run(debug=True)
