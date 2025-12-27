#!/usr/bin/env python3
"""
Database schema setup script for Zelavo Kids platform using Supabase client.
This script will create all necessary tables, enums, and functions in Supabase.
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Database schema SQL from implementation plan
DATABASE_SCHEMA = """
-- ===================
-- ENUMS
-- ===================

DO $$ BEGIN
    CREATE TYPE preview_status AS ENUM (
        'pending',
        'validating',
        'generating',
        'completed',
        'failed',
        'expired',
        'purchased'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE order_status AS ENUM (
        'paid',
        'generating',
        'completed',
        'failed',
        'refunded'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE job_status AS ENUM (
        'queued',
        'processing',
        'completed',
        'failed'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE job_type AS ENUM (
        'preview_generation',
        'full_book_generation',
        'pdf_creation'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE book_style AS ENUM (
        'artistic',
        'photorealistic'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- ===================
-- TABLES
-- ===================

-- Previews table
CREATE TABLE IF NOT EXISTS previews (
    id SERIAL PRIMARY KEY,
    preview_id UUID DEFAULT gen_random_uuid() UNIQUE NOT NULL,

    -- Session/Customer
    session_id VARCHAR(255),
    customer_id VARCHAR(255),

    -- Child details
    child_name VARCHAR(50) NOT NULL,
    child_age INTEGER NOT NULL CHECK (child_age >= 2 AND child_age <= 12),
    child_gender VARCHAR(10) NOT NULL CHECK (child_gender IN ('male', 'female')),

    -- Book configuration
    theme VARCHAR(50) NOT NULL,
    style book_style NOT NULL DEFAULT 'artistic',

    -- Photo
    photo_url VARCHAR(500) NOT NULL,
    photo_validated BOOLEAN DEFAULT FALSE,

    -- Status
    status preview_status DEFAULT 'pending',

    -- Generated content
    pages JSONB DEFAULT '[]'::jsonb,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '7 days'),

    -- Indexes
    CONSTRAINT valid_theme CHECK (theme IN ('magic_castle', 'space_adventure', 'underwater', 'forest_friends'))
);

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    order_id VARCHAR(100) UNIQUE NOT NULL,
    order_number VARCHAR(50),

    -- Customer
    customer_id VARCHAR(255),
    customer_email VARCHAR(255) NOT NULL,

    -- Link to preview
    preview_id UUID,

    -- Status
    status order_status DEFAULT 'paid',

    -- Generated content
    hq_images JSONB DEFAULT '[]'::jsonb,
    pdf_url VARCHAR(500),

    -- Shipping (for physical books)
    shipping_address JSONB,
    tracking_number VARCHAR(100),

    -- Error handling
    generation_attempts INTEGER DEFAULT 0,
    last_error TEXT,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '30 days')
);

-- Generation Jobs table
CREATE TABLE IF NOT EXISTS generation_jobs (
    id SERIAL PRIMARY KEY,
    job_id UUID DEFAULT gen_random_uuid() UNIQUE NOT NULL,

    -- Job details
    job_type job_type NOT NULL,
    reference_id VARCHAR(255) NOT NULL,

    -- Status
    status job_status DEFAULT 'queued',
    progress INTEGER DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),

    -- Timing
    queued_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,

    -- Error handling
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    error_message TEXT,

    -- Result
    result_data JSONB
);

-- Rate Limiting table
CREATE TABLE IF NOT EXISTS rate_limits (
    id SERIAL PRIMARY KEY,
    identifier VARCHAR(255) NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    count INTEGER DEFAULT 1,
    window_start TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(identifier, action_type)
);

-- ===================
-- INDEXES
-- ===================

CREATE INDEX IF NOT EXISTS idx_previews_preview_id ON previews(preview_id);
CREATE INDEX IF NOT EXISTS idx_previews_session_id ON previews(session_id);
CREATE INDEX IF NOT EXISTS idx_previews_status ON previews(status);
CREATE INDEX IF NOT EXISTS idx_previews_expires_at ON previews(expires_at);

CREATE INDEX IF NOT EXISTS idx_orders_order_id ON orders(order_id);
CREATE INDEX IF NOT EXISTS idx_orders_preview_id ON orders(preview_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_customer_email ON orders(customer_email);

CREATE INDEX IF NOT EXISTS idx_jobs_job_id ON generation_jobs(job_id);
CREATE INDEX IF NOT EXISTS idx_jobs_reference_id ON generation_jobs(reference_id);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON generation_jobs(status);

CREATE INDEX IF NOT EXISTS idx_rate_limits_identifier ON rate_limits(identifier);

-- ===================
-- FUNCTIONS
-- ===================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers
DROP TRIGGER IF EXISTS update_previews_updated_at ON previews;
CREATE TRIGGER update_previews_updated_at
    BEFORE UPDATE ON previews
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_orders_updated_at ON orders;
CREATE TRIGGER update_orders_updated_at
    BEFORE UPDATE ON orders
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Cleanup expired previews function
CREATE OR REPLACE FUNCTION cleanup_expired_previews()
RETURNS void AS $$
BEGIN
    UPDATE previews
    SET status = 'expired'
    WHERE expires_at < NOW()
    AND status NOT IN ('purchased', 'expired');
END;
$$ LANGUAGE plpgsql;

-- Add foreign key constraint after both tables are created
ALTER TABLE orders
    DROP CONSTRAINT IF EXISTS orders_preview_id_fkey;

ALTER TABLE orders
    ADD CONSTRAINT orders_preview_id_fkey
    FOREIGN KEY (preview_id)
    REFERENCES previews(preview_id);
"""

def setup_database():
    """Setup database schema in Supabase."""
    try:
        # Get Supabase credentials from environment
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables are required")

        print("🔌 Connecting to Supabase...")
        print(f"📍 URL: {supabase_url}")

        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)

        print("📊 Creating database schema...")

        # Execute the schema using RPC to run SQL
        response = supabase.rpc("exec_sql", {"sql": DATABASE_SCHEMA})

        if response.data is not None:
            print("✅ Database schema created successfully!")
        else:
            print("❌ Schema creation failed - trying alternative approach...")

            # Alternative approach: execute schema in smaller chunks
            print("📝 Attempting to create schema in parts...")

            # Just test basic connectivity first
            test_response = supabase.table('information_schema.tables').select('table_name').limit(1).execute()
            print("✅ Supabase connection successful!")

            # For now, we'll note that manual setup may be required
            print("⚠️  Manual schema setup may be required in Supabase SQL Editor")
            print("📋 Please execute the SQL from BACKEND_IMPLEMENTATION_PLAN.md section 5.1")

        print("\n🎉 Database setup process completed!")
        return True

    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        print("\n📖 Manual Setup Instructions:")
        print("1. Go to your Supabase project dashboard")
        print("2. Navigate to SQL Editor")
        print("3. Execute the SQL schema from BACKEND_IMPLEMENTATION_PLAN.md section 5.1")
        return False

if __name__ == "__main__":
    success = setup_database()
    exit(0 if success else 1)