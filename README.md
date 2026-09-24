# 📋 Clipboard

A simple temporary clipboard web application built with **Flask** and **PostgreSQL**.

The application allows users to store text temporarily and share it using a unique **6-digit numeric ID**. Clipboard data automatically expires after **1 hour**.

## ✨ Features

- Create a temporary clipboard
- Generate a unique 6-digit numeric ID
- Retrieve clipboard data using the ID
- Clipboard data expires after 1 hour
- Automatic cleanup of expired clipboard records
- Persistent PostgreSQL storage using Neon
- Timezone-aware UTC expiration handling
- Bootstrap-based frontend
- Jinja2 template inheritance
- Health-check endpoint for uptime monitoring
- Collision handling for generated IDs
- Production deployment with Gunicorn

## 🛠️ Technologies

| Technology | Purpose |
|---|---|
| Python | Programming language |
| Flask | Web framework |
| Flask-SQLAlchemy | Database ORM |
| SQLAlchemy | Database abstraction |
| PostgreSQL | Database |
| Neon | Hosted PostgreSQL |
| Psycopg 3 | PostgreSQL driver |
| Bootstrap | Frontend UI |
| Jinja2 | Server-side templating |
| APScheduler | Automatic cleanup |
| Gunicorn | Production WSGI server |
| Render | Deployment |

## 📁 Project Structure

```text
web-clipboard/
│
├── app.py
├── database.py
├── models.py
├── requirements.txt
├── .gitignore
├── README.md
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── created.html
│   └── clipboard.html
│
└── static/
    └── css/
        └── style.css
```

## ⚙️ How It Works

### 1. Create a Clipboard

The user enters text and submits it.

The application generates a random 6-digit numeric ID.

Example:

```text
583214
```

The clipboard record contains:

```text
ID
Content
Created At
Expires At
```

The expiration time is set to one hour after creation.

### 2. Retrieve a Clipboard

The user can retrieve the clipboard by visiting:

```text
/583214
```

The application looks up the ID in the database and checks its expiration time.

If the clipboard is still valid, its content is displayed.

If it has expired, the record is deleted and the user receives:

```text
Clipboard expired
```

If the ID does not exist, the application returns:

```text
Clipboard not found
```

### 3. Automatic Cleanup

APScheduler runs a cleanup task periodically.

The cleanup task finds records where:

```text
expires_at <= current UTC time
```

and removes them from the database.

The application also checks expiration whenever a clipboard is requested. Therefore, an expired clipboard is not displayed even if the background cleanup task has not run yet.

## 🔢 Clipboard ID Generation

Clipboard IDs are generated using Python's `secrets` module.

Each ID is a random 6-digit number in the range:

```text
100000 - 999999
```

If the generated ID already exists, PostgreSQL reports a unique-violation error.

The application then:

1. Rolls back the failed transaction.
2. Generates another 6-digit ID.
3. Attempts the insert again.

Only the duplicate/unique-violation condition is retried. Other database errors are raised normally.

## ⏱️ Expiration

Clipboard timestamps use timezone-aware UTC datetimes.

Example:

```text
Created:
2026-09-23 10:00:00 UTC

Expires:
2026-09-23 11:00:00 UTC
```

Using timezone-aware UTC timestamps prevents errors caused by comparing timezone-naive and timezone-aware datetime objects.

## 🧩 Templates

The application uses **Jinja2 template inheritance**.

`base.html` contains the common page structure and is extended by the other templates.

For example:

```jinja2
{% extends "base.html" %}
```

This avoids repeating common HTML such as the page layout, navigation, Bootstrap imports, and other shared elements.

## 🔐 Environment Variables

Create a `.env` file for local development:

```env
DATABASE_URL=your_neon_postgresql_connection_string
```

The `.env` file contains sensitive database credentials and should not be committed to GitHub.

## 🚀 Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/rootsh-dev/web-clipboard.git
cd web-clipboard
```

### 2. Create a virtual environment

```bash
python -m venv env
```

### 3. Activate the virtual environment on Windows

```bash
env\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure the database

Create a `.env` file in the project root:

```env
DATABASE_URL=your_neon_connection_string
```

### 6. Start the application

```bash
python app.py
```

The application will be available at:

```text
http://127.0.0.1:5000
```

## 🏥 Health Check

The application provides a health-check endpoint:

```text
/health
```

For local development:

```text
http://127.0.0.1:5000/health
```

A successful request returns:

```text
OK
```

This endpoint can be used by uptime-monitoring services such as UptimeRobot.

## ☁️ Deployment

The application can be deployed on **Render** with **Neon PostgreSQL** for persistent database storage.

### Build Command

```bash
pip install -r requirements.txt
```

### Start Command

```bash
gunicorn app:app
```

### Environment Variable

Add the following environment variable in Render:

```text
DATABASE_URL
```

Set its value to your Neon PostgreSQL connection string.

The local `.env` file should not be uploaded to Render or committed to the repository.

## 📄 License

MIT — see [LICENSE](LICENSE).
