"""
backend/app/db.py

Single shared Supabase client, per CLAUDE.md's isolation convention
(one place initializes external clients; routers import from here).
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)