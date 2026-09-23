
import os
import secrets

from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for
)

from flask_apscheduler import APScheduler
from sqlalchemy.exc import IntegrityError

from database import db
from models import Clipboard


# ==========================================
# Load Environment Variables
# ==========================================

load_dotenv()


# ==========================================
# Flask Application
# ==========================================

app = Flask(__name__)


# ==========================================
# Database Configuration
# ==========================================

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# ==========================================
# Initialize Database
# ==========================================

db.init_app(app)


# ==========================================
# Initialize Scheduler
# ==========================================

scheduler = APScheduler()
scheduler.init_app(app)


# ==========================================
# Create Database Tables
# ==========================================

with app.app_context():
    db.create_all()


# ==========================================
# Automatic Cleanup
# ==========================================

def cleanup_expired_clipboards():

    with app.app_context():

        current_time = datetime.now(timezone.utc)

        expired_clipboards = Clipboard.query.filter(
            Clipboard.expires_at <= current_time
        ).all()

        for clipboard in expired_clipboards:

            db.session.delete(clipboard)

        db.session.commit()

        if expired_clipboards:

            print(
                f"Deleted {len(expired_clipboards)} "
                f"expired clipboard(s)"
            )


# ==========================================
# Schedule Cleanup
# ==========================================

scheduler.add_job(
    id="cleanup_expired_clipboards",
    func=cleanup_expired_clipboards,
    trigger="interval",
    minutes=1
)

scheduler.start()


# ==========================================
# Home
# ==========================================

@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        # Get submitted clipboard content
        content = request.form.get(
            "content",
            ""
        ).strip()


        # Check empty content
        if not content:

            return render_template(
                "index.html",
                error="Clipboard content cannot be empty",
                content=content
            ), 400


        # Check content size
        if len(content) > 100_000:

            return render_template(
                "index.html",
                error="Clipboard content is too large",
                content=content
            ), 413


        # ==================================
        # Generate Clipboard
        # ==================================

        while True:

            # Generate 6-digit numeric ID
            clipboard_id = str(
                secrets.randbelow(900000) + 100000
            )


            # Current timezone-aware UTC time
            created_at = datetime.now(timezone.utc)


            # Expire after one hour
            expires_at = created_at + timedelta(
                hours=1
            )


            # Create Clipboard object
            clipboard = Clipboard(
                id=clipboard_id,
                content=content,
                created_at=created_at,
                expires_at=expires_at
            )


            # Add object to current session
            db.session.add(clipboard)


            try:

                # Try inserting into PostgreSQL
                db.session.commit()

                # Insert successful
                break


            except IntegrityError as error:

                # Roll back failed transaction
                db.session.rollback()


                # PostgreSQL SQLSTATE 23505
                # means unique_violation
                if getattr(
                    error.orig,
                    "sqlstate",
                    None
                ) == "23505":

                    # ID collision
                    # Generate another ID
                    continue


                # Some other integrity error
                # Do not hide it
                raise


        # Redirect to created page
        return redirect(
            url_for(
                "created",
                clipboard_id=clipboard_id
            )
        )


    return render_template(
        "index.html"
    )


# ==========================================
# Created Clipboard Page
# ==========================================

@app.route("/created/<clipboard_id>")
def created(clipboard_id):

    return render_template(
        "created.html",
        clipboard_id=clipboard_id
    )


# ==========================================
# View Clipboard
# ==========================================

@app.route("/<clipboard_id>")
def view_clipboard(clipboard_id):

    # Find clipboard by primary key
    clipboard = db.session.get(
        Clipboard,
        clipboard_id
    )


    # Clipboard doesn't exist
    if clipboard is None:

        return "Clipboard not found", 404


    # Current timezone-aware UTC time
    current_time = datetime.now(timezone.utc)


    # Check expiration
    if current_time >= clipboard.expires_at:

        db.session.delete(clipboard)

        db.session.commit()

        return "Clipboard expired"


    # Clipboard is still valid
    return render_template(
        "clipboard.html",
        clipboard=clipboard
    )


# ==========================================
# Endpoint for Health Check [UpTIME Bot]
# ==========================================

@app.route("/health")
def health():
    return "OK", 200


# ==========================================
# Run Application
# ==========================================

if __name__ == "__main__":

    app.run(
        debug=False
    )
