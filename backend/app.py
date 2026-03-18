from flask import Flask, jsonify

app = Flask(__name__)

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
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--tg-theme-bg-color, #1a1a2e);
            color: var(--tg-theme-text-color, #ffffff);
            min-height: 100vh;
        }
        .header {
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            padding: 20px;
            text-align: center;
        }
        .header h1 { font-size: 24px; margin-bottom: 5px; }
        .header p { font-size: 14px; opacity: 0.8; }
        .tabs {
            display: flex;
            background: var(--tg-theme-secondary-bg-color, #16213e);
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .tab {
            flex: 1; padding: 12px; text-align: center;
            font-size: 13px; cursor: pointer; border: none;
            background: none; color: var(--tg-theme-text-color, #fff);
            opacity: 0.6; transition: 0.3s;
        }
        .tab.active { opacity: 1; border-bottom: 2px solid #6366f1; }
        .content { padding: 16px; }
        .card {
            background: var(--tg-theme-secondary-bg-color, #16213e);
            border-radius: 12px; padding: 16px; margin-bottom: 12px;
        }
        .card h3 { font-size: 16px; margin-bottom: 8px; }
        .card p { font-size: 13px; opacity: 0.7; }
        .stats { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px; }
        .stat-card {
            background: var(--tg-theme-secondary-bg-color, #16213e);
            border-radius: 12px; padding: 16px; text-align: center;
        }
        .stat-card .number { font-size: 24px; font-weight: bold; color: #6366f1; }
        .stat-card .label { font-size: 12px; opacity: 0.6; margin-top: 4px; }
        .btn {
            width: 100%; padding: 14px; border: none; border-radius: 12px;
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            color: white; font-size: 16px; font-weight: 600;
            cursor: pointer; margin-top: 12px;
        }
        .channel-item {
            display: flex; justify-content: space-between;
            align-items: center; padding: 12px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        .channel-name { font-weight: 600; }
        .channel-subs { font-size: 13px; opacity: 0.6; }
        .channel-price { color: #6366f1; font-weight: 600; }
        .section-title { font-size: 18px; font-weight: 700; margin-bottom: 12px; }
        .hidden { display: none; }
        .ton-icon { color: #0098EA; }
    </style>
</head>
<body>
    <div class="header">
        <h1>💎 InsiderAd</h1>
        <p>Рекламная биржа Telegram каналов</p>
    </div>

    <div class="tabs">
        <button class="tab active" onclick="showTab('market')">📢 Биржа</button>
        <button class="tab" onclick="showTab('my-ads')">📊 Мои заказы</button>
        <button class="tab" onclick="showTab('my-channels')">📡 Каналы</button>
        <button class="tab" onclick="showTab('wallet')">💎 Кошелёк</button>
    </div>

    <div id="market" class="content">
        <div class="stats">
            <div class="stat-card">
                <div class="number">1,247</div>
                <div class="label">Каналов</div>
            </div>
            <div class="stat-card">
                <div class="number">89M</div>
                <div class="label">Охват</div>
            </div>
        </div>
        <div class="section-title">🔥 Популярные каналы</div>
        <div class="card">
            <div class="channel-item">
                <div><div class="channel-name">Крипто Новости</div><div class="channel-subs">125K подписчиков</div></div>
                <div class="channel-price">💎 5.2 TON</div>
            </div>
            <div class="channel-item">
                <div><div class="channel-name">Tech Insider</div><div class="channel-subs">89K подписчиков</div></div>
                <div class="channel-price">💎 3.8 TON</div>
            </div>
            <div class="channel-item">
                <div><div class="channel-name">Бизнес Канал</div><div class="channel-subs">210K подписчиков</div></div>
                <div class="channel-price">💎 8.5 TON</div>
            </div>
            <div class="channel-item">
                <div><div class="channel-name">Маркетинг PRO</div><div class="channel-subs">67K подписчиков</div></div>
                <div class="channel-price">💎 2.1 TON</div>
            </div>
        </div>
        <button class="btn">Разместить рекламу</button>
    </div>

    <div id="my-ads" class="content hidden">
        <div class="section-title">📊 Мои рекламные заказы</div>
        <div class="card">
            <p style="text-align:center; padding: 20px; opacity: 0.5;">У вас пока нет заказов</p>
        </div>
        <button class="btn">Создать рекламу</button>
    </div>

    <div id="my-channels" class="content hidden">
        <div class="section-title">📡 Мои каналы</div>
        <div class="card">
            <p style="text-align:center; padding: 20px; opacity: 0.5;">Добавьте свой канал для заработка</p>
        </div>
        <button class="btn">+ Добавить канал</button>
    </div>

    <div id="wallet" class="content hidden">
        <div class="card" style="text-align:center;">
            <p style="opacity:0.6;">Баланс</p>
            <div style="font-size:36px; font-weight:bold; margin:12px 0;">💎 0.00 TON</div>
            <p style="opacity:0.5; font-size:13px;">≈ $0.00</p>
        </div>
        <div style="display:flex; gap:12px;">
            <button class="btn" style="flex:1;">Пополнить</button>
            <button class="btn" style="flex:1; background: linear-gradient(135deg, #374151, #4b5563);">Вывести</button>
        </div>
    </div>

    <script>
        const tg = window.Telegram.WebApp;
        tg.ready();
        tg.expand();

        function showTab(tabId) {
            document.querySelectorAll('.content').forEach(c => c.classList.add('hidden'));
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.getElementById(tabId).classList.remove('hidden');
            event.target.classList.add('active');
        }
    </script>
</body>
</html>'''

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(debug=True)
