"""
Donish AI — Backend (FastAPI)
Авторизация через Telegram + Supabase база данных

Установка:
pip install fastapi uvicorn supabase anthropic python-dotenv

Запуск:
uvicorn main:app --reload --port 8000
"""

import os
import hashlib
import hmac
import json
from datetime import date
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Donish AI API")

# CORS — разрешаем запросы с Netlify
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшне замени на твой netlify URL
    allow_methods=["*"],
    allow_headers=["*"],
)

# Клиенты
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)
anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
BOT_TOKEN = os.getenv("BOT_TOKEN")


# ===================== МОДЕЛИ =====================
class TelegramUser(BaseModel):
    id: int
    first_name: str
    last_name: str = ""
    username: str = ""
    language: str = "ru"

class AskRequest(BaseModel):
    user_id: int
    subject: str
    topic: str
    prompt: str
    lang: str = "ru"

class PhotoRequest(BaseModel):
    user_id: int
    subject: str
    image_base64: str
    lang: str = "ru"

class ProgressRequest(BaseModel):
    user_id: int
    subject_id: str
    topic: str

class StatsRequest(BaseModel):
    user_id: int
    photos_solved: bool = False


# ===================== АВТОРИЗАЦИЯ TELEGRAM =====================
def verify_telegram_data(init_data: str) -> dict:
    """Проверяет подлинность данных от Telegram WebApp"""
    try:
        params = dict(x.split('=', 1) for x in init_data.split('&'))
        hash_value = params.pop('hash', '')
        data_check = '\n'.join(f"{k}={v}" for k, v in sorted(params.items()))
        secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
        expected = hmac.new(secret_key, data_check.encode(), hashlib.sha256).hexdigest()
        if hmac.compare_digest(expected, hash_value):
            user_data = json.loads(params.get('user', '{}'))
            return user_data
        return {}
    except Exception:
        return {}


# ===================== РОУТЫ =====================

@app.get("/")
async def root():
    return {"status": "Donish AI API работает! 🎓"}


@app.post("/auth")
async def auth_user(user: TelegramUser):
    """Регистрация/вход пользователя через Telegram"""
    try:
        # Upsert пользователя
        supabase.table("users").upsert({
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "language": user.language,
            "last_seen": "now()"
        }).execute()

        # Создаём статистику если нет
        existing = supabase.table("stats").select("*").eq("user_id", user.id).execute()
        if not existing.data:
            supabase.table("stats").insert({
                "user_id": user.id,
                "topics_done": 0,
                "photos_solved": 0,
                "streak": 0
            }).execute()

        # Получаем прогресс
        progress = supabase.table("progress").select("subject_id, topic").eq("user_id", user.id).execute()
        stats = supabase.table("stats").select("*").eq("user_id", user.id).execute()

        return {
            "success": True,
            "user": {"id": user.id, "name": user.first_name},
            "progress": progress.data,
            "stats": stats.data[0] if stats.data else {}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask")
async def ask_ai(req: AskRequest):
    """Задать вопрос Claude AI"""
    try:
        system_prompt = f"""Ты Donish AI — лучший AI-репетитор для учеников Таджикистана.
Предмет: {req.subject}. Тема: {req.topic}.
{'Отвечай на русском языке.' if req.lang == 'ru' else 'Танҳо ба забони тоҷикӣ ҷавоб деҳ.'}
Объясняй просто, как лучший учитель. Используй эмодзи. До 200 слов."""

        response = anthropic.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=800,
            system=system_prompt,
            messages=[{"role": "user", "content": req.prompt}]
        )

        answer = response.content[0].text

        # Сохраняем в историю
        supabase.table("history").insert({
            "user_id": req.user_id,
            "subject_id": req.subject,
            "topic": req.topic,
            "question": req.prompt[:500]
        }).execute()

        return {"success": True, "answer": answer}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/photo")
async def analyze_photo(req: PhotoRequest):
    """Анализ фото задачи через Claude Vision"""
    try:
        # Убираем data:image/...;base64, префикс
        img_data = req.image_base64.split(",")[-1]

        prompt = f"""Ты Donish AI. {'Отвечай на русском.' if req.lang == 'ru' else 'Ба тоҷикӣ ҷавоб деҳ.'}

На фото задача по предмету: {req.subject}.

Реши её шаг за шагом:
1. Прочитай условие задачи
2. Определи что дано и что найти
3. Реши подробно каждый шаг
4. Напиши ответ

Используй эмодзи, объясняй понятно для школьника."""

        response = anthropic.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": img_data
                        }
                    },
                    {"type": "text", "text": prompt}
                ]
            }]
        )

        return {"success": True, "answer": response.content[0].text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/progress/save")
async def save_progress(req: ProgressRequest):
    """Сохранить пройденную тему"""
    try:
        supabase.table("progress").upsert({
            "user_id": req.user_id,
            "subject_id": req.subject_id,
            "topic": req.topic
        }).execute()

        # Обновляем статистику
        stats = supabase.table("stats").select("*").eq("user_id", req.user_id).execute()
        if stats.data:
            s = stats.data[0]
            today = str(date.today())
            streak = s['streak']
            if s.get('last_active_date') != today:
                streak += 1
            supabase.table("stats").update({
                "topics_done": s['topics_done'] + 1,
                "streak": streak,
                "last_active_date": today
            }).eq("user_id", req.user_id).execute()

        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/progress/{user_id}")
async def get_progress(user_id: int):
    """Получить прогресс пользователя"""
    try:
        progress = supabase.table("progress").select("subject_id, topic, completed_at").eq("user_id", user_id).execute()
        stats = supabase.table("stats").select("*").eq("user_id", user_id).execute()
        return {
            "progress": progress.data,
            "stats": stats.data[0] if stats.data else {}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/stats/photo")
async def photo_solved(req: StatsRequest):
    """Записать что фото было решено"""
    try:
        stats = supabase.table("stats").select("photos_solved").eq("user_id", req.user_id).execute()
        if stats.data:
            supabase.table("stats").update({
                "photos_solved": stats.data[0]['photos_solved'] + 1
            }).eq("user_id", req.user_id).execute()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
