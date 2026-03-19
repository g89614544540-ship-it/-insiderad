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
        tg_id = data.get('telegram_id')
        users = sb_get("users", f"telegram_id=eq.{tg_id}")
        if users:
            return jsonify(users[0])
        new = sb_post("users", {"telegram_id": tg_id, "username": data.get("username", ""), "balance": 0, "total_watched": 0})
        return jsonify(new[0] if isinstance(new, list) else new)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/watch', methods=['POST'])
def api_watch():
    try:
        data = request.json
        uid = data.get('user_id')
        users = sb_get("users", f"id=eq.{uid}")
        if not users:
            return jsonify({"error": "not found"}), 404
        u = users[0]
        nb = float(u['balance']) + 0.04
        nw = u['total_watched'] + 1
        sb_patch("users", f"id=eq.{uid}", {"balance": nb, "total_watched": nw})
        if data.get('ad_id'):
            ads = sb_get("ads", f"id=eq.{data['ad_id']}")
            if ads:
                sb_patch("ads", f"id=eq.{data['ad_id']}", {"views_done": ads[0]['views_done'] + 1})
        return jsonify({"balance": nb, "total_watched": nw})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ads', methods=['GET'])
def get_ads():
    try:
        ads = sb_get("ads", "status=eq.active&paid=eq.true")
        active = [a for a in ads if a.get('views_done', 0) < a.get('views_ordered', 0)] if ads else []
        return jsonify(active)
    except:
        return jsonify([])

@app.route('/api/ads/create', methods=['POST'])
def create_ad():
    try:
        data = request.json
        ad = sb_post("ads", {"title": data.get("title"), "description": data.get("description", ""), "link": data.get("link"), "media_url": data.get("media_url", ""), "media_type": data.get("media_type", "text"), "views_ordered": data.get("views_ordered", 100), "price_paid": data.get("price_paid", 0), "status": "active", "paid": False, "views_done": 0})
        return jsonify(ad[0] if isinstance(ad, list) else ad)
    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

@app.route('/api/create_invoice', methods=['POST'])
def create_invoice():
    try:
        data = request.json
        ad_id = data.get('ad_id')
        amount = data.get('amount')
        r = requests.post(f"{CRYPTO_API}/createInvoice", headers={"Crypto-Pay-API-Token": CRYPTO_BOT_TOKEN}, json={"asset": "TON", "amount": str(amount), "description": f"InsiderAd #{ad_id}", "hidden_message": "Reklama zapuschena!", "paid_btn_name": "callback", "paid_btn_url": f"https://insiderad.vercel.app/api/check_payment?ad_id={ad_id}", "payload": str(ad_id)})
        res = r.json()
        if res.get("ok"):
            inv = res["result"]
            sb_patch("ads", f"id=eq.{ad_id}", {"invoice_id": str(inv["invoice_id"])})
            return jsonify({"pay_url": inv["pay_url"], "invoice_id": inv["invoice_id"]})
        return jsonify({"error": "invoice failed", "detail": res}), 500
    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

@app.route('/api/check_payment', methods=['GET'])
def check_payment():
    try:
        ad_id = request.args.get('ad_id')
        ads = sb_get("ads", f"id=eq.{ad_id}")
        if not ads:
            return jsonify({"error": "not found"}), 404
        ad = ads[0]
        inv_id = ad.get('invoice_id')
        if not inv_id:
            return jsonify({"paid": False})
        r = requests.get(f"{CRYPTO_API}/getInvoices", headers={"Crypto-Pay-API-Token": CRYPTO_BOT_TOKEN}, params={"invoice_ids": str(inv_id)})
        res = r.json()
        if res.get("ok") and res["result"]["items"]:
            if res["result"]["items"][0]["status"] == "paid":
                sb_patch("ads", f"id=eq.{ad_id}", {"paid": True})
                return jsonify({"paid": True})
        return jsonify({"paid": False})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_media():
    try:
        data = request.json
        file_data = data.get('file_data')
        file_name = data.get('file_name', f'{uuid.uuid4().hex}.jpg')
        content_type = data.get('content_type', 'image/jpeg')
        file_bytes = base64.b64decode(file_data)
        path = f"ads/{uuid.uuid4().hex}_{file_name}"
        r = requests.post(f"{SB_URL}/storage/v1/object/media/{path}", headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}", "Content-Type": content_type}, data=file_bytes)
        if r.status_code in [200, 201]:
            return jsonify({"url": f"{SB_URL}/storage/v1/object/public/media/{path}"})
        return jsonify({"error": "upload failed"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/withdraw', methods=['POST'])
def api_withdraw():
    try:
        data = request.json
        uid = data.get('user_id')
        wallet = data.get('wallet_address')
        users = sb_get("users", f"id=eq.{uid}")
        u = users[0]
        amt = float(u['balance'])
        if amt < 1.5:
            return jsonify({"error": "min 1.5"}), 400
        sb_post("withdrawals", {"user_id": uid, "amount": amt, "wallet_address": wallet})
        sb_patch("users", f"id=eq.{uid}", {"balance": 0})
        return jsonify({"success": True, "amount": amt})
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
