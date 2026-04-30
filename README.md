# 🎓 Donish AI — Telegram Mini App

AI-репетитор для таджикской молодёжи. Работает прямо внутри Telegram.

## 📱 Что умеет

- 📚 6 предметов: Математика, Физика, Английский, IT/Python, Вайб кодинг, ИИ и CV
- 📸 Фото → Решение (фотографируешь задачу — AI решает)
- 🇷🇺 Русский + 🇹🇯 Таджикский язык
- 🏆 Прогресс ученика сохраняется
- 4-шаговая система: Объяснение → Примеры → Практика → Проверка

---

## 🚀 Запуск за 30 минут

### Шаг 1 — Создай бота в Telegram
1. Напиши @BotFather в Telegram
2. Отправь `/newbot`
3. Придумай имя: `Donish AI`
4. Придумай username: `donishai_bot`
5. Скопируй токен — он выглядит так: `1234567890:ABCdef...`

### Шаг 2 — Загрузи на GitHub
1. Зайди на github.com → New repository → `donish-ai`
2. Загрузи файл `index.html`

### Шаг 3 — Задеплой на Vercel (бесплатно)
1. Зайди на vercel.com
2. Import → выбери твой GitHub репозиторий
3. Deploy → получи ссылку: `donish-ai.vercel.app`

### Шаг 4 — Подключи Mini App к боту
1. Напиши @BotFather → `/mybots` → выбери бота
2. `Bot Settings` → `Menu Button` → `Configure menu button`
3. Вставь URL: `https://donish-ai.vercel.app`
4. Название кнопки: `🎓 Donish AI`

### Шаг 5 — Подключи AI (Claude API)
1. Зайди на console.anthropic.com
2. Получи API ключ
3. В Vercel → Settings → Environment Variables
4. Добавь: `ANTHROPIC_API_KEY` = твой ключ

### Шаг 6 — Запусти бота (опционально)
```bash
pip install python-telegram-bot
# В bot.py замени BOT_TOKEN на свой токен
# В bot.py замени WEBAPP_URL на свой vercel URL
python bot.py
```

---

## 💰 Стоимость

| Сервис | Цена |
|--------|------|
| Telegram Bot | Бесплатно |
| GitHub | Бесплатно |
| Vercel (хостинг) | Бесплатно |
| Anthropic API (AI) | ~$5-10/месяц |
| **Итого старт** | **$0–10** |

---

## 📁 Структура

```
donish-ai/
├── index.html    ← Всё приложение (Mini App)
├── bot.py        ← Telegram бот
└── README.md     ← Эта инструкция
```

---

## 🗺 Роадмап

- [x] MVP — 6 предметов, 2 языка
- [x] Фото → Решение
- [x] Прогресс ученика
- [ ] Claude API интеграция (реальный AI)
- [ ] Авторизация через Telegram
- [ ] Supabase — синхронизация прогресса
- [ ] Freemium модель
- [ ] iOS + Android приложение

---

Сделано с ❤️ для таджикской молодёжи