# Personal Finance Management API

## Overview
The **Personal Finance Management API** is a backend service designed to help users track and manage their financial transactions efficiently. It provides secure authentication, transaction logging, balance tracking, and reporting features to assist users in managing their income and expenses.

## Tech Stack
- **Backend**: Python, Django (Django REST Framework)
- **Database**: PostgreSQL
- **Caching**: Redis
- **Task Queue**: Celery
- **Authentication**: JWT (JSON Web Tokens)

## Setup & Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/DevarshSimform/finance-manager.git
   cd finance-manager
   ```
2. Create a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   venv\Scripts\activate  # On Windows
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Set up environment variables in a `.env` file:
   ```plaintext
   DB_NAME=your_db_name
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_HOST=your_db_host
   DB_PORT=5432
   ```
5. Apply migrations:
   ```sh
   python manage.py migrate
   ```
6. Run the development server:
   ```sh
   python manage.py runserver
   ```


---
Project is under maintenance for now
