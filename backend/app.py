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
        users = sb_get("users", f"telegram_id=eq.{tid}")
        if isinstance(users, list) and len(users) > 0:
            return jsonify(users[0])
        new_user = sb_post("users", {
            "telegram_id": tid,
            "username": data.get('username', ''),
            "balance": 0,
            "wallet_address": ""
        })
        if isinstance(new_user, list):
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
            "price_paid": float(data.get('price_paid', 5.5)),
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
        amount = float(data.get('amount', 5.5))
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
        if tariff == 'pro':
            reward = 0.06
        else:
            reward = 0.04
        users = sb_get("users", f"id=eq.{uid}")
        if isinstance(users, list) and len(users) > 0:
            new_balance = round(float(users[0].get('balance', 0)) + reward, 4)
            sb_patch("users", f"id=eq.{uid}", {"balance": new_balance})
        return jsonify({"success": True, "reward": reward})
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


if __name__ == '__main__':
    app.run(debug=True)
