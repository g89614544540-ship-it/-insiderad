from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

CRYPTO_BOT_TOKEN = "552796:AAJmyEgL1NMBR1WROTDN1fWRW4nOHG8le9O"
CRYPTO_API_URL = f"https://cryptobot.org/api/v1/{CRYPTO_BOT_TOKEN}"

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

def sb_post(table, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    return response.json()

@app.route('/api/create_invoice', methods=['POST'])
def create_invoice():
    content = request.json
    # Здесь должна быть логика создания счёта через CryptoBot API
    # Для примера возвращаем заглушку:
    return jsonify({"ok": True, "invoice_id": "test123"})

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
