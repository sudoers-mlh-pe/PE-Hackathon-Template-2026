from flask import Blueprint, jsonify, redirect
from playhouse.shortcuts import model_to_dict

from app.models.url import URL
from app.redis import redis

redirect_bp = Blueprint("redirect", __name__)

@redirect_bp.route('/<short_code>')
def redirect_to_url(short_code):
    # Check redis for cache
    cached_url = redis.get(short_code)
    if cached_url:
        print("⚡ Cache Hit!")
        return redirect(cached_url)
    
    # Check postgres if not cached
    print("🐢 Cache Miss - Checking Postgres...")
    try:
        # Find the original link in the DB
        link = URL.get(URL.short_code == short_code)
        
        # Cache to redis
        redis.setex(short_code, 3600, link.full_url)
        redis.setex(f"long:{link.full_url}", 3600, short_code)
        return redirect(link.full_url)
    except URL.DoesNotExist:
        return "URL not found", 404