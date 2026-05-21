# Mehnat Bot

Telegram bot for code lookup by direction and specialty.

**Flow:** User selects a direction → selects a specialty → bot shows the corresponding codes from the database.

---

## Requirements

- Python 3.12+
- PostgreSQL 14+
- pip

---

## Installation

**1. Clone and enter the project:**

```bash
git clone <repo-url>
cd telegrambot-mehnat
```

**2. Create a virtual environment:**

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate
```

**3. Install dependencies:**

```bash
pip install -r requirements.txt
```

---

## PostgreSQL Setup

**Run the setup script as the `postgres` superuser:**

```bash
psql -U postgres -f scripts/setup_db.sql
```

This creates:
- User: `mehnat_user`
- Database: `mehnat_bot`
- Extensions: `pg_trgm`, `unaccent`

> If you want a different username or password, edit `scripts/setup_db.sql` before running it, then match the values in your `.env`.

---

## Environment Configuration

**Copy the example file:**

```bash
cp .env.example .env
```

**Edit `.env` and fill in your values:**

```env
BOT_TOKEN=7123456789:AAFxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ADMIN_IDS=123456789

POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=mehnat_bot
POSTGRES_USER=mehnat_user
POSTGRES_PASSWORD=strong_password_here
```

- `BOT_TOKEN` — get from [@BotFather](https://t.me/BotFather)
- `ADMIN_IDS` — your Telegram user ID (get from [@userinfobot](https://t.me/userinfobot)). Multiple admins: `123456789,987654321`

---

## Database Migration

**Create and apply the initial migration:**

```bash
alembic revision --autogenerate -m "init"
alembic upgrade head
```

This creates all tables: `directions`, `specialties`, `position_codes`, `admin_users`.

---

## Seeding the Database

The database is populated **once** using an Excel file. The bot itself has no upload feature.

**Prepare your Excel file** with these columns (Uzbek, Russian, or English headers all work):

| kod | yo'nalish | mutaxassislik | nomi | tavsif |
|-----|-----------|---------------|------|--------|
| BM-001 | Umumiy qurilish | Bosh muhandis | | |
| BM-002 | Umumiy qurilish | Bosh muhandis | Kichik loyiha | Qo'shimcha ma'lumot |
| ET-001 | Elektr ta'minoti | Elektrik | | |

**Required columns:** `kod`, `yo'nalish`, `mutaxassislik`  
**Optional columns:** `nomi`, `tavsif`

> Directions and specialties are created automatically if they don't exist yet.

**Run the seeder:**

```bash
python scripts/seed.py path/to/your_data.xlsx
```

**Example output:**
```
────────────────────────────────────────
  Total rows : 150
  Inserted   : 148 ✅
  Duplicates : 2   ⚠️
  Errors     : 0   ❌
────────────────────────────────────────
```

If there are errors, the row number and reason are printed so you can fix the source file and re-run. Duplicates are silently skipped.

---

## Running the Bot

```bash
python main.py
```

The bot starts in **polling mode** by default. You should see:

```
INFO | Bot started: @your_bot_username (id=...)
INFO | Environment: development
```

---

## User Flow

```
/start
  └─► Choose direction  (e.g. "Umumiy qurilish")
        └─► Choose specialty  (e.g. "Bosh muhandis")
              └─► View codes  (e.g. "BM-001")
                    └─► Pagination if multiple codes
                    └─► 🔄 New search  → back to directions
```

---

## Admin Panel

Send `/start` with an account whose Telegram ID is listed in `ADMIN_IDS`.

The admin panel shows **Statistics**: total code count broken down by direction.

---

## Supported Excel Column Headers

The seeder accepts headers in any of these languages:

| Field | Uzbek | Russian | English |
|-------|-------|---------|---------|
| Code | `kod`, `pozitsiya kodi` | `код` | `code`, `position code` |
| Direction | `yo'nalish`, `yunalish` | `направление` | `direction` |
| Specialty | `mutaxassislik` | `специальность` | `specialty`, `speciality` |
| Name | `nomi` | `название`, `наименование` | `name` |
| Description | `tavsif`, `izoh` | `описание` | `description` |

---

## Project Structure

```
telegrambot-mehnat/
├── main.py                        # Entry point
├── alembic.ini                    # Migration config
├── requirements.txt
├── .env.example
│
├── app/
│   ├── bot.py                     # Bot + dispatcher factory
│   ├── core/
│   │   ├── config.py              # Settings from .env
│   │   ├── database.py            # Async engine and session
│   │   └── logger.py              # Loguru configuration
│   ├── models/                    # SQLAlchemy ORM models
│   │   ├── direction.py
│   │   ├── speciality.py
│   │   ├── position_code.py
│   │   └── admin_user.py
│   ├── schemas/                   # Pydantic DTOs
│   ├── repositories/              # DB query layer
│   ├── services/                  # Business logic
│   ├── handlers/
│   │   ├── common/start.py        # /start command
│   │   ├── user/search.py         # Direction → specialty → codes
│   │   └── admin/stats.py         # Admin statistics
│   ├── keyboards/inline.py        # Inline keyboards
│   ├── middlewares/               # DB session, logging
│   └── filters/admin.py           # IsAdmin filter
│
├── migrations/                    # Alembic migrations
├── scripts/
│   ├── seed.py                    # One-time Excel seeder
│   └── setup_db.sql               # PostgreSQL setup
└── logs/                          # Auto-created on first run
```

---

## Logs

Logs are written to the `logs/` directory (auto-created):

| File | Contents |
|------|----------|
| `logs/bot_YYYY-MM-DD.log` | All INFO+ events, rotated daily |
| `logs/errors.log` | Errors only, kept 90 days |

Console output is also shown while the bot is running.

---

## Common Issues

**`sqlalchemy.exc.OperationalError: could not connect`**  
→ Check that PostgreSQL is running and `.env` credentials match `setup_db.sql`.

**`aiogram.exceptions.TelegramUnauthorizedError`**  
→ `BOT_TOKEN` in `.env` is wrong or the bot was deleted. Get a new token from @BotFather.

**Seed script: `Direction not found` errors**  
→ The direction name in the Excel file doesn't match any existing direction. The seeder creates directions automatically, so this only happens if the row's `yo'nalish` cell is empty.

**`alembic.util.exc.CommandError: Can't locate revision`**  
→ Run `alembic upgrade head` to apply all pending migrations before starting the bot.
