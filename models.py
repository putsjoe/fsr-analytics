
from datetime import datetime

from app import db

class Hit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    redisid = db.Column(db.Integer, unique=True)
    added = db.Column(db.DateTime, nullable=False)
    remote_addr = db.Column(db.String())
    referrer = db.Column(db.String())
    ua_device = db.Column(db.String())
    ua_platform = db.Column(db.String())
    ua_browser = db.Column(db.String())
    url = db.Column(db.String())
    unique = db.Column(db.Boolean, default=False)
    uid = db.Column(db.String())
    event = db.Column(db.String())
