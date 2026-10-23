# روال شاخه، تست و انتشار

این روال برای هر feature و bug fix اجرا می‌شود. هیچ تغییری مستقیم روی `main` انجام نمی‌شود.

## شروع کار

ابتدا branch و worktree را بررسی کن:

```sh
git branch --show-current
git status --short
```

اگر worktree تمیز است، `main` را به‌روز کن و branch تازه بساز:

```sh
git fetch origin
git switch main
git pull --ff-only origin main
git switch -c feat/<short-topic>
```

برای bug fix از `fix/<short-topic>` و برای مستندات از `docs/<short-topic>` استفاده کن. اگر checkout محلی `main` وجود ندارد:

```sh
git switch --track -c main origin/main
```

اگر worktree کثیف است، تغییرهای موجود را پاک، stash یا جابه‌جا نکن. اگر همان کار در حال انجام روی یک branch غیر-main است، همان را ادامه بده؛ اگر مالکیت/ارتباط تغییرها روشن نیست، پیش از جابه‌جایی یا commit از مالک بپرس. روی `main` ویرایش نکن.

## تست محلی

`dev_run.py` و `.env` خصوصی و local-only هستند؛ آن‌ها را در Git نگذار و token/proxy را در پیام یا log منتشر نکن.

```sh
docker compose up -d db
source .venv/bin/activate
alembic upgrade head
PYTHONPATH=src python dev_run.py
```

از bot token جداگانهٔ تست استفاده کن. `pgdata` volume پایدار است؛ DB را پاک یا recreate نکن. `docker compose up -d db` فقط دیتابیس را بالا می‌آورد و image بات را rebuild نمی‌کند. Migration را فقط وقتی `DATABASE_URL` به DB تست/محلی اشاره می‌کند اجرا کن. برنامهٔ Compose migration را در startup انجام می‌دهد؛ چون launcher محلی خصوصی است، اجرای خودکار migration توسط `dev_run.py` تأیید نشده است.

تست Docker لازم است وقتی Dockerfile، runtime dependencies، Compose یا خود image تغییر کرده باشد:

```sh
docker compose up -d --build
docker compose logs --tail=100 bot
```

## Commit و Pull Request

بعد از تست و بازبینی:

```sh
git status --short
git diff --check
git add <files-for-this-change>
git commit -m "feat: describe the change"
git push -u origin feat/<short-topic>
```

PR را از feature branch به `main` باز کن. پس از CI/review آن را merge کن؛ مستقیم به `main` push یا force-push نکن. Agent به‌صورت پیش‌فرض commit، push، merge یا tag نمی‌زند؛ دستورهای دقیق و branch واقعی را در تحویل نهایی می‌دهد.

## Tag و استقرار سرور

پس از merge و تأیید نسخه، version پروژه را به‌روز کن و tag annotated بساز:

```sh
git switch main
git pull --ff-only origin main
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z
```

روی سرور ابتدا backup خارج از repository بگیر و تنظیمات لازم را در `.env` به‌روز کن. سپس tag تأییدشده را deploy کن:

```sh
cd /path/to/BOOKzMA
git fetch origin --tags
git switch --detach vX.Y.Z
docker compose up -d --build bot
docker compose ps
docker compose logs --tail=100 bot
```

این دستور image سرویس bot را rebuild می‌کند و volume دیتابیس را حفظ می‌کند. Migrationها در startup اجرا می‌شوند. Logها را برای موفقیت migration، `polling` و `reminder loop started` بررسی کن؛ فقط یک نمونه با bot token production باید polling کند. اگر startup/migration شکست خورد، rollout را متوقف کن؛ downgrade/restore را بدون backup و بررسی سازگاری انجام نده. برای deploy `docker compose down -v` نزن.

## موارد الزامی در پایان هر کار

- branch واقعی، dirty/uncommitted بودن worktree و فایل‌های تغییرکرده.
- تست‌ها و checkهای واقعاً اجراشده و مواردی که اجرا نشده‌اند.
- دستور اجرای bot محلی، نیاز یا عدم نیاز به DB start، migration محلی و rebuild Docker.
- فرمان‌های متناسب commit/push/PR/merge/tag؛ هیچ placeholderی را با branch/version حدسی جایگزین نکن.
- مراحل سرور پس از merge/tag، backup و migration لازم، و نام envهای لازم بدون افشای secret.