# نصب روی سرور

## اولین بار

Docker و docker compose رو نصب کن، بعد:

```bash
git clone <آدرس ریپو> && cd BOOKzMA
cp .env.sample .env
nano .env        # BOT_TOKEN و POSTGRES_PASSWORD
docker compose up -d --build
docker compose logs --tail=30 bot
```

سرویس FastAPI داخل کانتینر روی پورت `8000` بالا می‌آید؛ روی میزبان فقط از `127.0.0.1:8000` در دسترس است. برای دسترسی عمومی وب‌سایت، آن را پشت reverse proxy با HTTPS قرار بده. مستند تعاملی API در `/docs` است.

توی لاگ باید `reminder loop started` و شروع polling را ببینی. migrationهای Alembic قبل از اجرای برنامه خودکار اجرا می‌شوند.

قبلش مطمئن شو تنظیمات کانال و دسترسی ربات را در `.env` درست کرده‌ای و ربات نسخهٔ لوکال (با همین توکن) خاموشه.

## آپدیت

```bash
git pull
docker compose up -d --build
```

migrationها موقع بالا اومدن ربات خودشون اجرا می‌شن.

## بکاپ

```bash
docker compose exec -T db pg_dump -U bookzma bookzma | gzip > backup-$(date +%F).sql.gz
```

بکاپ رو جایی غیر از همین سرور هم نگه دار. برای زمان‌بندی روزانه می‌تونی توی crontab بذاریش.

بازیابی روی یه دیتابیس خالی:

```bash
gunzip -c backup-2026-10-21.sql.gz | docker compose exec -T db psql -U bookzma bookzma
```

## نکته‌ها

- `docker compose down -v` دیتابیس رو پاک می‌کنه، فقط وقتی داده مهمی نداری بزنش. `docker compose down` بدون `-v` مشکلی نداره.
- `POSTGRES_PASSWORD` بعد از اولین اجرا عوض نمی‌شه. اگه مجبور شدی، رمز رو با `ALTER USER` توی خود Postgres عوض کن.
- پورت دیتابیس فقط روی `127.0.0.1:5433` باز می‌شه و از بیرون سرور قابل دسترسی نیست.
- از ربات فقط یه نمونه باید با polling اجرا بشه.
