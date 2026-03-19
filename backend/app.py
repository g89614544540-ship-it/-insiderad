from flask import Flask, request, jsonify

app = Flask(__name__)

WALLET = "UQBBklp5lYFEgYig5200TPsLjtDOnAUUGToyiFhzI6D0tP8d"
SB_URL = "https://kjschhxyiobwlrpeoqwp.supabase.co"
SB_KEY = "sb_publishable_lhTbA9PwffdfBsLmBzfCjQ_qlUW82MM"

@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0,user-scalable=no">
<title>InsiderAd</title>
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,sans-serif;background:#0a1628;color:#fff;min-height:100vh}
.hidden{display:none!important}
.rs{display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:100vh;padding:20px}
.rl{font-size:64px;margin-bottom:12px}
.rt{font-size:32px;font-weight:800;color:#4a9eff}
.rsb{font-size:14px;opacity:.4;margin:6px 0 50px}
.rb{width:100%;max-width:320px;padding:20px;border:none;border-radius:16px;font-size:17px;font-weight:700;cursor:pointer;margin-bottom:14px;display:flex;align-items:center;justify-content:center;gap:12px}
.rb:active{transform:scale(.97)}
.rv{background:#0d2744;color:#4a9eff;border:1px solid #1e4976}
.ra{background:#1a1508;color:#f5a623;border:1px solid #4a3510}
.vs{display:none;min-height:100vh;padding-bottom:70px}
.vh{background:#0d2744;padding:16px 20px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #1e4976}
.vht{font-size:18px;font-weight:700;color:#4a9eff}
.vbb{background:rgba(74,158,255,.15);padding:6px 14px;border-radius:20px;font-size:14px;font-weight:600;color:#4a9eff}
.aw{padding:20px;display:flex;flex-direction:column;align-items:center;min-height:calc(100vh - 140px)}
.ac{background:#0d1f3c;border:1px solid #1e4976;border-radius:20px;padding:20px;width:100%;max-width:400px}
.am{width:100%;height:200px;border-radius:12px;overflow:hidden;margin-bottom:16px;background:#0a1628;display:flex;align-items:center;justify-content:center}
.am img,.am video{width:100%;height:100%;object-fit:cover}
.ac h3{font-size:18px;margin-bottom:8px}
.ac p{font-size:14px;opacity:.6;line-height:1.5;margin-bottom:16px}
.al{display:block;text-align:center;padding:10px;background:rgba(74,158,255,.1);border-radius:10px;color:#4a9eff;text-decoration:none;font-size:14px;font-weight:600;margin-bottom:16px}
.at{font-size:52px;font-weight:800;color:#4a9eff;text-align:center;margin:16px 0}
.ap{width:100%;height:4px;background:#1e4976;border-radius:2px;margin:16px 0;overflow:hidden}
.apb{height:100%;background:linear-gradient(90deg,#0066cc,#4a9eff);border-radius:2px;transition:width 1s linear;width:0%}
.ar{text-align:center;font-size:14px;color:#4a9eff;font-weight:600;margin-bottom:16px}
.btn{width:100%;padding:16px;border:none;border-radius:14px;font-size:16px;font-weight:700;cursor:pointer;color:#fff;background:linear-gradient(135deg,#0066cc,#4a9eff)}
.btn:disabled{background:#1a2a3e;color:#3a4a5e;cursor:not-allowed}
.cnt{font-size:12px;opacity:.3;margin-top:12px;text-align:center}
.bn{position:fixed;bottom:0;left:0;width:100%;background:#0d1f3c;display:flex;border-top:1px solid #1e4976;padding:6px 0}
.ni{flex:1;text-align:center;padding:8px;font-size:11px;opacity:.4;cursor:pointer;background:none;border:none;color:#fff}
.ni.act{opacity:1;color:#4a9eff}
.nico{font-size:20px;margin-bottom:2px}
.ws{padding:20px}
.wc{background:#0d1f3c;border:1px solid #1e4976;border-radius:20px;padding:28px;text-align:center;margin-bottom:16px}
.wl{font-size:13px;opacity:.4}
.wa{font-size:40px;font-weight:800;color:#4a9eff;margin:8px 0}
.wi{width:100%;padding:14px;background:#0a1628;border:1px solid #1e4976;border-radius:12px;color:#fff;font-size:14px;outline:none;margin-bottom:12px}
.bw{width:100%;padding:16px;border:none;border-radius:14px;font-size:16px;font-weight:700;cursor:pointer;color:#fff;background:linear-gradient(135deg,#0a6e3a,#0d9e52)}
.bw:disabled{background:#1a2a3e;color:#3a4a5e}
.winf{font-size:12px;opacity:.3;text-align:center;margin-top:10px}
.cp{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(5,10,20,.97);z-index:1000;align-items:center;justify-content:center;flex-direction:column}
.cp.show{display:flex}
.cpt{font-size:22px;font-weight:800;color:#ff4444;margin:16px 0 8px}
.cpx{font-size:16px;opacity:.6;margin-bottom:24px}
.cpm{font-size:64px;font-weight:800;color:#ff4444;margin-bottom:24px}
.cpi{width:100px;height:64px;text-align:center;font-size:36px;font-weight:800;background:#0d1f3c;border:2px solid #1e4976;border-radius:16px;color:#fff;outline:none}
.cph{font-size:13px;opacity:.3;margin-top:16px}
.as{display:none;min-height:100vh}
.ah{background:#1a1508;padding:16px 20px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #4a3510}
.aht{font-size:18px;font-weight:700;color:#f5a623}
.abb{background:rgba(245,166,35,.15);padding:6px 14px;border-radius:20px;font-size:14px;font-weight:600;color:#f5a623}
.tabs{display:flex;background:#0d1f3c;border-bottom:1px solid #1e4976}
.tab{flex:1;padding:14px;text-align:center;font-size:12px;cursor:pointer;border:none;background:none;color:#fff;opacity:.4;border-bottom:2px solid transparent}
.tab.act{opacity:1;color:#f5a623;border-bottom-color:#f5a623}
.acn{padding:16px}
.acd{background:#0d1f3c;border:1px solid #1e4976;border-radius:16px;padding:20px;margin-bottom:14px}
.ig{margin-bottom:16px}
.ig label{display:block;font-size:13px;opacity:.5;margin-bottom:6px}
.ig input,.ig textarea{width:100%;padding:14px;background:#0a1628;border:1px solid #1e4976;border-radius:12px;color:#fff;font-size:15px;outline:none}
.ig textarea{height:90px;resize:none}
.mu{width:100%;height:120px;border:2px dashed #1e4976;border-radius:12px;display:flex;flex-direction:column;align-items:center;justify-content:center;cursor:pointer}
.mu:hover{border-color:#f5a623}
.mp{width:100%;height:120px;border-radius:12px;overflow:hidden;margin-top:8px;display:none}
.mp img,.mp video{width:100%;height:100%;object-fit:cover}
.pd{background:#0a1628;border:1px solid #1e4976;border-radius:14px;padding:20px;text-align:center;margin:16px 0}
.pam{font-size:32px;font-weight:800;color:#f5a623}
.plb{font-size:12px;opacity:.4;margin-top:4px}
.bc{width:100%;padding:16px;border:none;border-radius:14px;font-size:16px;font-weight:700;cursor:pointer;color:#fff;background:linear-gradient(135deg,#d4870a,#f5a623)}
</style>
</head>
<body>
<div id="R" class="rs">
<div class="rl">💎</div>
<div class="rt">InsiderAd</div>
<div class="rsb">Рекламная биржа в Telegram</div>
<button class="rb rv" onclick="go('v')">👁 Смотреть рекламу</button>
<button class="rb ra" onclick="go('a')">📢 Разместить рекламу</button>
</div>

<div id="V" class="vs">
<div class="vh"><div class="vht">💎 InsiderAd</div><div class="vbb">💎 <span id="vB">0.00</span> TON</div></div>
<div id="vA">
<div class="aw"><div class="ac">
<div class="am" id="aM"><div style="font-size:48px;opacity:.2">📢</div></div>
<h3 id="aT">Загрузка...</h3>
<p id="aP">Подождите</p>
<a href="#" id="aL" class="al" target="_blank">Перейти →</a>
<div class="at" id="aTm">15</div>
<div class="ap"><div class="apb" id="aB"></div></div>
<div class="ar">💎 +0.04 TON</div>
<button class="btn" id="bW" disabled onclick="watched()">Подождите... 15</button>
<div class="cnt">Просмотрено: <span id="aC">0</span></div>
</div></div>
</div>
<div id="vW" class="ws hidden">
<div class="wc"><div class="wl">Баланс</div><div class="wa">💎 <span id="wB">0.00</span> TON</div></div>
<label style="font-size:13px;opacity:.5;display:block;margin-bottom:6px">Адрес TON кошелька</label>
<input class="wi" id="wA" placeholder="UQ... или EQ..." oninput="chkW()">
<button class="bw" id="bWt" disabled onclick="doW()">Минимум 1.5 TON</button>
<div class="winf">Минимальный вывод: 1.5 TON</div>
</div>
<div class="bn">
<button class="ni act" id="n1" onclick="vt('a')"><div class="nico">👁</div>Реклама</button>
<button class="ni" id="n2" onclick="vt('w')"><div class="nico">💎</div>Кошелёк</button>
</div>
</div>

<div id="C" class="cp">
<div style="font-size:48px">🔒</div>
<div class="cpt">ПРОВЕРКА</div>
<div class="cpx">Введите число 4</div>
<div class="cpm" id="cT">7</div>
<input type="number" class="cpi" id="cI" oninput="chkC()">
<div class="cph">7 секунд или баланс сгорит!</div>
</div>

<div id="A" class="as">
<div class="ah"><div class="aht">📢 InsiderAd</div><div class="abb">💎 <span id="aB2">0.00</span> TON</div></div>
<div class="tabs">
<button class="tab act" id="t1" onclick="at('c')">➕ Создать</button>
<button class="tab" id="t2" onclick="at('o')">📊 Заказы</button>
</div>
<div id="sC" class="acn"><div class="acd">
<div class="ig"><label>Медиа</label>
<div class="mu" onclick="document.getElementById('mF').click()">
<div style="font-size:36px;opacity:.3">📷</div><div style="font-size:13px;opacity:.4">Загрузить фото/видео</div>
<input type="file" id="mF" accept="image/*,video/*" onchange="prM(this)" style="display:none">
</div><div class="mp" id="mP"></div></div>
<div class="ig"><label>Заголовок</label><input id="iT" placeholder="Название"></div>
<div class="ig"><label>Текст</label><textarea id="iTx" placeholder="Описание"></textarea></div>
<div class="ig"><label>Ссылка (обязательно)</label><input id="iL" placeholder="https://t.me/channel"></div>
<div class="ig"><label>Просмотры (мин 100)</label><input type="number" id="iV" min="100" value="100" oninput="calc()"></div>
<div class="pd"><div class="pam" id="pA">5.00 TON</div><div class="plb">100 просмотров = 5 TON</div></div>
<button class="bc" onclick="mkAd()">💎 Оплатить и запустить</button>
</div></div>
<div id="sO" class="acn hidden"><div style="text-align:center;padding:40px;opacity:.3"><div style="font-size:48px;margin-bottom:12px">📋</div><p>Нет заказов</p></div></div>
</div>

<script>
var tg=window.Telegram.WebApp;tg.ready();tg.expand();
var W="''' + WALLET + '''";
var SB="''' + SB_URL + '''";
var SK="''' + SB_KEY + '''";
var S={b:0,w:0,tot:0,nc:rc(),ti:null,tm:15,md:null,mt:null,uid:null};
var ads=[
{t:"🚀 Крипто Сигналы",p:"Лучший канал с сигналами!",l:"https://t.me/ex1",m:null,mt:null},
{t:"💰 Бизнес Инсайды",p:"Секретные стратегии заработка.",l:"https://t.me/ex2",m:null,mt:null},
{t:"📈 TON Новости",p:"Всё о блокчейне TON.",l:"https://t.me/ex3",m:null,mt:null},
{t:"🎮 GameZone",p:"Игры, обзоры и розыгрыши!",l:"https://t.me/ex4",m:null,mt:null}
];
function rc(){return Math.floor(Math.random()*9)+5}

// Init user
async function initUser(){
try{
var u=tg.initDataUnsafe&&tg.initDataUnsafe.user;
if(u){
var r=await fetch('/api/user',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({telegram_id:u.id,username:u.username||''})});
var d=await r.json();
if(d.id){S.uid=d.id;S.b=parseFloat(d.balance)||0;S.tot=d.total_watched||0;upd()}
}}catch(e){console.log(e)}
}
initUser();

function go(r){document.getElementById('R').style.display='none';if(r=='v'){document.getElementById('V').style.display='block';loadAd()}else{document.getElementById('A').style.display='block'}}

function loadAd(){
var a=ads[Math.floor(Math.random()*ads.length)];
var m=document.getElementById('aM');
if(a.m&&a.mt=='img'){m.innerHTML='<img src="'+a.m+'">'}
else if(a.m&&a.mt=='vid'){m.innerHTML='<video src="'+a.m+'" autoplay muted loop></video>'}
else{m.innerHTML='<div style="font-size:48px;opacity:.2">📢</div>'}
document.getElementById('aT').textContent=a.t;
document.getElementById('aP').textContent=a.p;
document.getElementById('aL').href=a.l;
S.tm=15;document.getElementById('aTm').textContent='15';
document.getElementById('aB').style.width='0%';
document.getElementById('bW').disabled=true;
document.getElementById('bW').textContent='Подождите... 15';
clearInterval(S.ti);
S.ti=setInterval(function(){
S.tm--;document.getElementById('aTm').textContent=S.tm;
document.getElementById('aB').style.width=((15-S.tm)/15*100)+'%';
document.getElementById('bW').textContent='Подождите... '+S.tm;
if(S.tm<=0){clearInterval(S.ti);document.getElementById('bW').disabled=false;document.getElementById('bW').textContent='✅ Получить 0.04 TON'}
},1000);
}

async function watched(){
S.b+=0.04;S.w++;S.tot++;upd();
try{await fetch('/api/watch',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user_id:S.uid,ad_id:null})})}catch(e){}
if(S.w>=S.nc){showCap();return}
loadAd();
}

function upd(){
document.getElementById('vB').textContent=S.b.toFixed(2);
document.getElementById('wB').textContent=S.b.toFixed(2);
document.getElementById('aC').textContent=S.tot;chkW();
}

function showCap(){
document.getElementById('C').classList.add('show');
document.getElementById('cI').value='';
var t=7;document.getElementById('cT').textContent=t;
clearInterval(S.ti);
S.ti=setInterval(function(){t--;document.getElementById('cT').textContent=t;if(t<=0){clearInterval(S.ti);capF()}},1000);
setTimeout(function(){document.getElementById('cI').focus()},100);
}

function chkC(){if(document.getElementById('cI').value=='4'){clearInterval(S.ti);capOk()}}
function capOk(){document.getElementById('C').classList.remove('show');S.w=0;S.nc=rc();loadAd()}
function capF(){document.getElementById('C').classList.remove('show');S.b=0;S.w=0;S.nc=rc();upd();alert('Время вышло! Баланс сгорел!');loadAd()}

function vt(t){
document.getElementById('n1').className='ni'+(t=='a'?' act':'');
document.getElementById('n2').className='ni'+(t=='w'?' act':'');
document.getElementById('vA').className=t=='a'?'':'hidden';
document.getElementById('vW').className=t=='w'?'ws':'ws hidden';
}

function chkW(){
var a=document.getElementById('wA').value;var b=document.getElementById('bWt');
if(S.b>=1.5&&a.length>10){b.disabled=false;b.textContent='Вывести '+S.b.toFixed(2)+' TON'}
else if(S.b<1.5){b.disabled=true;b.textContent='Минимум 1.5 TON ('+S.b.toFixed(2)+')'}
else{b.disabled=true;b.textContent='Введите адрес'}
}

async function doW(){
var a=document.getElementById('wA').value;
if(S.b>=1.5&&a.length>10){
try{await fetch('/api/withdraw',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user_id:S.uid,wallet_address:a})})}catch(e){}
alert('Заявка на вывод '+S.b.toFixed(2)+' TON\\nАдрес: '+a);S.b=0;upd();
}}

function calc(){var v=Math.max(100,parseInt(document.getElementById('iV').value)||100);document.getElementById('pA').textContent=(v/100*5).toFixed(2)+' TON'}

function prM(el){var f=el.files[0];if(!f)return;var r=new FileReader();var p=document.getElementById('mP');
r.onload=function(e){if(f.type.startsWith('image')){p.innerHTML='<img src="'+e.target.result+'">';S.mt='img'}else{p.innerHTML='<video src="'+e.target.result+'" autoplay muted loop></video>';S.mt='vid'}S.md=e.target.result;p.style.display='block'};r.readAsDataURL(f)}

function mkAd(){
var t=document.getElementById('iT').value,tx=document.getElementById('iTx').value,l=document.getElementById('iL').value,v=Math.max(100,parseInt(document.getElementById('iV').value)||100);
if(!t||!l){alert('Заполните заголовок и ссылку!');return}
var p=(v/100*5).toFixed(2);
ads.push({t:t,p:tx,l:l,m:S.md,mt:S.mt});
alert('Оплатите '+p+' TON на адрес:\\n'+W+'\\n\\nРеклама добавлена!');
}

function at(t){
document.getElementById('t1').className='tab'+(t=='c'?' act':'');
document.getElementById('t2').className='tab'+(t=='o'?' act':'');
document.getElementById('sC').className=t=='c'?'acn':'acn hidden';
document.getElementById('sO').className=t=='o'?'acn':'acn hidden';
}
</script>
</body>
</html>'''


@app.route('/api/user', methods=['POST'])
def api_user():
    try:
        import httpx
        data = request.json
        tg_id = data.get('telegram_id')
        headers = {"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}", "Content-Type": "application/json"}
        r = httpx.get(f"{SB_URL}/rest/v1/users?telegram_id=eq.{tg_id}&select=*", headers=headers)
        if r.json():
            return jsonify(r.json()[0])
        r2 = httpx.post(f"{SB_URL}/rest/v1/users", headers={**headers, "Prefer": "return=representation"}, json={"telegram_id": tg_id, "username": data.get("username", ""), "balance": 0, "total_watched": 0})
        return jsonify(r2.json()[0])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/watch', methods=['POST'])
def api_watch():
    try:
        import httpx
        data = request.json
        uid = data.get('user_id')
        headers = {"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}", "Content-Type": "application/json"}
        r = httpx.get(f"{SB_URL}/rest/v1/users?id=eq.{uid}&select=*", headers=headers)
        if not r.json():
            return jsonify({"error": "user not found"}), 404
        u = r.json()[0]
        nb = float(u['balance']) + 0.04
        nw = u['total_watched'] + 1
        httpx.patch(f"{SB_URL}/rest/v1/users?id=eq.{uid}", headers={**headers, "Prefer": "return=representation"}, json={"balance": nb, "total_watched": nw})
        return jsonify({"balance": nb, "total_watched": nw})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/withdraw', methods=['POST'])
def api_withdraw():
    try:
        import httpx
        data = request.json
        uid = data.get('user_id')
        wallet = data.get('wallet_address')
        headers = {"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}", "Content-Type": "application/json"}
        r = httpx.get(f"{SB_URL}/rest/v1/users?id=eq.{uid}&select=*", headers=headers)
        u = r.json()[0]
        amt = float(u['balance'])
        if amt < 1.5:
            return jsonify({"error": "min 1.5"}), 400
        httpx.post(f"{SB_URL}/rest/v1/withdrawals", headers={**headers, "Prefer": "return=representation"}, json={"user_id": uid, "amount": amt, "wallet_address": wallet})
        httpx.patch(f"{SB_URL}/rest/v1/users?id=eq.{uid}", headers={**headers, "Prefer": "return=representation"}, json={"balance": 0})
        return jsonify({"success": True, "amount": amt})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/health')
def health():
    return jsonify({"status": "ok"})


if __name__ == '__main__':
    app.run(debug=True)
