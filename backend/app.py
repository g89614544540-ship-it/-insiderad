from flask import Flask, request, jsonify, send_from_directory
import requests
import uuid
import base64
import os

app = Flask(__name__, static_folder='templates')

WALLET = "UQBBklp5lYFEgYig5200TPsLjtDOnAUUGToyiFhzI6D0tP8d"
SB_URL = "https://kjschhxyiobwlrpeoqwp.supabase.co"
SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtqc2NoaHh5aW9id2xycGVvcXdwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MzkxNzYyMiwiZXhwIjoyMDg5NDkzNjIyfQ.Vs5RIXIow314syxcM-jjDWxr4roP72fQ22BS4QY5XY4"
CRYPTO_BOT_TOKEN = "552796:AAJmyEgL1NMBR1WROTDN1fWRW4nOHG8le9O"
CRYPTO_API = "https://pay.crypt.bot/api"

def sb_headers():
    return {"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}", "Content-Type": "application/json", "Prefer": "return=representation"}

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

@app.route('/api/set_wallet', methods=['POST'])
def api_set_wallet():
    try:
        data = request.json
        uid = data.get('user_id')
        wallet = data.get('wallet_address', '')
        if not wallet:
            return jsonify({"error": "wallet required"}), 400
        result = sb_patch("users", f"id=eq.{uid}", {"wallet_address": wallet})
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ads', methods=['GET'])
def api_ads():
    try:
        ads = sb_get("ads", "status=eq.active&paid=eq.true")
        return jsonify(ads if isinstance(ads, list) else [])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/create_ad', methods=['POST'])
def api_create_ad():
    try:
        data = request.json
        views = int(data.get('views', 100))
        price = round(views * 0.05, 2)
        ad = sb_post("ads", {
            "title": data.get('title', ''),
            "description": data.get('description', ''),
            "link": data.get('link', ''),
            "media_url": data.get('media_url', ''),
            "media_type": data.get('media_type', 'text'),
            "views_ordered": views,
            "views_done": 0,
            "price_paid": price,
            "status": "pending",
            "paid": False
        })
        ad_id = ad[0]['id'] if isinstance(ad, list) else ad.get('id')
        inv = requests.post(f"{CRYPTO_API}/createInvoice", headers={
            "Crypto-Pay-API-Token": CRYPTO_BOT_TOKEN
        }, json={
            "asset": "TON",
            "amount": str(price),
            "description": f"Ad #{ad_id} - {views} views",
            "payload": str(ad_id)
        }).json()
        pay_url = inv.get('result', {}).get('pay_url', '')
        return jsonify({"ad": ad, "pay_url": pay_url, "price": price})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        @app.route('/api/webhook/cryptobot', methods=['POST'])
def webhook_cryptobot():
    try:
        data = request.json
        if data.get('update_type') == 'invoice_paid':
            payload = data['payload']
            ad_id = payload.get('payload', '')
            if ad_id:
                sb_patch("ads", f"id=eq.{ad_id}", {"paid": True, "status": "active"})
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/view_ad', methods=['POST'])
def api_view_ad():
    try:
        data = request.json
        ad_id = data.get('ad_id')
        uid = data.get('user_id')
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
        reward = round(ad['price_paid'] / ad['views_ordered'], 4)
        users = sb_get("users", f"id=eq.{uid}")
        if isinstance(users, list) and len(users) > 0:
            new_balance = round(float(users[0].get('balance', 0)) + reward, 4)
            sb_patch("users", f"id=eq.{uid}", {"balance": new_balance})
        return jsonify({"success": True, "reward": reward, "views_done": new_views})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/withdraw', methods=['POST'])
def api_withdraw():
    try:
        data = request.json
        uid = data.get('user_id')
        wallet = data.get('wallet_address')
        if not wallet:
            return jsonify({"error": "wallet_address required"}), 400
        users = sb_get("users", f"id=eq.{uid}")
        if not isinstance(users, list) or len(users) == 0:
            return jsonify({"error": "user not found"}), 404
        balance = float(users[0].get('balance', 0))
        if balance < 1.5:
            return jsonify({"error": "Минимум 1.5 TON для вывода"}), 400
        sb_patch("users", f"id=eq.{uid}", {"wallet_address": wallet})
        spend_id = str(uuid.uuid4())
        transfer = requests.post(f"{CRYPTO_API}/transfer", headers={
            "Crypto-Pay-API-Token": CRYPTO_BOT_TOKEN
        }, json={
            "user_id": int(users[0].get('telegram_id', 0)),
            "asset": "TON",
            "amount": str(balance),
            "spend_id": spend_id,
            "disable_send_notification": False
        }).json()
        if transfer.get('ok'):
            sb_patch("users", f"id=eq.{uid}", {"balance": 0})
            sb_post("withdrawals", {
                "user_id": uid,
                "amount": balance,
                "wallet_address": wallet,
                "status": "completed",
                "spend_id": spend_id
            })
            return jsonify({"success": True, "amount": balance, "transfer": transfer})
        else:
            check = requests.post(f"{CRYPTO_API}/createCheck", headers={
                "Crypto-Pay-API-Token": CRYPTO_BOT_TOKEN
            }, json={
                "asset": "TON",
                "amount": str(balance)
            }).json()
            if check.get('ok'):
                check_url = check['result']['bot_check_url']
                sb_patch("users", f"id=eq.{uid}", {"balance": 0})
                sb_post("withdrawals", {
                    "user_id": uid,
                    "amount": balance,
                    "wallet_address": wallet,
                    "status": "check_sent",
                    "spend_id": spend_id
                })
                return jsonify({"success": True, "amount": balance, "check_url": check_url})
            return jsonify({"error": "withdraw failed", "details": transfer}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/orders')
def api_orders():
    try:
        orders = sb_get("ads", "order=created_at.desc")
        return jsonify(orders if isinstance(orders, list) else [])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/test_create')
def test_create():
    try:
        result = sb_post("ads", {"title": "Test", "description": "test", "link": "https://t.me/test", "media_url": "", "media_type": "text", "views_ordered": 100, "views_done": 0, "price_paid": 5, "status": "active", "paid": False})
        return jsonify({"ok": True, "result": result})
    except Exception as e:
        import traceback
        return jsonify({"ok": False, "error": str(e), "trace": traceback.format_exc()})

if __name__ == '__main__':
    app.run(debug=True)
