from flask import Flask, request, jsonify
from supabase import create_client
import os

app = Flask(__name__)

# Supabase
SUPABASE_URL = "https://kjschhxyiobwlrpeoqwp.supabase.co"
SUPABASE_KEY = "sb_publishable_lhTbA9PwffdfBsLmBzfCjQ_qlUW82MM"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

WALLET = "UQBBklp5lYFEgYig5200TPsLjtDOnAUUGToyiFhzI6D0tP8d"

# === API ===
@app.route('/api/user', methods=['POST'])
def get_or_create_user():
    data = request.json
    tg_id = data.get('telegram_id')
    username = data.get('username', '')
    
    res = supabase.table('users').select('*').eq('telegram_id', tg_id).execute()
    if res.data:
        return jsonify(res.data[0])
    
    new = supabase.table('users').insert({
        'telegram_id': tg_id,
        'username': username,
        'balance': 0,
        'total_watched': 0
    }).execute()
    return jsonify(new.data[0])

@app.route('/api/watch', methods=['POST'])
def watch_ad():
    data = request.json
    user_id = data.get('user_id')
    ad_id = data.get('ad_id')
    
    supabase.table('views').insert({
        'user_id': user_id,
        'ad_id': ad_id,
        'reward': 0.04
    }).execute()
    
    user = supabase.table('users').select('*').eq('id', user_id).execute().data[0]
    new_bal = float(user['balance']) + 0.04
    new_watched = user['total_watched'] + 1
    
    supabase.table('users').update({
        'balance': new_bal,
        'total_watched': new_watched
    }).eq('id', user_id).execute()
    
    if ad_id:
        ad = supabase.table('ads').select('*').eq('id', ad_id).execute().data
        if ad:
            supabase.table('ads').update({
                'views_done': ad[0]['views_done'] + 1
            }).eq('id', ad_id).execute()
    
    return jsonify({'balance': new_bal, 'total_watched': new_watched})

@app.route('/api/ads', methods=['GET'])
def get_ads():
    res = supabase.table('ads').select('*').eq('status', 'active').execute()
    return jsonify(res.data)

@app.route('/api/ads', methods=['POST'])
def create_ad():
    data = request.json
    new = supabase.table('ads').insert({
        'advertiser_id': data.get('advertiser_id'),
        'title': data.get('title'),
        'description': data.get('description'),
        'link': data.get('link'),
        'media_url': data.get('media_url'),
        'media_type': data.get('media_type'),
        'views_ordered': data.get('views_ordered', 100),
        'price_paid': data.get('price_paid')
    }).execute()
    return jsonify(new.data[0])

@app.route('/api/withdraw', methods=['POST'])
def withdraw():
    data = request.json
    user_id = data.get('user_id')
    wallet = data.get('wallet_address')
    
    user = supabase.table('users').select('*').eq('id', user_id).execute().data[0]
    amount = float(user['balance'])
    
    if amount < 1.5:
        return jsonify({'error': 'Minimum 1.5 TON'}), 400
    
    supabase.table('withdrawals').insert({
        'user_id': user_id,
        'amount': amount,
        'wallet_address': wallet
    }).execute()
    
    supabase.table('users').update({'balance': 0}).eq('id', user_id).execute()
    
    return jsonify({'success': True, 'amount': amount})

@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>InsiderAd</title>
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,sans-serif;background:#0a1628;color:#fff;min-height:100vh}
.hidden{display:none!important}
.role-screen{display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:100vh;padding:20px}
.role-logo{font-size:64px;margin-bottom:12px}
.role-title{font-size:32px;font-weight:800;color:#4a9eff}
.role-sub{font-size:14px;opacity:.4;margin:6px 0 50px}
.role-btn{width:100%;max-width:320px;padding:20px;border:none;border-radius:16px;font-size:17px;font-weight:700;cursor:pointer;margin-bottom:14px;display:flex;align-items:center;justify-content:center;gap:12px}
.rv{background:#0d2744;color:#4a9eff;border:1px solid #1e4976}
.ra{background:#1a1508;color:#f5a623;border:1px solid #4a3510}
.vscreen{display:none;min-height:100vh;padding-bottom:70px}
.vhdr{background:#0d2744;padding:16px 20px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #1e4976}
.vhdr-t{font-size:18px;font-weight:700;color:#4a9eff}
.vbal{background:rgba(74,158,255,.15);padding:6px 14px;border-radius:20px;font-size:14px;font-weight:600;color:#4a9eff
