from flask import Flask, request, jsonify

app = Flask(__name__)

PLATFORM_WALLET = "UQBBklp5lYFEgYig5200TPsLjtDOnAUUGToyiFhzI6D0tP8d"

@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>InsiderAd</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <script src="https://unpkg.com/@tonconnect/sdk@latest/dist/tonconnect-sdk.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a1628;
            color: #ffffff;
            min-height: 100vh;
            overflow-x: hidden;
        }

        /* ===== ЭКРАН ВЫБОРА РОЛИ ===== */
        .role-screen {
            display: flex; flex-direction: column;
            align-items: center; justify-content: center;
            min-height: 100vh; padding: 20px;
            background: linear-gradient(180deg, #0d1f3c 0%, #0a1628 100%);
        }
        .role-logo { font-size: 64px; margin-bottom: 12px; }
        .role-title {
            font-size: 32px; font-weight: 800;
            background: linear-gradient(135deg, #4a9eff, #0066cc);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        .role-sub { font-size: 14px; opacity: 0.4; margin-top: 6px; margin-bottom: 50px; }
        .role-btn {
            width: 100%; max-width: 320px; padding: 20px;
            border: none; border-radius: 16px;
            font-size: 17px; font-weight: 700;
            cursor: pointer; margin-bottom: 14px;
            display: flex; align-items: center; justify-content: center; gap: 12px;
            transition: transform 0.2s;
        }
        .role-btn:active { transform: scale(0.97); }
        .role-viewer {
            background: linear-gradient(135deg, #1a3a5c, #0d2744);
            color: #4a9eff; border: 1px solid #1e4976;
        }
        .role-advertiser {
            background: linear-gradient(135deg, #2d1f0e, #1a1508);
            color: #f5a623; border: 1px solid #4a3510;
        }

        /* ===== ОБЩИЕ ===== */
        .hidden { display: none !important; }

        /* ===== ЗРИТЕЛЬ ===== */
        .viewer-screen { display: none; min-height: 100vh; padding-bottom: 70px; }
        .v-header {
            background: linear-gradient(135deg, #0d2744, #1a3a5c);
            padding: 16px 20px;
            display: flex; justify-content: space-between; align-items: center;
            border-bottom: 1px solid #1e4976;
        }
        .v-header-title { font-size: 18px; font-weight: 700; color: #4a9eff; }
        .v-balance-badge {
            background: rgba(74,158,255,0.15);
            padding: 6px 14px; border-radius: 20px;
            font-size: 14px; font-weight: 600; color: #4a9eff;
        }

        /* Карточка рекламы */
        .ad-container {
            padding: 20px; display: flex; flex-direction: column;
            align-items: center; justify-content: center;
            min-height: calc(100vh - 140px);
        }
        .ad-card {
            background: #0d1f3c; border: 1px solid #1e4976;
            border-radius: 20px; padding: 20px; width: 100%;
            max-width: 400px; overflow: hidden;
        }
        .ad-media {
            width: 100%; height: 200px; border-radius: 12px;
            overflow: hidden; margin-bottom: 16px;
            background: #0a1628; display: flex;
            align-items: center; justify-content: center;
        }
        .ad-media img, .ad-media video {
            width: 100%; height: 100%; object-fit: cover;
        }
        .ad-media-placeholder {
            font-size: 48px; opacity: 0.2;
        }
        .ad-card h3 { font-size: 18px; margin-bottom: 8px; color: #ffffff; }
        .ad-card p { font-size: 14px; opacity: 0.6; line-height: 1.5; margin-bottom: 16px; }
        .ad-link {
            display: block; text-align: center; padding: 10px;
            background: rgba(74,158,255,0.1); border-radius: 10px;
            color: #4a9eff; text-decoration: none;
            font-size: 14px; font-weight: 600; margin-bottom: 16px;
        }
        .ad-timer-block { text-align: center; margin: 16px 0; }
        .ad-timer {
            font-size: 52px; font-weight: 800; color: #4a9eff;
        }
        .ad-timer-label { font-size: 12px; opacity: 0.3; margin-top: 4px; }
        .ad-progress {
            width: 100%; height: 4px;
            background: #1e4976; border-radius: 2px;
            margin: 16px 0; overflow: hidden;
        }
        .ad-progress-bar {
            height: 100%; background: linear-gradient(90deg, #0066cc, #4a9eff);
            border-radius: 2px; transition: width 1s linear; width: 0%;
        }
        .ad-reward {
            text-align: center; font-size: 14px;
            color: #4a9eff; font-weight: 600; margin-bottom: 16px;
        }
        .btn-main {
            width: 100%; padding: 16px; border: none;
            border-radius: 14px; font-size: 16px; font-weight: 700;
            cursor: pointer; color: white;
            background: linear-gradient(135deg, #0066cc, #4a9eff);
            transition: transform 0.2s;
        }
        .btn-main:active { transform: scale(0.97); }
        .btn-main:disabled {
            background: #1a2a3e; color: #3a4a5e; cursor: not-allowed;
        }
        .ad-count { font-size: 12px; opacity: 0.3; margin-top: 12px; text-align: center; }

        /* ===== КОШЕЛЁК ЗРИТЕЛЯ ===== */
        .wallet-section { padding: 20px; }
        .wallet-card {
            background: #0d1f3c; border: 1px solid #1e4976;
            border-radius: 20px; padding: 28px; text-align: center;
            margin-bottom: 16px;
        }
        .wallet-label { font-size: 13px; opacity: 0.4; }
        .wallet-amount {
            font-size: 40px; font-weight: 800;
            color: #4a9eff; margin: 8px 0;
        }
        .wallet-input-group { margin-bottom: 16px; }
        .wallet-input-group label {
            display: block; font-size: 13px;
            opacity: 0.5; margin-bottom: 6px; text-align: left;
        }
        .wallet-input {
            width: 100%; padding: 14px;
            background: #0a1628; border: 1px solid #1e4976;
            border-radius: 12px; color: white;
            font-size: 14px; outline: none;
        }
        .wallet-input:focus { border-color: #4a9eff; }
        .btn-withdraw {
            width: 100%; padding: 16px; border: none;
            border-radius: 14px; font-size: 16px; font-weight: 700;
            cursor: pointer; color: white;
            background: linear-gradient(135deg, #0a6e3a, #0d9e52);
        }
        .btn-withdraw:disabled { background: #1a2a3e; color: #3a4a5e; cursor: not-allowed; }
        .wallet-info { font-size: 12px; opacity: 0.3; text-align: center; margin-top: 10px; }

        /* ===== НАВБАР ===== */
        .bottom-nav {
            position: fixed; bottom: 0; left: 0; width: 100%;
            background: #0d1f3c; display: flex;
            border-top: 1px solid #1e4976;
            padding: 6px 0; padding-bottom: max(6px, env(safe-area-inset-bottom));
        }
        .nav-item {
            flex: 1; text-align: center; padding: 8px;
            font-size: 11px; opacity: 0.4; cursor: pointer;
            background: none; border: none; color: white;
        }
        .nav-item.active { opacity: 1; color: #4a9eff; }
        .nav-icon { font-size: 20px; margin-bottom: 2px; }

        /* ===== КАПЧА ===== */
        .captcha-overlay {
            display: none; position: fixed; top: 0; left: 0;
            width: 100%; height: 100%;
            background: rgba(5,10,20,0.97);
            z-index: 1000; align-items: center; justify-content: center;
            flex-direction: column; padding: 20px;
        }
        .captcha-overlay.show { display: flex; }
        .captcha-icon { font-size: 48px; margin-bottom: 16px; }
        .captcha-title { font-size: 22px; font-weight: 800; color: #ff4444; margin-bottom: 8px; }
        .captcha-text { font-size: 16px; opacity: 0.6; margin-bottom: 24px; }
        .captcha-timer { font-size: 64px; font-weight: 800; color: #ff4444; margin-bottom: 24px; }
        .captcha-input {
            width: 100px; height: 64px; text-align: center;
            font-size: 36px; font-weight: 800;
            background: #0d1f3c; border: 2px solid #1e4976;
            border-radius: 16px; color: white; outline: none;
        }
        .captcha-input:focus { border-color: #4a9eff; }
        .captcha-hint { font-size: 13px; opacity: 0.3; margin-top: 16px; }

        /* ===== РЕКЛАМОДАТЕЛЬ ===== */
        .adv-screen { display: none; min-height: 100vh; padding-bottom: 10px; }
        .adv-header {
            background: linear-gradient(135deg, #2d1f0e, #1a1508);
            padding: 16px 20px;
            display: flex; justify-content: space-between; align-items: center;
            border-bottom: 1px solid #4a3510;
        }
        .adv-header-title { font-size: 18px; font-weight: 700; color: #f5a623; }
        .adv-balance-badge {
            background: rgba(245,166,35,0.15);
            padding: 6px 14px; border-radius: 20px;
            font-size: 14px; font-weight: 600; color: #f5a623;
        }
        .adv-tabs {
            display: flex; background: #0d1f3c;
            border-bottom: 1px solid #1e4976;
        }
        .adv-tab {
            flex: 1; padding: 14px; text-align: center;
            font-size: 12px; cursor: pointer; border: none;
            background: none; color: white; opacity: 0.4;
            border-bottom: 2px solid transparent;
        }
        .adv-tab.active { opacity: 1; color: #f5a623; border-bottom-color: #f5a623; }
        .adv-content { padding: 16px; }
        .adv-card {
            background: #0d1f3c; border: 1px solid #1e4976;
            border-radius: 16px; padding: 20px; margin-bottom: 14px;
        }
        .input-group { margin-bottom: 16px; }
        .input-group label {
            display: block; font-size: 13px;
            opacity: 0.5; margin-bottom: 6px;
        }
        .input-group input, .input-group textarea, .input-group select {
            width: 100%; padding: 14px;
            background: #0a1628; border: 1px solid #1e4976;
            border-radius: 12px; color: white;
            font-size: 15px; outline: none;
        }
        .input-group input:focus, .input-group textarea:focus { border-color: #f5a623; }
        .input-group textarea { height: 90px; resize: none; }

        /* Загрузка медиа */
        .media-upload {
            width: 100%; height: 140px;
            border: 2px dashed #1e4976; border-radius: 12px;
            display: flex; flex-direction: column;
            align-items: center; justify-content: center;
            cursor: pointer; transition: border-color 0.3s;
        }
        .media-upload:hover { border-color: #f5a623; }
        .media-upload-icon { font-size: 36px; margin-bottom: 8px; opacity: 0.3; }
        .media-upload-text { font-size: 13px; opacity: 0.4; }
        .media-upload input { display: none; }
        .media-preview {
            width: 100%; height: 140px; border-radius: 12px;
            overflow: hidden; margin-top: 8px; display: none;
        }
        .media-preview img, .media-preview video {
            width: 100%; height: 100%; object-fit: cover;
        }

        .price-display {
            background: #0a1628; border: 1px solid #1e4976;
            border-radius: 14px; padding: 20px;
            text-align: center; margin: 16px 0;
        }
        .price-amount { font-size: 32px; font-weight: 800; color: #f5a623; }
        .price-label { font-size: 12px; opacity: 0.4; margin-top: 4px; }
        .btn-create {
            width: 100%; padding: 16px; border: none;
            border-radius: 14px; font-size: 16px; font-weight: 700;
            cursor: pointer; color: white;
            background: linear-gradient(135deg, #d4870a, #f5a623);
        }
        .btn-create:active { transform: scale(0.97); }

        /* Заказы */
        .order-card {
            background: #0d1f3c; border: 1px solid #1e4976;
            border-radius: 14px; padding: 16px; margin-bottom: 10px;
        }
        .order-title { font-size: 15px; font-weight: 700; margin-bottom: 4px; }
        .order-stats { font-size: 13px; opacity: 0.5; }
        .order-status {
            display: inline-block; padding: 4px 10px;
            border-radius: 8px; font-size: 11px; font-weight: 600;
            margin-top: 8px;
        }
        .status-active { background: rgba(74,158,255,0.15); color: #4a9eff; }
        .status-done { background: rgba(13,158,82,0.15); color: #0d9e52; }

        .no-data {
            text-align: center; padding: 40px 20px; opacity: 0.3;
        }
        .no-data-icon { font-size: 48px; margin-bottom: 12px; }

        /* ===== TON CONNECT ===== */
        .connect-btn {
            width: 100%; padding: 14px; border: none;
            border-radius: 14px; font-size: 15px; font-weight: 700;
            cursor: pointer; color: white; margin-top: 12px;
            background: linear-gradient(135deg, #0098EA, #00B2FF);
        }
    </style>
</head>
<body>

<!-- ===== ЭКРАН ВЫБОРА РОЛИ ===== -->
<div id="roleScreen" class="role-screen">
    <div class="role-logo">💎</div>
    <div class="role-title">InsiderAd</div>
    <div class="role-sub">Рекламная биржа Telegram каналов</div>
    <button class="role-btn role-viewer" onclick="selectRole('viewer')">
        👁 Смотреть рекламу и зарабатывать
    </button>
    <button class="role-btn role-advertiser" onclick="selectRole('advertiser')">
        📢 Разместить рекламу
    </button>
</div>

<!-- ===== ЗРИТЕЛЬ ===== -->
<div id="viewerScreen" class="viewer-screen">
    <div class="v-header">
        <div class="v-header-title">💎 InsiderAd</div>
        <div class="v-balance-badge">💎 <span id="vBal">0.00</span> TON</div>
    </div>

    <div id="vAdsSection">
        <div class="ad-container">
            <div class="ad-card">
                <div class="ad-media" id="adMedia">
                    <div class="ad-media-placeholder">📢</div>
                </div>
                <h3 id="adTitle">Загрузка...</h3>
                <p id="adText">Подождите</p>
                <a href="#" id="adLink" class="ad-link" target="_blank">Перейти →</a>
                <div class="ad-timer-block">
                    <div class="ad-timer" id="adTimer">15</div>
                    <div class="ad-timer-label">секунд</div>
                </div>
                <div class="ad-progress">
                    <div class="ad-progress-bar" id="adBar"></div>
                </div>
                <div class="ad-reward">💎 +0.04 TON за просмотр</div>
                <button class="btn-main" id="btnWatch" disabled onclick="adWatched()">
                    Подождите... 15 сек
                </button>
                <div class="ad-count">Просмотрено: <span id="adCount">0</span></div>
            </div>
        </div>
    </div>

    <div id="vNoAds" class="ad-container hidden">
        <div class="no-data">
            <div class="no-data-icon">📭</div>
            <p>Нет доступной рекламы</p>
        </div>
    </div>

    <div id="vWalletSection" class="wallet-section hidden">
        <div class="wallet-card">
            <div class="wallet-label">Ваш баланс</div>
            <div class="wallet-amount">💎 <span id="vWalBal">0.00</span> TON</div>
        </div>
        <div class="wallet-input-group">
            <label>Адрес TON кошелька для вывода</label>
            <input type="text" class="wallet-input" id="withdrawAddress"
                   placeholder="UQ... или EQ..." oninput="checkWithdraw()">
        </div>
        <button class="btn-withdraw" id="btnWithdraw" disabled onclick="withdraw()">
            Минимум 1.5 TON
        </button>
        <div class="wallet-info">Минимальный вывод: 1.5 TON</div>
        <button class="connect-btn" onclick="connectWallet()">
            🔗 Подключить TON кошелёк
        </button>
    </div>

    <div class="bottom-nav">
        <button class="nav-item active" id="navAds" onclick="vTab('ads')">
            <div class="nav-icon">👁</div>Реклама
        </button>
        <button class="nav-item" id="navWal" onclick="vTab('wallet')">
            <div class="nav-icon">💎</div>Кошелёк
        </button>
    </div>
</div>

<!-- ===== КАПЧА ===== -->
<div id="captchaOverlay" class="captcha-overlay">
    <div class="captcha-icon">🔒</div>
    <div class="captcha-title">ПРОВЕРКА</div>
    <div class="captcha-text">Введите число 4</div>
    <div class="captcha-timer" id="capTimer">7</div>
    <input type="number" class="captcha-input" id="capInput" oninput="checkCap()">
    <div class="captcha-hint">У вас 7 секунд. Не прошли — баланс сгорает!</div>
</div>

<!-- ===== РЕКЛАМОДАТЕЛЬ ===== -->
<div id="advScreen" class="adv-screen">
    <div class="adv-header">
        <div class="adv-header-title">📢 InsiderAd</div>
        <div class="adv-balance-badge">💎 <span id="aBal">0.00</span> TON</div>
    </div>

    <div class="adv-tabs">
        <button class="adv-tab active" id="tabCreate" onclick="aTab('create')">➕ Создать</button>
        <button class="adv-tab" id="tabOrders" onclick="aTab('orders')">📊 Заказы</button>
        <button class="adv-tab" id="tabAWallet" onclick="aTab('awallet')">💎 Кошелёк</button>
    </div>

    <!-- Создать -->
    <div id="secCreate" class="adv-content">
        <div class="adv-card">
            <div class="input-group">
                <label>Медиа (фото или видео)</label>
                <div class="media-upload" onclick="document.getElementById('mediaFile').click()">
                    <div class="media-upload-icon">📷</div>
                    <div class="media-upload-text">Нажмите для загрузки</div>
                    <input type="file" id="mediaFile" accept="image/*,video/*" onchange="previewMedia(this)">
                </div>
                <div class="media-preview" id="mediaPreview"></div>
            </div>
            <div class="input-group">
                <label>Заголовок рекламы</label>
                <input type="text" id="inTitle" placeholder="Название канала или продукта">
            </div>
            <div class="input-group">
                <label>Текст рекламы</label>
                <textarea id="inText" placeholder="Описание"></textarea>
            </div>
            <div class="input-group">
                <label>Ссылка (обязательно)</label>
                <input type="text" id="inLink" placeholder="https://t.me/yourchannel">
            </div>
            <div class="input-group">
                <label>Количество просмотров (мин. 100)</label>
                <input type="number" id="inViews" min="100" value="100" oninput="calcPrice()">
            </div>
            <div class="price-display">
                <div class="price-amount" id="priceAmt">5.00 TON</div>
                <div class="price-label">100 просмотров = 5 TON</div>
            </div>
            <button class="btn-create" onclick="createAd()">💎 Оплатить и запустить</button>
        </div>
    </div>

    <!-- Заказы -->
    <div id="secOrders" class="adv-content hidden">
        <div id="ordersList">
            <div class="no-data">
                <div class="no-data-icon">📋</div>
                <p>У вас пока нет заказов</p>
            </div>
        </div>
    </div>

    <!-- Кошелёк -->
    <div id="secAWallet" class="adv-content hidden">
        <div class="wallet-card">
            <div class="wallet-label">Баланс рекламодателя</div>
            <div class="wallet-amount">💎 <span id="aWalBal">0.00</span> TON</div>
        </div>
        <button class="connect-btn" onclick="connectWallet()">
            🔗 Подключить TON кошелёк
        </button>
    </div>
</div>

<script>
// ===== КОНФИГ =====
const WALLET = "UQBBklp5lYFEgYig5200TPsLjtDOnAUUGToyiFhzI6D0tP8d";
const REWARD = 0.04;
const MIN_WITHDRAW = 1.5;
const PRICE_100 = 5;

// ===== TELEGRAM =====
const tg = window.Telegram.WebApp;
tg.ready();
tg.expand();

// ===== СОСТОЯНИЕ =====
let S = {
    role: null,
    bal: 0,
    watched: 0,
    total: 0,
    nextCap: rndCap(),
    timer: null,
    time: 15,
    orders: [],
    mediaData: null,
    mediaType: null,
    walletConnected: false,
    walletAddress: null
};

function rndCap() { return Math.floor(Math.random() * 9) + 5; }

// ===== ДЕМО РЕКЛАМА =====
const demoAds = [
    { title: "🚀 Крипто Сигналы", text: "Лучший канал с сигналами. Бесплатные прогнозы каждый день!", link: "https://t.me/example1", media: null },
    { title: "💰 Бизнес Инсайды", text: "Секретные стратегии заработка от профессионалов рынка.", link: "https://t.me/example2", media: null },
    { title: "📈 TON Новости", text: "Всё о блокчейне TON. Аналитика и обновления.", link: "https://t.me/example3", media: null },
    { title: "🎮 GameZone", text: "Лучшие игры, обзоры, розыгрыши и подарки!", link: "https://t.me/example4", media: null },
];

// ===== РОЛЬ =====
function selectRole(role) {
    S.role = role;
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
    let allAds = [...demoAds, ...S.orders.filter(o => o.viewsLeft > 0)];
    if (allAds.length === 0) {
        document.getElementById('vAdsSection').classList.add('hidden');
        document.getElementById('vNoAds').classList.remove('hidden');
        return;
    }

    const ad = allAds[Math.floor(Math.random() * allAds.length)];

    // Медиа
    const mediaEl = document.getElementById('adMedia');
    if (ad.media && ad.mediaType === 'image') {
        mediaEl.innerHTML = '<img src="' + ad.media + '">';
    } else if (ad.media && ad.mediaType === 'video') {
        mediaEl.innerHTML = '<video src="' + ad.media + '" autoplay muted loop></video>';
    } else {
        mediaEl.innerHTML = '<div class="ad-media-placeholder">📢</div>';
    }

    document.getElementById('adTitle').textContent = ad.title;
    document.getElementById('ad
