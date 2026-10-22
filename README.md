# کتابخونه مرجع

ربات تلگرام برای ثبت مطالعهٔ روزانه، پیگیری استریک و یادآوری. هر روز مطالعه‌ات را ثبت کن و خلاصهٔ هفتگی‌ات را ببین.

بخش زیادی از پروژه وایب کد شده است.

## اجرا

برای اجرای برنامه داخل Docker به Docker Compose نیاز داری؛ نسخهٔ Python پروژه برای توسعهٔ محلی 3.12 است.

```bash
cp .env.sample .env
```

مقادیر `BOT_TOKEN` و `POSTGRES_PASSWORD` را در `.env` قرار بده، سپس:

```bash
docker compose up -d --build
```

سرویس FastAPI روی پورت `8000` در دسترس است و مستند تعاملی API در `/docs` قرار دارد.

## اتصال وب‌سایت

برای ورود وب‌سایت، Telegram Web App `initData` را به `POST /api/v1/auth/telegram` بفرست. پاسخ شامل access token یک‌ساعته است؛ آن را در درخواست‌های بعدی با هدر `Authorization: Bearer <token>` بفرست. شناسهٔ کاربر از دادهٔ امضاشدهٔ تلگرام گرفته می‌شود و API شناسهٔ دلخواه کاربر را نمی‌پذیرد.

Endpointهای نسخهٔ اول API:

- `GET /health`
- `GET /api/v1/me` و `PUT /api/v1/me/timezone`
- `POST /api/v1/me/read`
- `GET /api/v1/me/weekly-summary`
- `GET`, `POST` و `DELETE /api/v1/me/reminders`

اگر وب‌سایت روی origin دیگری است، originهای مجاز را با جداکنندهٔ کاما در `WEB_ORIGINS` تنظیم کن. برای محیط production از HTTPS استفاده کن و `initData` را در مرورگر ذخیره نکن؛ پس از دریافت access token، دادهٔ خام را دور بینداز.

## داده و migration

در شروع سرویس، migrationهای Alembic به‌صورت خودکار اجرا می‌شوند. migration نسخهٔ `0002` فقط وضعیت تلاش مجدد یادآورها را اضافه می‌کند و اطلاعات قبلی را حذف نمی‌کند.

## توسعه با ابزارهای هوش مصنوعی

پیش از هر تغییر، [AGENTS.md](AGENTS.md) و سندهای مرتبط در `docs/` را بخوان. تفاوت محیط محلی و Docker را در [docs/LOCAL_DEV.md](docs/LOCAL_DEV.md) ببین؛ فایل محلی `dev_run.py` را به Git اضافه نکن.
docker compose up -d --build
