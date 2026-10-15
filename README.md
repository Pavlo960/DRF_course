# 🍺 BeerHub REST API

Backend engine powering pub menu management and draft beer ordering. Built with Django REST Framework, containerized with Docker, and secured using JWT token pairs.

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Django](https://img.shields.io/badge/Django-6.x-092E20?logo=django)
![DRF](https://img.shields.io/badge/DRF-SimpleJWT-red)
![Docker](https://img.shields.io/badge/Docker-WSL2-2496ED?logo=docker)

---

## ⚡ Quick Start

### Option A: Docker Deployment (Recommended)

Make sure Docker Desktop is up and running.

```bash
# 1. Prepare environment variables
cp .env.example .env    # On Windows: copy .env.example .env

# 2. Build and run containers
docker compose up --build

# 3. (Optional) Load sample beers & categories
docker compose exec web python manage.py seed
```

> API base address: **`http://localhost:8000/api/`**

---

### Option B: Local Environment

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