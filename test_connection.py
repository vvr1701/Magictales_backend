#!/usr/bin/env python3
"""Quick database connection test after updating credentials."""

import os
import sys
sys.path.append('/mnt/c/Users/santh/Desktop/Magictales')

from dotenv import load_dotenv
import psycopg2

load_dotenv()

print("🔧 Quick Connection Test")
print("=" * 30)

DATABASE_URL = os.getenv('DATABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

try:
    # Test PostgreSQL connection
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("SELECT 'Connection successful!' as status")
    result = cursor.fetchone()

    print("✅ PostgreSQL: CONNECTED")
    print(f"✅ Status: {result[0]}")

    # Quick table check
    cursor.execute("""
        SELECT COUNT(*) FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name IN ('previews', 'orders', 'generation_jobs', 'rate_limits')
    """)
    table_count = cursor.fetchone()[0]
    print(f"📊 Tables found: {table_count}/4")

    if table_count == 4:
        print("🎉 All tables exist!")
    elif table_count == 0:
        print("📋 No tables found - run supabase_schema.sql")
    else:
        print("⚠️ Some tables missing - check schema")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"❌ Connection failed: {str(e)}")
    if "Tenant or user not found" in str(e):
        print("💡 Update your DATABASE_URL credential")
    elif "authentication failed" in str(e):
        print("💡 Check your database password")

print()
print("Next: If connection works but no tables, run:")
print("   supabase_schema.sql in Supabase Dashboard")