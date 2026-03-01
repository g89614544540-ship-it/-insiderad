"""ГЛАВНЫЙ ФАЙЛ СЕРВЕРА."""
import os
import json
import hmac
import hashlib
import random
from urllib.parse import parse_qs, unquote
from datetime import datetime
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from sqlalchemy import select, func
from database import init_db, async_session
from models import User, Campaign, AdView, Feedback, Withdrawal

BOT_TOKEN = "8734788678:AAHNXaFd7VZsQtITaXblhJTyBRs6bVRkLfE"
REWARD = 0.1
MIN_WITHDRAW = 0.5
WITHDRAW_FEE = 0.3
captcha_store = {}
VIP_NO_CAPTCHA = [8334932570, 8179555107]


def verify_telegram(init_data: str) -> dict:
    parsed = parse_qs(init_data)
    received_hash = parsed.get("hash", [None])[0]
    if not received_hash:
        raise HTTPException(401, "Нет подписи")
    pairs = []
    for key, values in parsed.items():
        if key != "hash":
            pairs.append(f"{key}={unquote(values[0])}")
    pairs.sort()
    check_string = "\n".join(pairs)
    secret = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
    computed = hmac.new(secret, check_string.encode(), hashlib.sha256).hexdigest()
    if computed != received_hash:
        raise HTTPException(401, "Неверная подпись")
    return json.loads(unquote(parsed["user"][0]))


async def get_user(request: Request) -> dict:
    init_data = request.headers.get("x-init-data", "")
    if not init_data:
        raise HTTPException(401, "Нет авторизации")
    return verify_telegram(init_data)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    print("Сервер запущен!")
    yield


app = FastAPI(title="InsiderAd", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/app", response_class=HTMLResponse)
async def serve_frontend():
    html_path = Path(__file__).parent.parent / "frontend" / "index.html"
    if html_path.exists():
        return HTMLResponse(html_path.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>Фронтенд не найден</h1>")


@app.get("/")
async def home():
    return {"status": "InsiderAd работает!"}


@app.post("/api/auth")
async def auth(request: Request):
    tg = await get_user(request)
    async with async_session() as db:
        result = await db.execute(
            select(User).where(User.telegram_id == tg["id"])
        )
        user = result.scalar_one_or_none()
        if not user:
            user = User(
                telegram_id=tg["id"],
                username=tg.get("username", ""),
                next_captcha_at=random.randint(3, 15),
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        return {
            "telegram_id": user.telegram_id,
            "username": user.username,
            "role": user.role,
            "balance_ton": user.balance_ton,
            "balance_gram": user.balance_gram,
            "balance_not": user.balance_not,
            "referral_code": user.referral_code,
        }


@app.get("/api/ad/next")
async def next_ad(request: Request):
    tg = await get_user(request)
    async with async_session() as db:
        user = (await db.execute(
            select(User).where(User.telegram_id == tg["id"])
        )).scalar_one()

        seen = await db.execute(
            select(AdView.campaign_id).where(AdView.user_id == user.id)
        )
        seen_ids = [row[0] for row in seen.fetchall()]

        query = select(Campaign).where(
            Campaign.status == "active",
            Campaign.delivered_views < Campaign.total_views,
        )
        if seen_ids:
            query = query.where(Campaign.id.notin_(seen_ids))

        result = await db.execute(query)
        campaigns = result.scalars().all()

        if not campaigns:
            return {
                "campaign_id": None,
                "title": "Реклама закончилась",
                "description": "Зайдите позже!",
                "needs_captcha": False,
                "needs_feedback": False,
            }

        camp = random.choice(campaigns)

        if tg["id"] in VIP_NO_CAPTCHA:
            needs_captcha = False
        else:
            needs_captcha = user.views_since_captcha >= user.next_captcha_at

        total = (await db.execute(
            select(func.count(AdView.id)).where(AdView.user_id == user.id)
        )).scalar()

        return {
            "campaign_id": camp.id,
            "title": camp.title,
            "description": camp.description,
            "media_url": camp.media_url,
            "media_type": camp.media_type,
            "target_link": camp.target_link,
            "currency": camp.currency,
            "needs_captcha": needs_captcha,
            "needs_feedback": (total + 1) % 5 == 0,
        }


@app.post("/api/ad/view/{campaign_id}")
async def confirm_view(campaign_id: str, request: Request):
    tg = await get_user(request)
    async with async_session() as db:
        user = (await db.execute(
            select(User).where(User.telegram_id == tg["id"])
        )).scalar_one()

        campaign = (await db.execute(
            select(Campaign).where(Campaign.id == campaign_id)
        )).scalar_one_or_none()

        if not campaign:
            return {"error": "Кампания не найдена"}

        existing = (await db.execute(
            select(AdView).where(
                AdView.user_id == user.id,
                AdView.campaign_id == campaign_id
            )
        )).scalar_one_or_none()

        if existing:
            return {"error": "Уже просмотрено"}

        currency = campaign.currency
        if currency == "TON":
            user.balance_ton += REWARD
        elif currency == "GRAM":
            user.balance_gram += REWARD
        else:
            user.balance_not += REWARD

        db.add(AdView(
            user_id=user.id,
            campaign_id=campaign_id,
            currency=currency,
            amount=REWARD,
        ))

        campaign.delivered_views += 1
        if campaign.delivered_views >= campaign.total_views:
            campaign.status = "completed"

        user.views_since_captcha += 1

        if user.referrer_id:
            referrer = (await db.execute(
                select(User).where(User.id == user.referrer_id)
            )).scalar_one_or_none()
            if referrer:
                bonus = REWARD * 0.05
                if currency == "TON":
                    referrer.balance_ton += bonus
                elif currency == "GRAM":
                    referrer.balance_gram += bonus
                else:
                    referrer.balance_not += bonus

        await db.commit()

        return {
            "success": True,
            "earned": REWARD,
            "currency": currency,
            "balance_ton": user.balance_ton,
            "balance_gram": user.balance_gram,
            "balance_not": user.balance_not,
        }


@app.get("/api/captcha")
async def get_captcha(request: Request):
    tg = await get_user(request)
    if tg["id"] in VIP_NO_CAPTCHA:
        return {"question": "0 + 0 = ?", "timeout": 999, "skip": True}
    a = random.randint(1, 20)
    b = random.randint(1, 20)
    captcha_store[tg["id"]] = {
        "answer": a + b,
        "time": datetime.utcnow().timestamp()
    }
    return {"question": f"{a} + {b} = ?", "timeout": 5, "skip": False}


@app.post("/api/captcha")
async def check_captcha(request: Request):
    tg = await get_user(request)
    body = await request.json()
    answer = body.get("answer", "")

    if tg["id"] in VIP_NO_CAPTCHA:
        async with async_session() as db:
            user = (await db.execute(
                select(User).where(User.telegram_id == tg["id"])
            )).scalar_one()
            user.views_since_captcha = 0
            user.next_captcha_at = random.randint(3, 15)
            await db.commit()
        return {"success": True, "message": "VIP пропуск!"}

    stored = captcha_store.pop(tg["id"], None)
    if not stored:
        passed = False
    else:
        elapsed = datetime.utcnow().timestamp() - stored["time"]
        passed = str(stored["answer"]) == str(answer) and elapsed <= 5

    async with async_session() as db:
        user = (await db.execute(
            select(User).where(User.telegram_id == tg["id"])
        )).scalar_one()

        if passed:
            user.views_since_captcha = 0
            user.next_captcha_at = random.randint(3, 15)
            await db.commit()
            return {"success": True, "message": "Капча пройдена!"}
        else:
            user.balance_ton = user.withdrawn_ton
            user.balance_gram = user.withdrawn_gram
            user.balance_not = user.withdrawn_not
            user.views_since_captcha = 0
            user.next_captcha_at = random.randint(3, 15)
            await db.commit()
            return {"success": False, "message": "Неправильно! Средства сгорели."}


@app.post("/api/campaign/create")
async def create_campaign(request: Request):
    tg = await get_user(request)
    body = await request.json()
    async with async_session() as db:
        user = (await db.execute(
            select(User).where(User.telegram_id == tg["id"])
        )).scalar_one()

        total_views = int(body.get("total_views", 0))
        if total_views <= 0:
            return {"error": "Укажите просмотры"}

        cost = total_views * REWARD
        currency = body.get("currency", "TON")

        bal = {"TON": user.balance_ton, "GRAM": user.balance_gram, "NOT_MEME": user.balance_not}
        if bal.get(currency, 0) < cost:
            return {"error": f"Нужно {cost} {currency}, у вас {bal.get(currency, 0)}"}

        if currency == "TON":
            user.balance_ton -= cost
        elif currency == "GRAM":
            user.balance_gram -= cost
        else:
            user.balance_not -= cost

        user.role = "creator"
        campaign = Campaign(
            creator_id=user.id,
            title=body.get("title", "Без названия"),
            description=body.get("description", ""),
            media_url=body.get("media_url", ""),
            media_type=body.get("media_type", "text"),
            target_link=body.get("target_link", ""),
            currency=currency,
            total_views=total_views,
        )
        db.add(campaign)
        await db.commit()
        return {"success": True, "campaign_id": campaign.id, "cost": cost}


@app.get("/api/campaigns/my")
async def my_campaigns(request: Request):
    tg = await get_user(request)
    async with async_session() as db:
        user = (await db.execute(
            select(User).where(User.telegram_id == tg["id"])
        )).scalar_one()
        result = await db.execute(
            select(Campaign).where(Campaign.creator_id == user.id)
        )
        return [
            {
                "id": c.id, "title": c.title, "status": c.status,
                "total_views": c.total_views, "delivered_views": c.delivered_views,
                "clicks": c.clicks,
            }
            for c in result.scalars().all()
        ]


@app.get("/api/campaign/{campaign_id}/stats")
async def campaign_stats(campaign_id: str, request: Request):
    tg = await get_user(request)
    async with async_session() as db:
        campaign = (await db.execute(
            select(Campaign).where(Campaign.id == campaign_id)
        )).scalar_one_or_none()
        if not campaign:
            return {"error": "Не найдена"}
        feedbacks = (await db.execute(
            select(Feedback).where(Feedback.campaign_id == campaign_id)
        )).scalars().all()
        likes = sum(1 for f in feedbacks if f.liked)
        return {
            "title": campaign.title,
            "delivered": campaign.delivered_views,
            "remaining": campaign.total_views - campaign.delivered_views,
            "clicks": campaign.clicks,
            "likes": likes,
            "dislikes": len(feedbacks) - likes,
            "comments": [f.comment for f in feedbacks if f.comment][-20:],
        }


@app.post("/api/feedback")
async def submit_feedback(request: Request):
    tg = await get_user(request)
    body = await request.json()
    async with async_session() as db:
        user = (await db.execute(
            select(User).where(User.telegram_id == tg["id"])
        )).scalar_one()
        db.add(Feedback(
            campaign_id=body["campaign_id"],
            user_id=user.id,
            liked=body.get("liked", True),
            comment=body.get("comment", ""),
        ))
        await db.commit()
    return {"success": True}


@app.get("/api/balance")
async def get_balance(request: Request):
    tg = await get_user(request)
    async with async_session() as db:
        user = (await db.execute(
            select(User).where(User.telegram_id == tg["id"])
        )).scalar_one()
        return {
            "TON": user.balance_ton,
            "GRAM": user.balance_gram,
            "NOT_MEME": user.balance_not,
            "wallet": user.ton_wallet,
        }


@app.post("/api/wallet/set")
async def set_wallet(request: Request):
    tg = await get_user(request)
    body = await request.json()
    wallet = body.get("wallet", "")
    if not wallet or len(wallet) < 40:
        return {"error": "Неверный адрес"}
    async with async_session() as db:
        user = (await db.execute(
            select(User).where(User.telegram_id == tg["id"])
        )).scalar_one()
        user.ton_wallet = wallet
        await db.commit()
    return {"success": True}


@app.post("/api/withdraw")
async def withdraw(request: Request):
    tg = await get_user(request)
    body = await request.json()
    currency = body.get("currency", "TON")
    amount = float(body.get("amount", 0))

    if amount < MIN_WITHDRAW:
        return {"error": f"Минимум {MIN_WITHDRAW}"}

    async with async_session() as db:
        user = (await db.execute(
            select(User).where(User.telegram_id == tg["id"])
        )).scalar_one()

        if not user.ton_wallet:
            return {"error": "Укажите кошелёк"}

        bal = {"TON": user.balance_ton, "GRAM": user.balance_gram, "NOT_MEME": user.balance_not}
        if bal.get(currency, 0) < amount:
            return {"error": "Недостаточно средств"}

        net = amount - WITHDRAW_FEE
        if currency == "TON":
            user.balance_ton -= amount
            user.withdrawn_ton += amount
        elif currency == "GRAM":
            user.balance_gram -= amount
            user.withdrawn_gram += amount
        else:
            user.balance_not -= amount
            user.withdrawn_not += amount

        db.add(Withdrawal(
            user_id=user.id, currency=currency, amount=amount,
            fee=WITHDRAW_FEE, net_amount=net, to_wallet=user.ton_wallet,
            status="pending",
        ))
        await db.commit()
        return {"success": True, "sent": net, "fee": WITHDRAW_FEE}


@app.get("/api/history")
async def view_history(request: Request):
    tg = await get_user(request)
    async with async_session() as db:
        user = (await db.execute(
            select(User).where(User.telegram_id == tg["id"])
        )).scalar_one()
        views = await db.execute(
            select(AdView, Campaign.title, Campaign.status).join(
                Campaign, AdView.campaign_id == Campaign.id
            ).where(AdView.user_id == user.id).order_by(AdView.viewed_at.desc()).limit(50)
        )
        return [
            {
                "title": title, "currency": v.currency,
                "amount": v.amount, "viewed_at": v.viewed_at.isoformat(),
                "campaign_id": v.campaign_id, "campaign_active": status == "active",
            }
            for v, title, status in views.fetchall()
        ]


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)