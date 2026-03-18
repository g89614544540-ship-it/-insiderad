from flask import Flask, request, jsonify
import json
import os
import random
import time

app = Flask(__name__)

# ===== КОНФИГУРАЦИЯ =====
BOT_TOKEN = "8734788678:AAHNXaFd7VZsQtITaXblhJTyBRs6bVRkLfE"
BOT_USERNAME = "mytonads_bot"
PLATFORM_WALLET = "UQBBklp5lYFEgYig5200TPsLjtDOnAUUGToyiFhzI6D0tP8d"
PRICE_PER_100_VIEWS = 5  # TON
VIEWER_REWARD = 0.04  # TON за просмотр
COMMISSION = 0.20  # 20%
MIN_WITHDRAWAL = 1.5  # TON
CAPTCHA_MIN = 5
CAPTCHA_MAX = 13
CAPTCHA_NUMBER = 4
CAPTCHA_TIME = 7  # секунд

# ===== БАЗА ДАННЫХ (временная) =====
users = {}
ads = []

@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>InsiderAd</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f0f1a;
            color: #ffffff;
            min-height: 100vh;
            overflow-x: hidden;
        }

        /* ===== ЭКРАН ВЫБОРА РОЛИ ===== */
        .role-screen {
            display: flex; flex-direction: column;
            align-items: center; justify-content: center;
            min-height: 100vh; padding: 20px;
        }
        .role-logo { font-size: 60px; margin-bottom: 10px; }
        .role-title { font-size: 28px; font-weight: 800; margin-bottom: 5px; }
        .role-sub { font-size: 14px; opacity: 0.5; margin-bottom: 40px; }
        .role-btn {
            width: 100%; max-width: 320px; padding: 18px;
            border: none; border-radius: 16px;
            font-size: 17px; font-weight: 700;
            cursor: pointer; margin-bottom: 12px;
            display: flex; align-items: center; justify-content: center; gap: 10px;
        }
        .role-viewer {
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            color: white;
        }
        .role-advertiser {
            background: linear-gradient(135deg, #f59e0b, #ef4444);
            color: white;
        }

        /* ===== ЭКРАН ЗРИТЕЛЯ ===== */
        .viewer-screen { display: none; min-height: 100vh; }
        .viewer-header {
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            padding: 16px 20px;
            display: flex; justify-content: space-between; align-items: center;
        }
        .viewer-balance {
            background: rgba(255,255,255,0.15);
            padding: 6px 14px; border-radius: 20px;
            font-size: 14px; font-weight: 600;
        }
        .viewer-header-title { font-size: 18px; font-weight: 700; }
        .ad-container {
            padding: 20px; display: flex; flex-direction: column;
            align-items: center; justify-content: center;
            min-height: calc(100vh - 140px);
        }
        .ad-card {
            background: #1a1a2e; border-radius: 16px;
            padding: 24px; width: 100%; max-width: 400px;
            text-align: center;
        }
        .ad-card h3 { font-size: 20px; margin-bottom: 12px; }
        .ad-card p { font-size: 14px; opacity: 0.7; line-height: 1.5; margin-bottom: 20px; }
        .ad-timer {
            font-size: 48px; font-weight: 800;
            color: #6366f1; margin: 20px 0;
        }
        .ad-progress {
            width: 100%; height: 4px;
            background: #2a2a3e; border-radius: 2px;
            margin-bottom: 20px; overflow: hidden;
        }
        .ad-progress-bar {
            height: 100%; background: linear-gradient(90deg, #6366f1, #8b5cf6);
            border-radius: 2px; transition: width 1s linear;
        }
        .ad-reward {
            font-size: 14px; color: #6366f1;
            font-weight: 600; margin-bottom: 16px;
        }
        .btn-watched {
            width: 100%; padding: 16px; border: none;
            border-radius: 12px; font-size: 16px; font-weight: 700;
            cursor: pointer; color: white;
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
        }
        .btn-watched:disabled {
            background: #2a2a3e; color: #555; cursor: not-allowed;
        }
        .ad-count {
            font-size: 12px; opacity: 0.4; margin-top: 12px;
        }

        /* ===== КАПЧА ===== */
        .captcha-overlay {
            display: none; position: fixed; top: 0; left: 0;
            width: 100%; height: 100%;
            background: rgba(0,0,0,0.95);
            z-index: 1000; align-items: center; justify-content: center;
            flex-direction: column;
        }
        .captcha-overlay.show { display: flex; }
        .captcha-title { font-size: 24px; font-weight: 800; margin-bottom: 10px; color: #ef4444; }
        .captcha-text { font-size: 16px; margin-bottom: 20px; opacity: 0.7; }
        .captcha-timer { font-size: 60px; font-weight: 800; color: #ef4444; margin-bottom: 20px; }
        .captcha-input {
            width: 120px; height: 60px; text-align: center;
            font-size: 32px; font-weight: 800;
            background: #1a1a2e; border: 2px solid #6366f1;
            border-radius: 12px; color: white; outline: none;
        }
        .captcha-hint { font-size: 14px; opacity: 0.5; margin-top: 12px; }

        /* ===== ЭКРАН РЕКЛАМОДАТЕЛЯ ===== */
        .adv-screen { display: none; min-height: 100vh; }
        .adv-header {
            background: linear-gradient(135deg, #f59e0b, #ef4444);
            padding: 16px 20px;
            display: flex; justify-content: space-between; align-items: center;
        }
        .adv-header-title { font-size: 18px; font-weight: 700; }
        .adv-balance {
            background: rgba(255,255,255,0.15);
            padding: 6px 14px; border-radius: 20px;
            font-size: 14px; font-weight: 600;
        }
        .adv-tabs {
            display: flex; background: #1a1a2e;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        .adv-tab {
            flex: 1; padding: 12px; text-align: center;
            font-size: 12px; cursor: pointer; border: none;
            background: none; color: white; opacity: 0.5;
        }
        .adv-tab.active { opacity: 1; border-bottom: 2px solid #f59e0b; }
        .adv-content { padding: 16px; }
        .adv-card {
            background: #1a1a2e; border-radius: 12px;
            padding: 16px; margin-bottom: 12px;
        }
        .input-group { margin-bottom: 16px; }
        .input-group label {
            display: block; font-size: 13px;
            opacity: 0.6; margin-bottom: 6px;
        }
        .input-group input, .input-group textarea {
            width: 100%; padding: 12px;
            background: #0f0f1a; border: 1px solid #2a2a3e;
            border-radius: 10px; color: white;
            font-size: 15px; outline: none;
        }
        .input-group textarea { height: 80px; resize: none; }
        .price-display {
            background: #0f0f1a; border-radius: 10px;
            padding: 16px; text-align: center; margin: 16px 0;
        }
        .price-display .amount { font-size: 28px; font-weight: 800; color: #f59e0b; }
        .price-display .label { font-size: 12px; opacity: 0.5; margin-top: 4px; }
        .btn-create {
            width: 100%; padding: 16px; border: none;
            border-radius: 12px; font-size: 16px; font-weight: 700;
            cursor: pointer; color: white;
            background: linear-gradient(135deg, #f59e0b, #ef4444);
        }

        /* ===== КОШЕЛЁК ===== */
        .wallet-card {
            background: #1a1a2e; border-radius: 16px;
            padding: 24px; text-align: center; margin-bottom: 16px;
        }
        .wallet-amount { font-size: 36px; font-weight: 800; margin: 8px 0; }
        .wallet-label { font-size: 13px; opacity: 0.5; }
        .btn-withdraw {
            width: 100%; padding: 16px; border: none;
            border-radius: 12px; font-size: 16px; font-weight: 700;
            cursor: pointer; color: white;
            background: linear-gradient(135deg, #10b981, #059669);
        }
        .btn-withdraw:disabled { background: #2a2a3e; color: #555; }
        .withdraw-info { font-size: 12px; opacity: 0.4; text-align: center; margin-top: 8px; }

        /* ===== НАВБАР ===== */
        .bottom-nav {
            position: fixed; bottom: 0; left: 0; width: 100%;
            background: #1a1a2e; display: flex;
            border-top: 1px solid rgba(255,255,255,0.05);
            padding: 8px 0; padding-bottom: max(8px, env(safe-area-inset-bottom));
        }
        .nav-item {
            flex: 1; text-align: center; padding: 8px;
            font-size: 11px; opacity: 0.5; cursor: pointer;
            background: none; border: none; color: white;
        }
        .nav-item.active { opacity: 1; }
        .nav-icon { font-size: 20px; margin-bottom: 2px; }

        .hidden { display: none !important; }
        .no-ads { text-align: center; padding: 40px 20px; opacity: 0.4; }
    </style>
</head>
<body>

<!-- ===== ЭКРАН ВЫБОРА РОЛИ ===== -->
<div id="roleScreen" class="role-screen">
    <div class="role-logo">💎</div>
    <div class="role-title">InsiderAd</div>
    <div class="role-sub">Рекламная биржа Telegram</div>
    <button class="role-btn role-viewer" onclick="selectRole('viewer')">
        👁 Смотреть рекламу
    </button>
    <button class="role-btn role-advertiser" onclick="selectRole('advertiser')">
        📢 Разместить рекламу
    </button>
</div>

<!-- ===== ЭКРАН ЗРИТЕЛЯ ===== -->
<div id="viewerScreen" class="viewer-screen">
    <div class="viewer-header">
        <div class="viewer-header-title">👁 InsiderAd</div>
        <div class="viewer-balance">💎 <span id="viewerBalance">0.00</span> TON</div>
    </div>

    <div id="viewerContent">
        <!-- Просмотр рекламы -->
        <div id="adView" class="ad-container">
            <div class="ad-card">
                <h3 id="adTitle">Загрузка рекламы...</h3>
                <p id="adText">Подождите</p>
                <div class="ad-timer" id="adTimer">15</div>
                <div class="ad-progress">
                    <div class="ad-progress-bar" id="adProgressBar" style="width: 0%"></div>
                </div>
                <div class="ad-reward">+0.04 TON за просмотр</div>
                <button class="btn-watched" id="btnWatched" disabled onclick="adWatched()">
                    Подождите...
                </button>
                <div class="ad-count">Просмотрено: <span id="adCount">0</span></div>
            </div>
        </div>

        <!-- Нет рекламы -->
        <div id="noAds" class="ad-container hidden">
            <div class="no-ads">
                <div style="font-size:60px; margin-bottom:16px;">📭</div>
                <h3>Нет доступной рекламы</h3>
                <p style="margin-top:8px;">Зайдите позже</p>
            </div>
        </div>
    </div>

    <!-- Кошелёк зрителя -->
    <div id="viewerWallet" class="ad-container hidden">
        <div class="wallet-card">
            <div class="wallet-label">Ваш баланс</div>
            <div class="wallet-amount">💎 <span id="walletBalance">0.00</span> TON</div>
        </div>
        <button class="btn-withdraw" id="btnWithdraw" disabled onclick="withdraw()">
            Вывести TON
        </button>
        <div class="withdraw-info">Минимум для вывода: 1.5 TON</div>
    </div>

    <div class="bottom-nav">
        <button class="nav-item active" onclick="showViewerTab('ads')">
            <div class="nav-icon">👁</div>Реклама
        </button>
        <button class="nav-item" onclick="showViewerTab('wallet')">
            <div class="nav-icon">💎</div>Кошелёк
        </button>
    </div>
</div>

<!-- ===== ЭКРАН РЕКЛАМОДАТЕЛЯ ===== -->
<div id="advScreen" class="adv-screen">
    <div class="adv-header">
        <div class="adv-header-title">📢 InsiderAd</div>
        <div class="adv-balance">💎 <span id="advBalance">0.00</span> TON</div>
    </div>

    <div class="adv-tabs">
        <button class="adv-tab active" onclick="showAdvTab('create')">➕ Создать</button>
        <button class="adv-tab" onclick="showAdvTab('myads')">📊 Мои заказы</button>
        <button class="adv-tab" onclick="showAdvTab('advwallet')">💎 Кошелёк</button>
    </div>

    <!-- Создать рекламу -->
    <div id="advCreate" class="adv-content">
        <div class="adv-card">
            <div class="input-group">
                <label>Заголовок рекламы</label>
                <input type="text" id="adTitleInput" placeholder="Например: Крипто канал">
            </div>
            <div class="input-group">
                <label>Текст рекламы</label>
                <textarea id="adTextInput" placeholder="Описание вашего канала или продукта"></textarea>
            </div>
            <div class="input-group">
                <label>Ссылка</label>
                <input type="text" id="adLinkInput" placeholder="https://t.me/yourchannel">
            </div>
            <div class="input-group">
                <label>Количество просмотров (минимум 100)</label>
                <input type="number" id="adViewsInput" min="100" value="100" oninput="calcPrice()">
            </div>
            <div class="price-display">
                <div class="amount" id="priceAmount">5.00 TON</div>
                <div class="label">Стоимость рекламы</div>
            </div>
            <button class="btn-create" onclick="createAd()">Оплатить и запустить</button>
        </div>
    </div>

    <!-- Мои заказы -->
    <div id="advMyAds" class="adv-content hidden">
        <div class="adv-card">
            <p style="text-align:center; padding:20px; opacity:0.4;">У вас пока нет заказов</p>
        </div>
    </div>

    <!-- Кошелёк рекламодателя -->
    <div id="advWallet" class="adv-content hidden">
        <div class="wallet-card">
            <div class="wallet-label">Баланс рекламодателя</div>
            <div class="wallet-amount">💎 <span id="advWalletBalance">0.00</span> TON</div>
        </div>
        <button class="btn-create" onclick="depositTON()">Пополнить через TON</button>
    </div>
</div>

<!-- ===== КАПЧА ===== -->
<div id="captchaOverlay" class="captcha-overlay">
    <div class="captcha-title">⚠️ КАПЧА</div>
    <div class="captcha-text">Введите число 4</div>
    <div class="captcha-timer" id="captchaTimer">7</div>
    <input type="number" class="captcha-input" id="captchaInput" maxlength="1" oninput="checkCaptcha()">
    <div class="captcha-hint">У вас 7 секунд!</div>
</div>

<script>
    // ===== TELEGRAM WEB APP =====
    const tg = window.Telegram.WebApp;
    tg.ready();
    tg.expand();

    // ===== СОСТОЯНИЕ =====
    let state = {
        role: null,
        balance: 0,
        adsWatched: 0,
        totalAdsWatched: 0,
        nextCaptcha: getRandomCaptcha(),
        timerInterval: null,
        currentAdTime: 15,
        advBalance: 0
    };

    function getRandomCaptcha() {
        return Math.floor(Math.random() * (13 - 5 + 1)) + 5;
    }

    // ===== ВЫБОР РОЛИ =====
    function selectRole(role) {
        state.role = role;
        document.getElementById('roleScreen').style.display = 'none';
        if (role === 'viewer') {
            document.getElementById('viewerScreen').style.display = 'block';
            loadAd();
        } else {
            document.getElementById('advScreen').style.display = 'block';
        }
    }

    // ===== ЗРИТЕЛЬ: ЗАГРУЗКА РЕКЛАМЫ =====
    function loadAd() {
        // Демо реклама
        const demoAds = [
            { title: "🚀 Крипто Сигналы", text: "Лучший канал с сигналами для трейдинга. Бесплатные прогнозы каждый день!", link: "https://t.me/example1" },
            { title: "💰 Бизнес Инсайды", text: "Узнай как зарабатывать на крипте. Секретные стратегии от профи!", link: "https://t.me/example2" },
            { title: "🎮 GameZone", text: "Лучшие игры, обзоры и розыгрыши. Вступай в наше комьюнити!", link: "https://t.me/example3" },
            { title: "📈 TON Новости", text: "Все о блокчейне TON. Новости, аналитика, обновления.", link: "https://t.me/example4" },
        ];

        const ad = demoAds[Math.floor(Math.random() * demoAds.length)];
        document.getElementById('adTitle').textContent = ad.title;
        document.getElementById('adText').textContent = ad.text;

        // Сброс таймера
        state.currentAdTime = 15;
        document.getElementById('adTimer').textContent = '15';
        document.getElementById('adProgressBar').style.width = '0%';
        document.getElementById('btnWatched').disabled = true;
        document.getElementById('btnWatched').textContent = 'Подождите... 15 сек';

        clearInterval(state.timerInterval);
        state.timerInterval = setInterval(() => {
            state.currentAdTime--;
            document.getElementById('adTimer').textContent = state.currentAdTime;
            const progress = ((15 - state.currentAdTime) / 15) * 100;
            document.getElementById('adProgressBar').style.width = progress + '%';
            document.getElementById('btnWatched').textContent = 'Подождите... ' + state.currentAdTime + ' сек';

            if (state.currentAdTime <= 0) {
                clearInterval(state.timerInterval);
                document.getElementById('btnWatched').disabled = false;
                document.getElementById('btnWatched').textContent = '✅ Получить 0.04 TON';
            }
        }, 1000);
    }

    // ===== ЗРИТЕЛЬ: ПРОСМОТРЕНА =====
    function adWatched() {
        state.balance += 0.04;
        state.adsWatched++;
        state.totalAdsWatched++;

        updateViewerUI();

        // Проверка капчи
        if (state.adsWatched >= state.nextCaptcha) {
            showCaptcha();
            return;
        }

        loadAd();
    }

    // ===== КАПЧА =====
    function showCaptcha() {
        document.getElementById('captchaOverlay').classList.add('show');
        document.getElementById('captchaInput').value = '';
        document.getElementById('captchaInput').focus();

        let captchaTime = 7;
        document.getElementById('captchaTimer').textContent = captchaTime;

        clearInterval(state.timerInterval);
        state.timerInterval = setInterval(() => {
            captchaTime--;
            document.getElementById('captchaTimer').textContent = captchaTime;

            if (captchaTime <= 0) {
                clearInterval(state.timerInterval);
                captchaFailed();
            }
        }, 1000);
    }

    function checkCaptcha() {
        const val = document.getElementById('captchaInput').value;
        if (val === '4') {
            clearInterval(state.timerInterval);
            captchaPassed();
        }
    }

    function captchaPassed() {
        document.getElementById('captchaOverlay').classList.remove('show');
        state.adsWatched = 0;
        state.nextCaptcha = getRandomCaptcha();
        loadAd();
    }

    function captchaFailed() {
        document.getElementById('captchaOverlay').classList.remove('show');
        state.balance = 0;
        state.adsWatched = 0;
        state.nextCaptcha = getRandomCaptcha();
        updateViewerUI();

        alert('⏰ Время вышло! Баланс сгорел!');
        loadAd();
    }

    // ===== ЗРИТЕЛЬ: UI =====
    function updateViewerUI() {
        document.getElementById('viewerBalance').textContent = state.balance.toFixed(2);
        document.getElementById('walletBalance').textContent = state.balance.toFixed(2);
        document.getElementById('adCount').textContent = state.totalAdsWatched;

        const btnWithdraw = document.getElementById('btnWithdraw');
        if (state.balance >= 1.5) {
            btnWithdraw.disabled = false;
            btnWithdraw.textContent = 'Вывести ' + state.balance.toFixed(2) + ' TON';
        } else {
            btnWithdraw.disabled = true;
            btnWithdraw.textContent = 'Минимум 1.5 TON (сейчас ' + state.balance.toFixed(2) + ')';
        }
    }

    function showViewerTab(tab) {
        document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
        event.target.closest('.nav-item').classList.add('active');

        if (tab === 'ads') {
            document.getElementById('viewerContent').classList.remove('hidden');
            document.getElementById('viewerWallet').classList.add('hidden');
        } else {
            document.getElementById('viewerContent').classList.add('hidden');
            document.getElementById('viewerWallet').classList.remove('hidden');
            updateViewerUI();
        }
    }

    // ===== ВЫВОД =====
    function withdraw() {
        if (state.balance >= 1.5) {
            alert('Заявка на вывод ' + state.balance.toFixed(2) + ' TON отправлена!\\nАдрес: подключите TON кошелёк');
            state.balance = 0;
            updateViewerUI();
        }
    }

    // ===== РЕКЛАМОДАТЕЛЬ =====
    function calcPrice() {
        const views = Math.max(100, parseInt(document.getElementById('adViewsInput').value) || 100);
        const price = (views / 100) * 5;
        document.getElementById('priceAmount').textContent = price.toFixed(2) + ' TON';
    }

    function showAdvTab(tab) {
        document.querySelectorAll('.adv-tab').forEach(t => t.classList.remove('active'));
        event.target.classList.add('active');

        document.getElementById('advCreate').classList.add('hidden');
        document.getElementById('advMyAds').classList.add('hidden');
        document.getElementById('advWallet').classList.add('hidden');

        if (tab === 'create') document.getElementById('advCreate').classList.remove('hidden');
        if (tab === 'myads') document.getElementById('advMyAds').classList.remove('hidden');
        if (tab === 'advwallet') document.getElementById('advWallet').classList.remove('hidden');
    }

    function createAd() {
        const title = document.getElementById('adTitleInput').value;
        const text = document.getElementById('adTextInput').value;
        const views = parseInt(document.getElementById('adViewsInput').value);

        if (!title || !text) {
            alert('Заполните все поля!');
            return;
        }

        const price = (views / 100) * 5;
        alert('Оплатите ' + price.toFixed(2) + ' TON для запуска рекламы\\n\\nАдрес: ''' + PLATFORM_WALLET + '''');
    }

    function depositTON() {
        alert('Отправьте TON на адрес:\\n''' + PLATFORM_WALLET + '''');
    }

    const PLATFORM_WALLET = "UQBBklp5lYFEgYig5200TPsLjtDOnAUUGToyiFhzI6D0tP8d";
</script>
</body>
</html>'''


@app.route('/api/health')
def health():
    return jsonify({"status": "healthy"})


if __name__ == '__main__':
    app.run(debug=True)
