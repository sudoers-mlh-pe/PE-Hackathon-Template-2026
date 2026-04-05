import string
import random
from peewee import CharField, DateTimeField
import datetime

from app.database import BaseModel

class URL(BaseModel):
    full_url = CharField()
    short_code = CharField(unique=True, index=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    
    @classmethod
    def generate_code(cls):
        # Generates a random 6-character string like 'aB3dE1'
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(6))