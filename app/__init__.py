from dotenv import load_dotenv
from flask import Flask, jsonify

from app.database import init_db
from app.routes import register_routes
from app.redis import redis

def create_app():
    load_dotenv()

    app = Flask(__name__)

    init_db(app)
    
    from app import models  # noqa: F401 - registers models with Peewee
    from app.database import db
    from app.models.url import URL

    db.create_tables([URL], safe=True)
    register_routes(app)

    @app.route("/health")
    def health():
        try:
            # 1. Check Redis
            redis.ping()
            # 2. Check Database (Peewee)
            db.connect(reuse_if_open=True)
            return jsonify(status="ok"), 200
        except Exception as e:
            app.logger.error(f"Healthcheck failed: {e}")
            return {"status": "unhealthy", "reason": str(e)}, 500

    return app
