from flask import Flask, request, jsonify, render_template
import requests
import os

app = Flask(__name__)

CRYPTO_BOT_TOKEN = "552796:AAJmyEgL1NMBR1WROTDN1fWRW4nOHG8le9O"
CRYPTO_API = "https://pay.crypt.bot/api"

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

def sb_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

def sb_post(table, data):
    r = requests.post(f"{SUPABASE_URL}/rest/v1/{table}", json=data, headers=sb_headers())
    r.raise_for_status()
    return r.json()

def sb_get(table, params=""):
    r = requests.get(f"{SUPABASE_URL}/rest/v1/{table}?{params}", headers=sb_headers())
    r.raise_for_status()
    return r.json()

def sb_patch(table, params, data):
    r = requests.patch(f"{SUPABASE_URL}/rest/v1/{table}?{params}", json=data, headers=sb_headers())
    r.raise_for_status()
    return r.json()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/api/ads')
def get_ads():
    try:
        ads = sb_get("ads", "status=eq.active&order=created_at.desc")
        return jsonify(ads)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/init_user', methods=['POST'])
def init_user():
    try:
        data = request.json
        tid = data.get('telegram_id')
        username = data.get('username', '')
        existing = sb_get("users", f"telegram_id=eq.{tid}")
        if existing:
            return jsonify(existing[0])
        user = sb_post("users", {"telegram_id": tid, "username": username})
        return jsonify(user[0] if isinstance(user, list) else user)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/create_invoice', methods=['POST'])
def create_invoice():
    try:
        data = request.json
        title = data.get('title', '')
        description = data.get('description', '')
        link = data.get('link', '')
        media_url = data.get('media_url', '')
        media_type = data.get('media_type', 'text')
        views = int(data.get('views', 100))
        price = round(views * 0.05, 2)

        r = requests.post(f"{CRYPTO_API}/createInvoice", headers={
            "Crypto-Pay-API-Token": CRYPTO_BOT_TOKEN
        }, json={
            "amount": str(price),
            "currency_type": "crypto",
            "asset": "USDT",
            "description": f"InsiderAd: {views} views",
            "payload": title
        })
        resp = r.json()

        if not resp.get("ok"):
            return jsonify({"error": resp}), 400

        invoice = resp["result"]
        sb_post("ads", {
            "title": title,
            "description": description,
            "link": link,
            "media_url": media_url,
            "media_type": media_type,
            "views_ordered": views,
            "price_paid": price,
            "invoice_id": str(invoice["invoice_id"]),
            "status": "pending",
            "paid": False
        })

        return jsonify({"ok": True, "pay_url": invoice["pay_url"]})
    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

@app.route('/api/test_create')
def test_create():
    try:
        result = sb_post("ads", {
            "title": "Test Ad",
            "description": "test",
            "link": "https://t.me/test",
            "media_url": "",
            "media_type": "text",
            "views_ordered": 100,
            "views_done": 0,
            "price_paid": 5,
            "status": "active",
            "paid": False
        })
        return jsonify({"ok": True, "result": result})
    except Exception as e:
        import traceback
        return jsonify({"ok": False, "error": str(e), "trace": traceback.format_exc()})

if __name__ == '__main__':
    app.run(debug=True)
