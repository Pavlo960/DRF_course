# 🍺 BeerHub REST API

Backend engine powering pub menu management and draft beer ordering. Built with Django REST Framework, containerized with Docker, and secured using JWT token pairs.

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Django](https://img.shields.io/badge/Django-6.x-092E20?logo=django)
![DRF](https://img.shields.io/badge/DRF-SimpleJWT-red)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-4169E1?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-WSL2-2496ED?logo=docker)

---

## ⚡ Quick Start

### Option A: Docker + PostgreSQL (Recommended)

Make sure Docker Desktop is up and running. Run all commands from the `beerhub/` folder (where `docker-compose.yml` is).

`docker compose` starts two services:

| Service | What it is | Details |
| :--- | :--- | :--- |
| `db` | PostgreSQL 17 | database `app_db`, user `app_user`, password `app_pass`; data persists in the `postgres_data` volume; `pg_isready` healthcheck |
| `web` | Django API on port `8000` | connects via `DATABASE_URL=postgres://app_user:app_pass@db:5432/app_db`; starts only after `db` is healthy and runs `migrate` on every start |

```bash
# 1. Prepare environment variables
cp .env.example .env    # On Windows: copy .env.example .env

# 2. Build and run containers (-d = in the background)
docker compose up --build -d

# 3. Fill the database — sample data and/or your own admin
docker compose exec web python manage.py seed
docker compose exec web python manage.py createsuperuser
```

> API base address: **`http://localhost:8000/api/`**

Useful commands:

```bash
docker compose logs -f web      # follow Django logs
docker compose down             # stop containers (data is kept)
docker compose down -v          # stop and DELETE the database volume
```

#### Moving existing data from SQLite to PostgreSQL

```bash
# locally (venv, no DATABASE_URL -> uses db.sqlite3)
python manage.py migrate
python manage.py dumpdata --exclude contenttypes --exclude auth.permission --exclude sessions --exclude admin.logentry -o data.json

# into PostgreSQL in Docker (the project folder is mounted into the container)
docker compose up -d
docker compose exec web python manage.py loaddata data.json
```

> `data.json` contains users with password hashes — it is git-ignored, don't commit it.

#### Looking into the database (psql)

```bash
docker compose exec db psql -U app_user -d app_db -c "\dt"
docker compose exec db psql -U app_user -d app_db -c "SELECT * FROM pub_order;"
```

Or open an interactive session with `docker compose exec db psql -U app_user -d app_db` and type commands one by one (`\dt`, `SELECT ...;`, `\q` to exit). Tables are named `pub_category`, `pub_menuitem`, `pub_order`, `auth_user`.

---

### Option B: Local Environment

Without `DATABASE_URL` in `.env` the app uses a local SQLite file (`db.sqlite3`). To use PostgreSQL locally, set e.g. `DATABASE_URL=postgres://app_user:app_pass@localhost:5432/app_db` (for the Docker `db` service this also needs `ports: ["5432:5432"]` added to it in `docker-compose.yml`).

```bash
# Clone & navigate
git clone [https://github.com/Pavlo960/DRF_course.git](https://github.com/Pavlo960/DRF_course.git)
cd DRF_course/beerhub

# Initialize virtual environment
python -m venv .venv
source .venv/bin/activate       # On Windows: .venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt

# Configure settings & migrate
copy .env.example .env          # Linux/macOS: cp .env.example .env
python manage.py migrate
python manage.py seed
python manage.py runserver

# Run tests
python manage.py test pub
```

> ⚠️ `seed` creates a demo superuser **`barman` / `beer12345`** (and resets its password on every run). It is meant for local development only — never run it against a production database.

---

## 🔐 Security & Auth Flow

The API uses stateless **JWT (JSON Web Tokens)**:
* `POST /api/token/` yields short-lived `access` and long-lived `refresh` tokens.
* Include access token in subsequent HTTP requests:
  ```http
  Authorization: Bearer <your_access_token>
  ```
* Expired or missing tokens immediately return `401 Unauthorized`.

---

## 📋 Route Map

### Core & Auth
| Verb | Route | Description | Auth Level |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/token/` | Issue new token pair | Public |
| `POST` | `/api/token/refresh/` | Renew expired access token | Public |
| `POST` | `/api/token/verify/` | Validate token status | Public |

### Assortment & Catalog
| Verb | Route | Description | Auth Level |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/categories/` | Explore beer categories | Public |
| `GET` | `/api/menu-items/` | Browse drinks catalog | Public |
| `POST` | `/api/menu-items/` | Add item to catalog | Staff / Admin |
| `GET` | `/api/menu-items/<id>/` | Detailed drink specs | Public |
| `PUT` / `PATCH` | `/api/menu-items/<id>/` | Modify price/availability | Staff / Admin |
| `DELETE` | `/api/menu-items/<id>/` | Remove item | Staff / Admin |

### Orders & Checkout
| Verb | Route | Description | Auth Level |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/orders/` | Own orders (staff sees all) | Token Required |
| `GET` | `/api/orders/my/` | Only the current user's orders | Token Required |
| `POST` | `/api/orders/` | Place a new order | Token Required |
| `GET` | `/api/orders/<id>/` | Order details | Order Owner / Staff |
| `PUT` / `PATCH` | `/api/orders/<id>/` | Change item or volume | Order Owner / Staff |
| `DELETE` | `/api/orders/<id>/` | Cancel order | Order Owner / Staff |

Order body: `{"menu_item": 1, "volume": 0.5, "customer_name": "John"}` — `volume` must be one of `0.25`, `0.5`, `1`, `1.5`, `2`; `customer_name` is optional (defaults to the user's name). Unavailable menu items can't be ordered.

* The menu price is copied into the order (`price_per_liter`) when it is placed, so later menu price changes don't affect existing orders.
* Order `status`: `new` → `preparing` → `served` (or `cancelled`). Only staff can change it, e.g. `PATCH {"status": "preparing"}`.
* Customers can edit or delete their order only while it is `new`; after that the API returns `403`.

---

## 🔍 Query Parameters

`/api/menu-items/`:

* **Keyword Search:** `?search=Lviv` (searches name and description)
* **Category Filter:** `?category=1` (by category ID) or `?category=draft` (by part of the name)
* **Availability:** `?available=true`
* **Sorting:** `?ordering=-price_per_liter` (highest price first) or `?ordering=name`

`/api/orders/`:

* **Search:** `?search=ale` (customer name or menu item name)
* **Filters:** `?volume=0.5`, `?customer_name=john`, `?status=new`
* **Sorting:** `?ordering=created_at` (default `-created_at`) or `?ordering=volume`