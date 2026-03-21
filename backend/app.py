from flask import Flask, request, jsonify
import requests
import uuid
import base64
import os

app = Flask(__name__, static_folder='templates')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

SB_URL = "https://kjschhxyiobwlrpeoqwp.supabase.co"
SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtqc2NoaHh5aW9id2xycGVvcXdwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MzkxNzYyMiwiZXhwIjoyMDg5NDkzNjIyfQ.Vs5RIXIow314syxcM-jjDWxr4roP72fQ22BS4QY5XY4"
CRYPTO_BOT_TOKEN = "552796:AAJmyEgL1NMBR1WROTDN1fWRW4nOHG8le9O"
CRYPTO_API = "https://pay.crypt.bot/api"

REF_PERCENT = 0.10


def sb_headers():
    return {
        "apikey": SB_KEY,
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }


def sb_get(table, params=""):
    r = requests.get(f"{SB_URL}/rest/v1/{table}?{params}&select=*", headers=sb_headers())
    return r.json()


def sb_post(table, data):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", json=data, headers=sb_headers())
    return r.json()


def sb_patch(table, params, data):
    r = requests.patch(f"{SB_URL}/rest/v1/{table}?{params}", json=data, headers=sb_headers())
    return r.json()


def generate_ref_code():
    return uuid.uuid4().hex[:8]


def get_ref_count(ref_code):
    try:
        refs = sb_get("users", f"referred_by=eq.{ref_code}")
        if isinstance(refs, list):
            return len(refs)
        return 0
    except:
        return 0


@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/api/health')
def health():
    return jsonify({"status": "ok"})


@app.route('/api/bot_balance')
def bot_balance():
    try:
        r = requests.get(f"{CRYPTO_API}/getBalance",
            headers={"Crypto-Pay-API-Token": CRYPTO_BOT_TOKEN}).json()
        return jsonify(r)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/user', methods=['POST'])
def api_user():
    try:
        data = request.json
        tid = str(data.get('telegram_id'))
        referrer_code = data.get('referrer_code', '')

        users = sb_get("users", f"telegram_id=eq.{tid}")
        if isinstance(users, list) and len(users) > 0:
            user = users[0]
            # Обновляем username если изменился
            uname = data.get('username', '')
            if uname and uname != user.get('username', ''):
                sb_patch("users", f"id=eq.{user['id']}", {"username": uname})
                user['username'] = uname

            # Добавляем ref_count
            user['ref_count'] = get_ref_count(user.get('ref_code', ''))
            return jsonify(user)

        # Новый пользователь
        ref_code = generate_ref_code()
        new_user_data = {
            "telegram_id": tid,
            "username": data.get('username', ''),
            "balance": 0,
            "wallet_address": "",
            "ref_code": ref_code,
            "referred_by": "",
            "ref_earned": 0
        }

        # Привязка реферала
        if referrer_code:
            referrers = sb_get("users", f"ref_code=eq.{referrer_code}")
            if isinstance(referrers, list) and len(referrers) > 0:
                referrer = referrers[0]
                # Нельзя пригласить самого себя
                if str(referrer.get('telegram_id')) != tid:
                    new_user_data['referred_by'] = referrer_code

        new_user = sb_post("users", new_user_data)

        if isinstance(new_user, list) and len(new_user) > 0:
            new_user[0]['ref_count'] = 0
            return jsonify(new_user[0])
        return jsonify(new_user)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/ads', methods=['GET'])
def api_ads():
    try:
        ads = sb_get("ads", "status=eq.active&paid=eq.true")
        return jsonify(ads if isinstance(ads, list) else [])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/upload', methods=['POST'])
def api_upload():
    try:
        data = request.json
        file_data = data.get('file_data')
        file_name = data.get('file_name', 'file.jpg')
        content_type = data.get('content_type', 'image/jpeg')

        if not file_data:
            return jsonify({"error": "no file"}), 400

        file_bytes = base64.b64decode(file_data)

        is_video = content_type.startswith('video')
        max_size = 20 * 1024 * 1024 if is_video else 5 * 1024 * 1024

        if len(file_bytes) > max_size:
            limit_mb = 20 if is_video else 5
            return jsonify({"error": f"Файл слишком большой! Максимум {limit_mb}MB"}), 400

        if is_video:
            if 'mp4' in content_type:
                ext = '.mp4'
            elif 'webm' in content_type:
                ext = '.webm'
            elif 'mov' in content_type or 'quicktime' in content_type:
                ext = '.mp4'
            elif '3gp' in content_type:
                ext = '.mp4'
            else:
                ext = '.mp4'
        else:
            if 'png' in content_type:
                ext = '.png'
            elif 'gif' in content_type:
                ext = '.gif'
            elif 'webp' in content_type:
                ext = '.webp'
            else:
                ext = '.jpg'

        unique_name = f"{uuid.uuid4()}{ext}"

        bucket_headers = {
            "apikey": SB_KEY,
            "Authorization": f"Bearer {SB_KEY}",
            "Content-Type": "application/json"
        }
        requests.post(f"{SB_URL}/storage/v1/bucket",
            headers=bucket_headers,
            json={"id": "ads-media", "name": "ads-media", "public": True})

        upload_headers = {
            "apikey": SB_KEY,
            "Authorization": f"Bearer {SB_KEY}",
            "Content-Type": content_type,
            "x-upsert": "true"
        }
        r = requests.post(
            f"{SB_URL}/storage/v1/object/ads-media/{unique_name}",
            headers=upload_headers,
            data=file_bytes
        )

        if r.status_code in [200, 201]:
            url = f"{SB_URL}/storage/v1/object/public/ads-media/{unique_name}"
            return jsonify({"url": url})

        return jsonify({"error": "upload failed", "details": r.text, "status": r.status_code}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/ads/create', methods=['POST'])
def api_ads_create():
    try:
        data = request.json
        tariff = data.get('tariff', 'standard')
        ad = sb_post("ads", {
            "title": data.get('title', ''),
            "description": data.get('description', ''),
            "link": data.get('link', ''),
            "media_url": data.get('media_url', ''),
            "media_type": data.get('media_type', 'text'),
            "views_ordered": int(data.get('views_ordered', 100)),
            "views_done": 0,
            "price_paid": float(data.get('price_paid', 5.9)),
            "tariff": tariff,
            "status": "pending",
            "paid": False
        })
        if isinstance(ad, list) and len(ad) > 0:
            return jsonify(ad[0])
        return jsonify(ad)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/create_invoice', methods=['POST'])
def api_create_invoice():
    try:
        data = request.json
        ad_id = data.get('ad_id')
        amount = float(data.get('amount', 5.9))
        inv = requests.post(f"{CRYPTO_API}/createInvoice",
            headers={"Crypto-Pay-API-Token": CRYPTO_BOT_TOKEN},
            json={
                "asset": "TON",
                "amount": str(amount),
                "description": f"Ad #{ad_id}",
                "payload": str(ad_id)
            }).json()
        if inv.get('ok'):
            pay_url = inv['result'].get('pay_url', '')
            invoice_id = inv['result'].get('invoice_id', '')
            sb_patch("ads", f"id=eq.{ad_id}", {"invoice_id": str(invoice_id)})
            return jsonify({"pay_url": pay_url, "invoice_id": invoice_id})
        return jsonify({"error": "invoice failed", "details": inv}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/check_payment', methods=['GET'])
def api_check_payment():
    try:
        ad_id = request.args.get('ad_id')
        ads = sb_get("ads", f"id=eq.{ad_id}")
        if isinstance(ads, list) and len(ads) > 0:
            ad = ads[0]
            if ad.get('paid'):
                return jsonify({"paid": True})
            invoice_id = ad.get('invoice_id')
            if invoice_id:
                inv = requests.post(f"{CRYPTO_API}/getInvoices",
                    headers={"Crypto-Pay-API-Token": CRYPTO_BOT_TOKEN},
                    json={"invoice_ids": [int(invoice_id)]}).json()
                if inv.get('ok'):
                    items = inv['result'].get('items', [])
                    if items and items[0].get('status') == 'paid':
                        sb_patch("ads", f"id=eq.{ad_id}", {"paid": True, "status": "active"})
                        return jsonify({"paid": True})
        return jsonify({"paid": False})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/watch', methods=['POST'])
def api_watch():
    try:
        data = request.json
        ad_id = data.get('ad_id')
        uid = data.get('user_id')
        if not ad_id or not uid:
            return jsonify({"error": "missing data"}), 400

        ads = sb_get("ads", f"id=eq.{ad_id}")
        if not isinstance(ads, list) or len(ads) == 0:
            return jsonify({"error": "ad not found"}), 404
        ad = ads[0]

        if ad['views_done'] >= ad['views_ordered']:
            return jsonify({"error": "views complete"}), 400

        views_list = sb_get("ad_views", f"ad_id=eq.{ad_id}&user_id=eq.{uid}")
        if isinstance(views_list, list) and len(views_list) > 0:
            return jsonify({"error": "already viewed"}), 400

        sb_post("ad_views", {"ad_id": ad_id, "user_id": uid})

        new_views = ad['views_done'] + 1
        status = "completed" if new_views >= ad['views_ordered'] else "active"
        sb_patch("ads", f"id=eq.{ad_id}", {"views_done": new_views, "status": status})

        tariff = ad.get('tariff', 'standard')
        reward = 0.06 if tariff == 'pro' else 0.04

        # Начисляем зрителю
        users = sb_get("users", f"id=eq.{uid}")
        if isinstance(users, list) and len(users) > 0:
            user = users[0]
            new_balance = round(float(user.get('balance', 0)) + reward, 4)
            sb_patch("users", f"id=eq.{uid}", {"balance": new_balance})

            # Реферальный бонус
            ref_bonus = 0
            referred_by = user.get('referred_by', '')
            if referred_by:
                ref_bonus = round(reward * REF_PERCENT, 4)
                referrers = sb_get("users", f"ref_code=eq.{referred_by}")
                if isinstance(referrers, list) and len(referrers) > 0:
                    referrer = referrers[0]
                    new_ref_balance = round(float(referrer.get('balance', 0)) + ref_bonus, 4)
                    new_ref_earned = round(float(referrer.get('ref_earned', 0)) + ref_bonus, 4)
                    sb_patch("users", f"id=eq.{referrer['id']}", {
                        "balance": new_ref_balance,
                        "ref_earned": new_ref_earned
                    })

            return jsonify({"success": True, "reward": reward, "ref_bonus": ref_bonus})

        return jsonify({"success": True, "reward": reward, "ref_bonus": 0})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/withdraw', methods=['POST'])
def api_withdraw():
    try:
        data = request.json
        uid = data.get('user_id')
        wallet = data.get('wallet_address')
        if not wallet:
            return jsonify({"error": "Введите адрес кошелька"}), 400
        users = sb_get("users", f"id=eq.{uid}")
        if not isinstance(users, list) or len(users) == 0:
            return jsonify({"error": "Пользователь не найден"}), 404
        balance = float(users[0].get('balance', 0))
        if balance < 1.5:
            return jsonify({"error": "Минимум 1.5 TON"}), 400

        sb_patch("users", f"id=eq.{uid}", {"wallet_address": wallet})

        bot_ton = 0
        try:
            bal_r = requests.get(f"{CRYPTO_API}/getBalance",
                headers={"Crypto-Pay-API-Token": CRYPTO_BOT_TOKEN}).json()
            if bal_r.get('ok'):
                for coin in bal_r['result']:
                    if coin['currency_code'] == 'TON':
                        bot_ton = float(coin['available'])
        except:
            bot_ton = 0

        if bot_ton < balance:
            return jsonify({"error": f"На боте {bot_ton} TON, нужно {balance} TON. Попробуйте позже."}), 400

        spend_id = str(uuid.uuid4())
        check = requests.post(f"{CRYPTO_API}/createCheck",
            headers={"Crypto-Pay-API-Token": CRYPTO_BOT_TOKEN},
            json={"asset": "TON", "amount": str(balance)}).json()

        if check.get('ok'):
            check_url = check['result']['bot_check_url']
            sb_patch("users", f"id=eq.{uid}", {"balance": 0})
            sb_post("withdrawals", {
                "user_id": uid,
                "amount": balance,
                "wallet_address": wallet,
                "status": "completed",
                "spend_id": spend_id
            })
            return jsonify({"success": True, "amount": balance, "check_url": check_url})

        return jsonify({"error": "Ошибка создания чека: " + str(check)}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/webhook/cryptobot', methods=['POST'])
def webhook_cryptobot():
    try:
        data = request.json
        if data.get('update_type') == 'invoice_paid':
            payload = data.get('payload', {})
            ad_id = payload.get('payload', '')
            if ad_id:
                sb_patch("ads", f"id=eq.{ad_id}", {"paid": True, "status": "active"})
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


from bot import start_bot_thread
start_bot_thread()

from bot import start_bot_thread
start_bot_thread()
