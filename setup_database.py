#!/usr/bin/env python3
"""
Database schema setup script for Zelavo Kids platform.
This script will create all necessary tables, enums, and functions in Supabase.
"""

import asyncio
import os
from dotenv import load_dotenv
import asyncpg

# Load environment variables
load_dotenv()

# Database schema SQL from implementation plan
DATABASE_SCHEMA = """
-- ===================
-- ENUMS
-- ===================

CREATE TYPE preview_status AS ENUM (
    'pending',
    'validating',
    'generating',
    'completed',
    'failed',
    'expired',
    'purchased'
);

CREATE TYPE order_status AS ENUM (
    'paid',
    'generating',
    'completed',
    'failed',
    'refunded'
);

CREATE TYPE job_status AS ENUM (
    'queued',
    'processing',
    'completed',
    'failed'
);

CREATE TYPE job_type AS ENUM (
    'preview_generation',
    'full_book_generation',
    'pdf_creation'
);

CREATE TYPE book_style AS ENUM (
    'artistic',
    'photorealistic'
);

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

CREATE INDEX IF NOT EXISTS idx_previews_preview_id ON previews(preview_id);
CREATE INDEX IF NOT EXISTS idx_previews_session_id ON previews(session_id);
CREATE INDEX IF NOT EXISTS idx_previews_status ON previews(status);
CREATE INDEX IF NOT EXISTS idx_previews_expires_at ON previews(expires_at);

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    order_id VARCHAR(100) UNIQUE NOT NULL,
    order_number VARCHAR(50),

    -- Customer
    customer_id VARCHAR(255),
    customer_email VARCHAR(255) NOT NULL,

    -- Link to preview
    preview_id UUID REFERENCES previews(preview_id),

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

CREATE INDEX IF NOT EXISTS idx_orders_order_id ON orders(order_id);
CREATE INDEX IF NOT EXISTS idx_orders_preview_id ON orders(preview_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_customer_email ON orders(customer_email);

-- Generation Jobs table
CREATE TABLE IF NOT EXISTS generation_jobs (
    id SERIAL PRIMARY KEY,
    job_id UUID DEFAULT gen_random_uuid() UNIQUE NOT NULL,

    -- Job details
    job_type job_type NOT NULL,
    reference_id VARCHAR(255) NOT NULL,  -- preview_id or order_id

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

CREATE INDEX IF NOT EXISTS idx_jobs_job_id ON generation_jobs(job_id);
CREATE INDEX IF NOT EXISTS idx_jobs_reference_id ON generation_jobs(reference_id);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON generation_jobs(status);

-- Rate Limiting table
CREATE TABLE IF NOT EXISTS rate_limits (
    id SERIAL PRIMARY KEY,
    identifier VARCHAR(255) NOT NULL,  -- IP address or session_id
    action_type VARCHAR(50) NOT NULL,  -- 'upload', 'preview'
    count INTEGER DEFAULT 1,
    window_start TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(identifier, action_type)
);

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

-- Cleanup expired previews (run daily via cron)
CREATE OR REPLACE FUNCTION cleanup_expired_previews()
RETURNS void AS $$
BEGIN
    UPDATE previews
    SET status = 'expired'
    WHERE expires_at < NOW()
    AND status NOT IN ('purchased', 'expired');
END;
$$ LANGUAGE plpgsql;
"""

async def setup_database():
    """Setup database schema in Supabase."""
    try:
        # Get database URL from environment
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is required")

        print("🔌 Connecting to Supabase database...")

        # Connect to database
        conn = await asyncpg.connect(database_url)

        print("📊 Creating database schema...")

        # Execute the schema creation
        await conn.execute(DATABASE_SCHEMA)

        print("✅ Database schema created successfully!")

        # Verify tables were created
        print("\n🔍 Verifying created tables...")
        tables_query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """

        tables = await conn.fetch(tables_query)
        print(f"📋 Found {len(tables)} tables:")
        for table in tables:
            print(f"  - {table['table_name']}")

        # Verify enums were created
        print("\n🏷️  Verifying created enums...")
        enums_query = """
            SELECT typname
            FROM pg_type
            WHERE typtype = 'e'
            ORDER BY typname;
        """

        enums = await conn.fetch(enums_query)
        print(f"📑 Found {len(enums)} custom types:")
        for enum in enums:
            print(f"  - {enum['typname']}")

        # Test a simple query
        print("\n🧪 Testing database connectivity...")
        result = await conn.fetchval("SELECT 'Database connection successful!' as message")
        print(f"💬 {result}")

        await conn.close()

        print("\n🎉 Database setup completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(setup_database())
    exit(0 if success else 1)