# 💸 Personal Finance Management API

A full-featured backend system for managing personal finances, built with **Django**, **Django REST Framework**, **Celery**, and **Redis**. This API supports secure authentication, user-level permissions, soft deletion, scheduled tasks, and insightful transaction analytics using PostgreSQL stored procedures.

---

## 🚀 Features

### 🔐 Authentication & Security
- **JWT Authentication** with refresh token blacklisting on logout.
- **2FA Email Verification** during user registration.
- **Scoped throttling** to prevent API spamming.

### 🛡 Permissions
- **Object-level permission** for categories using `django-guardian`.
- **Custom permissions** applied on transactions.

### 🔄 Middleware
- Logs transaction details using a custom middleware (`TransactionLogMiddleware`).

### ⚙️ Signals
- Automatically assigns object-level permissions when a category is created.
- Adds new users to a default group for accessing predefined categories.

### ⚡ Redis Integration
- Used as **Celery broker** for background tasks.
- Acts as a **cache** for email verification tokens.

### ⏱ Celery & Celery Beat Tasks

Celery is used to run asynchronous and scheduled tasks:

- ✅ **Send daily email** to users with the previous day's transaction summary.
- 🧹 **Clean up blacklisted refresh tokens** from the outstanding token table.
- ❌ **Delete inactive users** who failed to complete **2FA email verification**:
  - When the 2FA token is **not found in Redis** (expired or deleted), the background task automatically deletes the inactive user from the database to avoid stale entries.

### 🧪 Validations
- Ensures valid:
  - **Transaction amounts**
  - **Category names**
  - **Transaction descriptions**

### 🔍 Filtering & Search
- Search-enabled list views for categories and transactions.

### 🗑 Soft Deletion
- Implemented for:
  - `CustomUser`
  - `Transaction`

---

## 📊 PostgreSQL Stored Procedures

This project includes custom **PostgreSQL stored functions** that efficiently analyze transaction data at the database level.

- ✅ Perform aggregated operations (e.g., totals by category, date, or type).
- ⚙️ Called directly from Django views or services for performance-optimized analytics.
- 📉 Reduces Django-side computation by offloading logic to the database.
- 📦 Improves performance for reporting and dashboard generation.

---

## 🧭 API Endpoints

### 🔑 Authentication (`/api/auth/`)

| Method | Endpoint         | Description                         |
|--------|------------------|-------------------------------------|
| POST   | `/login/`        | Obtain access and refresh tokens    |
| POST   | `/logout/`       | Logout and blacklist refresh token  |
| POST   | `/register/`     | Register new user (triggers 2FA)    |
| POST   | `/verify-email/` | Verify email for 2FA registration   |

---

### 📊 Finance API (`/api/v1/`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/transactions/` | List and create transactions |
| GET/PUT/PATCH/DELETE | `/transactions/<uuid>/` | Manage specific transaction |
| GET/POST | `/category/` | List and create categories |
| GET/PUT/PATCH/DELETE | `/category/<uuid>/` | Manage specific category |
| GET | `/balance/` | Get current balance |
| GET | `/profile/` | User profile info |
| GET | `/category-wise-expanse/` | Expenses categorized (uses stored procedure) |
| GET | `/transaction-detail/` | Transaction details by date (uses stored procedure) |
| POST | `/forgot-password/` | Request password reset |
| POST | `/reset-password/<token>/` | Reset password |

---

### 🛠 Developer Utilities (`/api/dev/`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/transactions/all` | All transactions |
| GET | `/transactions/deleted` | Soft-deleted transactions |
| POST | `/transactions/restore/<uuid>/` | Restore a soft-deleted transaction |
| DELETE | `/transactions/hard-delete/<uuid>/` | Permanently delete a transaction |
| GET | `/users/all` | All users |
| GET | `/users/deleted` | Soft-deleted users |
| POST | `/users/restore/<int>/` | Restore a soft-deleted user |

---

### 🌐 Client Pages (`/`)
| Endpoint | Description |
|----------|-------------|
| `/home/` | Homepage |
| `/category-expense-analysis/` | Visual expense analysis by category |
| `/transaction-analysis/` | Transaction analysis by date |
| `/login/` | Login page |
| `/transaction/` | List of transactions (client view) |
| `/category/` | List of categories (client view) |
| `/log/` | View transaction logs |

---

## 🛠 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/finance-api.git
cd finance-api
```

---

### 2. Set Up Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

---

### 3. Install Requirements
```bash
pip install -r requirements.txt
```

---

### 4. Create `.env` File
```bash
DB_NAME=your_db_name
DB_USER=your_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

EMAIL_HOST_USER=youremail@gmail.com
EMAIL_HOST_PASSWORD=your_app_password

ACCESS_TOKEN_LIFETIME_MIN=5
REFRESH_TOKEN_LIFETIME_MIN=60
ROTATE_REFRESH_TOKENS=True
BLACKLIST_AFTER_ROTATION=True
```

---

### 5. Apply Migrations
```bash
python manage.py migrate
```

---

### 6. Run Development Server
```bash
python manage.py runserver
```

---

## ⚙️ Running Celery and Celery Beat

### Start Redis (if not already running)
```bash
redis-server
```

---

### Start Celery Worker
```bash
celery -A core worker -l info
```

---

### Start Celery Beat Schedular
```bash
celery -A core beat -l info
```

---

## 📂 Project Structure
```bash
core/
├── authentication/       # Auth app with 2FA and JWT
├── client/               # Frontend views (HTML rendering)
├── developersOnly/       # Developer utilities and admin-only tools
├── finance/              # Core finance logic: categories,transactions
├── transactionLog/       # Custom logging middleware          
├── core/                 # Project settings, URLs, WSGI
```

--- 

## 🧩 Tech Stack

- **Frontend Templates:** Javascript + `fetch()` + DjangoTemplates + Bootstrap
- **Backend:** Django, DRF
- **Authentication:** JWT (`djangorestframework-simplejwt`)
- **Permissions:** `django-guardian` + `BasePermission`
- **Asynchronous Tasks:** Celery + Celery Beat
- **Cache & Broker:** Redis
- **Database:** PostgreSQL
- **Email:** SMTP (Gmail)
- **Env Management:** `python-dotenv`
