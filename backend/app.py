from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return """<!DOCTYPE html>
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
.role-btn:active{transform:scale(.97)}
.rv{background:#0d2744;color:#4a9eff;border:1px solid #1e4976}
.ra{background:#1a1508;color:#f5a623;border:1px solid #4a3510}
.vscreen{display:none;min-height:100vh;padding-bottom:70px}
.vhdr{background:#0d2744;padding:16px 20px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #1e4976}
.vhdr-t{font-size:18px;font-weight:700;color:#4a9eff}
.vbal{background:rgba(74,158,255,.15);padding:6px 14px;border-radius:20px;font-size:14px;font-weight:600;color:#4a9eff}
.adwrap{padding:20px;display:flex;flex-direction:column;align-items:center;min-height:calc(100vh - 140px)}
.adcard{background:#0d1f3c;border:1px solid #1e4976;border-radius:20px;padding:20px;width:100%;max-width:400px}
.admedia{width:100%;height:200px;border-radius:12px;overflow:hidden;margin-bottom:16px;background:#0a1628;display:flex;align-items:center;justify-content:center}
.admedia img,.admedia video{width:100%;height:100%;object-fit:cover}
.adcard h3{font-size:18px;margin-bottom:8px}
.adcard p{font-size:14px;opacity:.6;line-height:1.5;margin-bottom:16px}
.adlink{display:block;text-align:center;padding:10px;background:rgba(74,158,255,.1);border-radius:10px;color:#4a9eff;text-decoration:none;font-size:14px;font-weight:600;margin-bottom:16px}
.adtimer{font-size:52px;font-weight:800;color:#4a9eff;text-align:center;margin:16px 0}
.adprog{width:100%;height:4px;background:#1e4976;border-radius:2px;margin:16px 0;overflow:hidden}
.adprogbar{height:100%;background:linear-gradient(90deg,#0066cc,#4a9eff);border-radius:2px;transition:width 1s linear;width:0%}
.adrew{text-align:center;font-size:14px;color:#4a9eff;font-weight:600;margin-bottom:16px}
.btn{width:100%;padding:16px;border:none;border-radius:14px;font-size:16px;font-weight:700;cursor:pointer;color:#fff;background:linear-gradient(135deg,#0066cc,#4a9eff)}
.btn:active{transform:scale(.97)}
.btn:disabled{background:#1a2a3e;color:#3a4a5e;cursor:not-allowed}
.adcnt{font-size:12px;opacity:.3;margin-top:12px;text-align:center}
.wnav{position:fixed;bottom:0;left:0;width:100%;background:#0d1f3c;display:flex;border-top:1px solid #1e4976;padding:6px 0}
.ni{flex:1;text-align:center;padding:8px;font-size:11px;opacity:.4;cursor:pointer;background:none;border:none;color:#fff}
.ni.act{opacity:1;color:#4a9eff}
.nicon{font-size:20px;margin-bottom:2px}
.wsec{padding:20px}
.wcard{background:#0d1f3c;border:1px solid #1e4976;border-radius:20px;padding:28px;text-align:center;margin-bottom:16px}
.wlbl{font-size:13px;opacity:.4}
.wamt{font-size:40px;font-weight:800;color:#4a9eff;margin:8px 0}
.winp{width:100%;padding:14px;background:#0a1628;border:1px solid #1e4976;border-radius:12px;color:#fff;font-size:14px;outline:none;margin-bottom:12px}
.winp:focus{border-color:#4a9eff}
.bwit{width:100%;padding:16px;border:none;border-radius:14px;font-size:16px;font-weight:700;cursor:pointer;color:#fff;background:linear-gradient(135deg,#0a6e3a,#0d9e52)}
.bwit:disabled{background:#1a2a3e;color:#3a4a5e}
.winf{font-size:12px;opacity:.3;text-align:center;margin-top:10px}
.cap{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(5,10,20,.97);z-index:1000;align-items:center;justify-content:center;flex-direction:column;padding:20px}
.cap.show{display:flex}
.captit{font-size:22px;font-weight:800;color:#ff4444;margin-bottom:8px}
.captxt{font-size:16px;opacity:.6;margin-bottom:24px}
.captim{font-size:64px;font-weight:800;color:#ff4444;margin-bottom:24px}
.capinp{width:100px;height:64px;text-align:center;font-size:36px;font-weight:800;background:#0d1f3c;border:2px solid #1e4976;border-radius:16px;color:#fff;outline:none}
.caphint{font-size:13px;opacity:.3;margin-top:16px}
.ascreen{display:none;min-height:100vh}
.ahdr{background:#1a1508;padding:16px 20px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #4a3510}
.ahdr-t{font-size:18px;font-weight:700;color:#f5a623}
.abalb{background:rgba(245,166,35,.15);padding:6px 14px;border-radius:20px;font-size:14px;font-weight:600;color:#f5a623}
.atabs{display:flex;background:#0d1f3c;border-bottom:1px solid #1e4976}
.atab{flex:1;padding:14px;text-align:center;font-size:12px;cursor:pointer;border:none;background:none;color:#fff;opacity:.4;border-bottom:2px solid transparent}
.atab.act{opacity:1;color:#f5a623;border-bottom-color:#f5a623}
.acont{padding:16px}
.acard{background:#0d1f3c;border:1px solid #1e4976;border-radius:16px;padding:20px;margin-bottom:14px}
.ig{margin-bottom:16px}
.ig label{display:block;font-size:13px;opacity:.5;margin-bottom:6px}
.ig input,.ig textarea{width:100%;padding:14px;background:#0a1628;border:1px solid #1e4976;border-radius:12px;color:#fff;font-size:15px;outline:none}
.ig input:focus,.ig textarea:focus{border-color:#f5a623}
.ig textarea{height:90px;resize:none}
.mup{width:100%;height:140px;border:2px dashed #1e4976;border-radius:12px;display:flex;flex-direction:column;align-items:center;justify-content:center;cursor:pointer}
.mup:hover{border-color:#f5a623}
.mup-i{font-size:36px;opacity:.3;margin-bottom:8px}
.mup-t{font-size:13px;opacity:.4}
.mprev{width:100%;height:140px;border-radius:12px;overflow:hidden;margin-top:8px;display:none}
.mprev img,.mprev video{width:100%;height:100%;object-fit:cover}
.pdisp{background:#0a1628;border:1px solid #1e4976;border-radius:14px;padding:20px;text-align:center;margin:16px 0}
.pamt{font-size:32px;font-weight:800;color:#f5a623}
.plbl{font-size:12px;opacity:.4;margin-top:4px}
.bcr{width:100%;padding:16px;border:none;border-radius:14px;font-size:16px;font-weight:700;cursor:pointer;color:#fff;background:linear-gradient(135deg,#d4870a,#f5a623)}
.nodata{text-align:center;padding:40px 20px;opacity:.3}
.nodata-i{font-size:48px;margin-bottom:12px}
</style>
</head>
<body>

<div id="roleScr" class="role-screen">
<div class="role-logo">💎</div>
<div class="role-title">InsiderAd</div>
<div class="role-sub">Рекламная биржа Telegram каналов</div>
<button class="role-btn rv" onclick="go('viewer')">👁 Смотреть рекламу и зарабатывать</button>
<button class="role-btn ra" onclick="go('adv')">📢 Разместить рекламу</button>
</div>

<div id="vScr" class="vscreen">
<div class="vhdr"><div class="vhdr-t">💎 InsiderAd</div><div class="vbal">💎 <span id="vB">0.00</span> TON</div></div>
<div id="vAds">
<div class="adwrap"><div class="adcard">
<div class="admedia" id="adM"><div style="font-size:48px;opacity:.2">📢</div></div>
<h3 id="adT">Загрузка...</h3>
<p id="adP">Подождите</p>
<a href="#" id="adL" class="adlink" target="_blank">Перейти →</a>
<div class="adtimer" id="adTm">15</div>
<div class="adprog"><div class="adprogbar" id="adBr"></div></div>
<div class="adrew">💎 +0.04 TON за просмотр</div>
<button class="btn" id="bW" disabled onclick="watched()">Подождите... 15 сек</button>
<div class="adcnt">Просмотрено: <span id="adC">0</span></div>
</div></div>
</div>
<div id="vWal" class="wsec hidden">
<div class="wcard"><div class="wlbl">Ваш баланс</div><div class="wamt">💎 <span id="wB">0.00</span> TON</div></div>
<label style="font-size:13px;opacity:.5;margin-bottom:6px;display:block">Адрес TON кошелька для вывода</label>
<input type="text" class="winp" id="wAddr" placeholder="UQ... или EQ..." oninput="chkW()">
<button class="bwit" id="bWit" disabled onclick="doWithdraw()">Минимум 1.5 TON</button>
<div class="winf">Минимальный вывод: 1.5 TON</div>
</div>
<div class="wnav">
<button class="ni act" id="n1" onclick="vt('ads')"><div class="nicon">👁</div>Реклама</button>
<button class="ni" id="n2" onclick="vt('wal')"><div class="nicon">💎</div>Кошелёк</button>
</div>
</div>

<div id="capO" class="cap">
<div style="font-size:48px;margin-bottom:16px">🔒</div>
<div class="captit">ПРОВЕРКА</div>
<div class="captxt">Введите число 4</div>
<div class="captim" id="cTm">7</div>
<input type="number" class="capinp" id="cIn" oninput="chkC()">
<div class="caphint">У вас 7 секунд. Не прошли — баланс сгорает!</div>
</div>

<div id="aScr" class="ascreen">
<div class="ahdr"><div class="ahdr-t">📢 InsiderAd</div><div class="abalb">💎 <span id="aB">0.00</span> TON</div></div>
<div class="atabs">
<button class="atab act" id="t1" onclick="at('cr')">➕ Создать</button>
<button class="atab" id="t2" onclick="at('or')">📊 Заказы</button>
</div>
<div id="sCr" class="acont">
<div class="acard">
<div class="ig"><label>Медиа (фото или видео)</label>
<div class="mup" onclick="document.getElementById('mF').click()">
<div class="mup-i">📷</div><div class="mup-t">Нажмите для загрузки</div>
<input type="file" id="mF" accept="image/*,video/*" onchange="prevM(this)" style="display:none">
</div>
<div class="mprev" id="mPr"></div>
</div>
<div class="ig"><label>Заголовок рекламы</label><input type="text" id="iT" placeholder="Название канала"></div>
<div class="ig"><label>Текст рекламы</label><textarea id="iTx" placeholder="Описание"></textarea></div>
<div class="ig"><label>Ссылка (обязательно)</label><input type="text" id="iL" placeholder="https://t.me/channel"></div>
<div class="ig"><label>Просмотры (мин. 100)</label><input type="number" id="iV" min="100" value="100" oninput="calc()"></div>
<div class="pdisp"><div class="pamt" id="pA">5.00 TON</div><div class="plbl">100 просмотров = 5 TON</div></div>
<button class="bcr" onclick="mkAd()">💎 Оплатить и запустить</button>
</div></div>
<div id="sOr" class="acont hidden"><div class="nodata"><div class="nodata-i">📋</div><p>Нет заказов</p></div></div>
</div>

<script>
var tg=window.Telegram.WebApp;tg.ready();tg.expand();
var W="UQBBklp5lYFEgYig5200TPsLjtDOnAUUGToyiFhzI6D0tP8d";
var S={b:0,w:0,tot:0,nc:rc(),ti:null,tm:15,md:null,mt:null};
var ads=[
{t:"🚀 Крипто Сигналы",p:"Лучший канал с сигналами. Бесплатные прогнозы!",l:"https://t.me/ex1",m:null},
{t:"💰 Бизнес Инсайды",p:"Секретные стратегии заработка от профи.",l:"https://t.me/ex2",m:null},
{t:"📈 TON Новости",p:"Всё о блокчейне TON. Аналитика.",l:"https://t.me/ex3",m:null},
{t:"🎮 GameZone",p:"Лучшие игры, обзоры и розыгрыши!",l:"https://t.me/ex4",m:null}
];
function rc(){return Math.floor(Math.random()*9)+5}
function go(r){document.getElementById('roleScr').style.display='none';if(r=='viewer'){document.getElementById('vScr').style.display='block';loadAd()}else{document.getElementById('aScr').style.display='block'}}
function loadAd(){var a=ads[Math.floor(Math.random()*ads.length)];var m=document.getElementById('adM');if(a.m&&a.mt=='img'){m.innerHTML='<img src="'+a.m+'">'}else if(a.m&&a.mt=='vid'){m.innerHTML='<video src="'+a.m+'" autoplay muted loop></video>'}else{m.innerHTML='<div style="font-size:48px;opacity:.2">📢</div>'}
document.getElementById('adT').textContent=a.t;document.getElementById('adP').textContent=a.p;document.getElementById('adL').href=a.l;document.getElementById('adL').textContent='Перейти →';
S.tm=15;document.getElementById('adTm').textContent='15';document.getElementById('adBr').style.width='0%';document.getElementById('bW').disabled=true;document.getElementById('bW').textContent='Подождите... 15 сек';
clearInterval(S.ti);S.ti=setInterval(function(){S.tm--;document.getElementById('adTm').textContent=S.tm;document.getElementById('adBr').style.width=((15-S.tm)/15*100)+'%';document.getElementById('bW').textContent='Подождите... '+S.tm+' сек';
if(S.tm<=0){clearInterval(S.ti);document.getElementById('bW').disabled=false;document.getElementById('bW').textContent='✅ Получить 0.04 TON'}},1000)}
function watched(){S.b+=0.04;S.w++;S.tot++;upd();if(S.w>=S.nc){showCap();return}loadAd()}
function upd(){document.getElementById('vB').textContent=S.b.toFixed(2);document.getElementById('wB').textContent=S.b.toFixed(2);document.getElementById('adC').textContent=S.tot;chkW()}
function showCap(){document.getElementById('capO').classList.add('show');document.getElementById('cIn').value='';document.getElementById('cIn').focus();var t=7;document.getElementById('cTm').textContent=t;clearInterval(S.ti);S.ti=setInterval(function(){t--;document.getElementById('cTm').textContent=t;if(t<=0){clearInterval(S.ti);capFail()}},1000)}
function chkC(){if(document.getElementById('cIn').value=='4'){clearInterval(S.ti);capOk()}}
function capOk(){document.getElementById('capO').classList.remove('show');S.w=0;S.nc=rc();loadAd()}
function capFail(){document.getElementById('capO').classList.remove('show');S.b=0;S.w=0;S.nc=rc();upd();alert('Время вышло! Баланс сгорел!');loadAd()}
function vt(t){document.getElementById('n1').className='ni'+(t=='ads'?' act':'');document.getElementById('n2').className='ni'+(t=='wal'?' act':'');document.getElementById('vAds').className=t=='ads'?'':'hidden';document.getElementById('vWal').className=t=='wal'?'wsec':'wsec hidden'}
function chkW(){var a=document.getElementById('wAddr').value;var b=document.getElementById('bWit');if(S.b>=1.5&&a.length>10){b.disabled=false;b.textContent='Вывести '+S.b.toFixed(2)+' TON'}else if(S.b<1.5){b.disabled=true;b.textContent='Минимум 1.5 TON (сейчас '+S.b.toFixed(2)+')'}else{b.disabled=true;b.textContent='Введите адрес кошелька'}}
function doWithdraw(){var a=document.getElementById('wAddr').value;if(S.b>=1.5&&a.length>10){alert('Заявка на вывод '+S.b.toFixed(2)+' TON на адрес:\\n'+a);S.b=0;upd()}}
function calc(){var v=Math.max(100,parseInt(document.getElementById('iV').value)||100);document.getElementById('pA').textContent=(v/100*5).toFixed(2)+' TON'}
function prevM(el){var f=el.files[0];if(!f)return;var r=new FileReader();var pr=document.getElementById('mPr');r.onload=function(e){if(f.type.startsWith('image')){pr.innerHTML='<img src="'+e.target.result+'">';S.mt='img'}else{pr.innerHTML='<video src="'+e.target.result+'" autoplay muted loop></video>';S.mt='vid'}S.md=e.target.result;pr.style.display='block'};r.readAsDataURL(f)}
function mkAd(){var t=document.getElementById('iT').value;var tx=document.getElementById('iTx').value;var l=document.getElementById('iL').value;var v=Math.max(100,parseInt(document.getElementById('iV').value)||100);
if(!t||!l){alert('Заполните заголовок и ссылку!');return}
var p=(v/100*5).toFixed(2);ads.push({t:t,p:tx,l:l,m:S.md,mt:S.mt});
alert('Оплатите '+p+' TON на адрес:\\n'+W+'\\n\\nРеклама добавлена!')}
function at(t){document.getElementById('t1').className='atab'+(t=='cr'?' act':'');document.getElementById('t2').className='atab'+(t=='or'?' act':'');document.getElementById('sCr').className=t=='cr'?'acont':'acont hidden';document.getElementById('sOr').className=t=='or'?'acont':'acont hidden'}
</script>
</body>
</html>"""

if __name__ == '__main__':
    app.run(debug=True)
