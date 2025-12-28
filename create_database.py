#!/usr/bin/env python3
"""
Database setup script for Magictales application.
This script sets up the Supabase database schema.
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

def check_database_tables():
    """Check if tables exist using Supabase REST API."""
    print("🔍 Checking database tables...")

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Missing Supabase credentials")
        return False

    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }

    # Check each table
    tables_to_check = ['previews', 'orders', 'generation_jobs', 'rate_limits']
    existing_tables = []

    for table in tables_to_check:
        try:
            url = f"{SUPABASE_URL}/rest/v1/{table}?select=*&limit=1"
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                existing_tables.append(table)
                print(f"✅ Table '{table}' exists")
            elif response.status_code == 404:
                print(f"❌ Table '{table}' not found")
            else:
                print(f"⚠️ Table '{table}' - Status: {response.status_code}")

        except Exception as e:
            print(f"❌ Error checking table '{table}': {str(e)}")

    print(f"📊 Found {len(existing_tables)}/{len(tables_to_check)} tables")
    return len(existing_tables) == len(tables_to_check)

def main():
    """Main setup function."""
    print("🚀 Magictales Database Setup")
    print("="*50)

    print(f"📍 Supabase URL: {SUPABASE_URL}")
    print(f"🔑 API Key: {'✅ Present' if SUPABASE_KEY else '❌ Missing'}")

    # Check if tables exist
    tables_exist = check_database_tables()

    if tables_exist:
        print("🎉 All tables already exist! Database is ready.")
        return True
    else:
        print("\n📋 Tables missing. Please create them manually:")
        print("1. Go to your Supabase project dashboard")
        print("2. Click 'SQL Editor'")
        print("3. Copy and paste the contents of 'supabase_schema.sql'")
        print("4. Click 'Run' to execute")
        return False

if __name__ == "__main__":
    main()