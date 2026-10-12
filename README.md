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
```

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
| `GET` | `/api/me/` | Current user profile | Token Required |

### Assortment & Catalog
| Verb | Route | Description | Auth Level |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/categories/` | Explore beer categories | Public |
| `GET` | `/api/items/` | Browse drinks catalog | Public |
| `POST` | `/api/items/` | Add item to catalog | Staff / Admin |
| `GET` | `/api/items/<id>/` | Detailed drink specs | Public |
| `PATCH` | `/api/items/<id>/` | Modify price/availability | Staff / Admin |
| `DELETE` | `/api/items/<id>/` | Remove item | Staff / Admin |

### Orders & Checkout
| Verb | Route | Description | Auth Level |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/orders/` | User order history | Token Required |
| `POST` | `/api/orders/` | Place a new order | Token Required |
| `GET` | `/api/orders/<id>/` | View order progress | Order Owner / Staff |
| `PATCH` | `/api/orders/<id>/` | Update item count/status | Order Owner / Staff |
| `DELETE` | `/api/orders/<id>/` | Cancel order | Order Owner / Staff |

---

## 🔍 Query Parameters

Filter and paginate `/api/items/` via standard query params:

* **Keyword Search:** `?search=Lviv` (searches title and brew description)
* **Category Filter:** `?category=1` (filter by category ID)
* **Sorting:** `?ordering=-price` (highest price first) or `?ordering=name`
* **Pagination:** `?page=1` (default limit: 10 entries per payload)