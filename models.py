from database import db
from datetime import datetime, timezone


class Clipboard(db.Model):
    id = db.Column(db.String(6), primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    expires_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False
    )