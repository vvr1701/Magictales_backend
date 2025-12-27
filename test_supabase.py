#!/usr/bin/env python3
"""
Simple Supabase connectivity test
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_supabase_connection():
    """Test basic Supabase connectivity."""
    try:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        print(f"🔍 Checking environment variables...")
        print(f"SUPABASE_URL: {supabase_url}")
        print(f"SUPABASE_KEY: {'*' * 20}...{supabase_key[-10:] if supabase_key else 'NOT SET'}")

        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")

        print(f"📦 Importing supabase client...")
        from supabase import create_client

        print(f"🔌 Creating Supabase client...")
        # Try creating client with minimal parameters
        supabase = create_client(supabase_url, supabase_key)

        print(f"🧪 Testing basic query...")
        # Test with a simple query
        response = supabase.table("information_schema.tables").select("table_name").limit(1).execute()

        print(f"✅ Connection successful!")
        print(f"📊 Response data: {response.data}")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print(f"Error type: {type(e)}")
        return False

if __name__ == "__main__":
    success = test_supabase_connection()
    exit(0 if success else 1)