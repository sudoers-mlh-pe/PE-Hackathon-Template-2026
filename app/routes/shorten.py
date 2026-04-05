from flask import Blueprint, jsonify, request
from playhouse.shortcuts import model_to_dict
from app.models.url import URL
from app.redis import redis
import validators
import os

shorten_bp = Blueprint("shorten", __name__)

@shorten_bp.route("/shorten", methods=['POST'])
def shorten():
    long_url = request.json.get('url')
    
    # Check if valid
    if not long_url or not is_valid_url(long_url):
        return jsonify({"error": "invalid URL"}), 400
    
    # Check if redis cached the long url
    existing_code = redis.get(f"long:{long_url}")
    if existing_code:
        print("⚡ Redis found existing long URL!")
        return jsonify({"short_url": f"{os.environ.get("APP_URL", "http://127.0.0.1:5000")}/{existing_code}", "cached": True})
    
    # Check if postgres already has the long url
    db_entry = URL.get_or_none(URL.full_url == long_url)
    if db_entry:
        print("🐢 Postgres found existing long URL!")
        # Put it back in Redis for next time
        redis.setex(f"long:{long_url}", 3600, db_entry.short_code)
        redis.setex(db_entry.short_code, 3600, long_url)
        return jsonify({"short_url": f"{os.environ.get("APP_URL", "http://127.0.0.1:5000")}/{db_entry.short_code}"})
    
    # Create new record if not in redis and postgres URL table
    code = URL.generate_code()
    URL.create(full_url=long_url, short_code=code)
    
    # Cache code to redis
    redis.setex(f"long:{long_url}", 3600, code)
    redis.setex(code, 3600, long_url)
    
    return jsonify({"short_url": f"{os.environ.get("APP_URL", "http://127.0.0.1:5000")}/{code}"}), 201

def is_valid_url(url):
    # This handles schemes, dots, TLD lengths, and weird characters automatically
    return validators.url(url)