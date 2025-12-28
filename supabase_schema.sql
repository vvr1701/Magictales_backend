-- ============================================================================
-- Magictales Application - Complete Supabase Database Schema
-- ============================================================================
-- This script creates all tables, enums, functions, and indexes required
-- for the Magictales AI-powered personalized storybook application.
-- ============================================================================

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- 1. CUSTOM ENUM TYPES
-- ============================================================================

-- Preview status lifecycle
CREATE TYPE preview_status AS ENUM (
    'pending',      -- Initial state when preview request is created
    'validating',   -- Photo validation in progress
    'generating',   -- AI images being generated
    'active',       -- Preview ready, can be viewed/purchased
    'completed',    -- Legacy status (same as active)
    'failed',       -- Generation failed
    'expired',      -- Preview expired (7 days)
    'purchased'     -- Customer purchased, extends to 30 days
);

-- Order status lifecycle
CREATE TYPE order_status AS ENUM (
    'paid',           -- Payment confirmed by Shopify webhook
    'generating_pdf', -- PDF generation in progress
    'completed',      -- PDF ready for download
    'failed',         -- PDF generation failed
    'refunded'        -- Order refunded
);

-- Background job status
CREATE TYPE job_status AS ENUM (
    'queued',     -- Job queued for execution
    'processing', -- Job currently running
    'completed',  -- Job completed successfully
    'failed'      -- Job failed with error
);

-- Background job types
CREATE TYPE job_type AS ENUM (
    'preview_generation',  -- Generate 10 pages + 5 previews
    'full_book_generation', -- Legacy (same as preview_generation)
    'pdf_creation'         -- Generate final PDF from existing images
);

-- Visual style for generated images
CREATE TYPE book_style AS ENUM (
    'artistic',        -- Cartoon-style illustrations
    'photorealistic'   -- Realistic AI-generated images
);

-- ============================================================================
-- 2. CORE TABLES
-- ============================================================================

-- Stores personalized storybook preview generation records
CREATE TABLE previews (
    -- Primary identifiers
    id SERIAL PRIMARY KEY,
    preview_id UUID UNIQUE NOT NULL DEFAULT uuid_generate_v4(),

    -- Session and customer tracking
    session_id VARCHAR(255),
    customer_id VARCHAR(255),
    customer_email VARCHAR(255),

    -- Child information (required for story personalization)
    child_name VARCHAR(50) NOT NULL CHECK (LENGTH(child_name) >= 2),
    child_age INTEGER NOT NULL CHECK (child_age >= 2 AND child_age <= 12),
    child_gender VARCHAR(10) NOT NULL CHECK (child_gender IN ('male', 'female')),

    -- Story configuration
    theme VARCHAR(50) NOT NULL CHECK (theme IN ('magic_castle', 'space_adventure', 'underwater', 'forest_friends')),
    style book_style NOT NULL DEFAULT 'artistic',

    -- Photo information
    photo_url VARCHAR(500) NOT NULL,
    photo_validated BOOLEAN DEFAULT FALSE,

    -- Generation status
    status preview_status DEFAULT 'pending',

    -- Generated content (stored as JSONB for flexibility)
    -- hires_images: [{page: int, url: string}, ...] (all 10 pages)
    hires_images JSONB DEFAULT '[]'::jsonb,

    -- preview_images: [{page: int, url: string, text: string}, ...] (first 5 pages, watermarked)
    preview_images JSONB,

    -- story_pages: [{page: int, text: string}, ...] (story text for all pages)
    story_pages JSONB,

    -- Legacy column (for backward compatibility)
    pages JSONB DEFAULT '[]'::jsonb,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() + INTERVAL '7 days'
);

-- Tracks customer purchases and PDF generation
CREATE TABLE orders (
    -- Primary identifiers
    id SERIAL PRIMARY KEY,
    order_id VARCHAR(100) UNIQUE NOT NULL, -- Shopify order ID or DEV-prefixed for testing
    order_number VARCHAR(50), -- Human-readable order number

    -- Customer information
    customer_id VARCHAR(255),
    customer_email VARCHAR(255) NOT NULL,
    customer_name VARCHAR(255),

    -- Link to preview
    preview_id UUID, -- Foreign key to previews.preview_id

    -- Order lifecycle
    status order_status DEFAULT 'paid',

    -- Generated content
    -- hq_images: [{page: int, url: string}, ...] (final high-quality images)
    hq_images JSONB DEFAULT '[]'::jsonb,
    pdf_url VARCHAR(500), -- URL to generated PDF file
    pdf_generated_at TIMESTAMP WITH TIME ZONE,

    -- Shipping information (from Shopify webhook)
    -- {first_name, last_name, address1, address2, city, province, country, zip}
    shipping_address JSONB,
    tracking_number VARCHAR(100),

    -- Error handling and retries
    generation_attempts INTEGER DEFAULT 0,
    last_error TEXT,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,

    -- Payment information
    total_amount DECIMAL(10,2),
    currency VARCHAR(10),
    payment_method VARCHAR(50), -- 'shopify', 'DEV_BYPASS', etc.

    -- Development testing flag
    is_development_order BOOLEAN DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() + INTERVAL '30 days'
);

-- Tracks async background job execution (preview generation, PDF creation)
CREATE TABLE generation_jobs (
    -- Primary identifiers
    id SERIAL PRIMARY KEY,
    job_id UUID UNIQUE NOT NULL DEFAULT uuid_generate_v4(),

    -- Job configuration
    job_type job_type NOT NULL,
    reference_id VARCHAR(255) NOT NULL, -- preview_id or order_id

    -- Job status
    status job_status DEFAULT 'queued',
    progress INTEGER DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),

    -- Execution tracking
    queued_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,

    -- Error handling
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    error_message TEXT,

    -- Results and progress info
    result_data JSONB, -- Generated URLs, progress details, etc.
    current_step VARCHAR(255) -- Human-readable current step
);

-- Rate limiting to prevent abuse
CREATE TABLE rate_limits (
    id SERIAL PRIMARY KEY,
    identifier VARCHAR(255) NOT NULL, -- IP address or session_id
    action_type VARCHAR(50) NOT NULL, -- 'upload', 'preview', etc.
    count INTEGER DEFAULT 1,
    window_start TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(identifier, action_type)
);

-- ============================================================================
-- 3. INDEXES FOR PERFORMANCE
-- ============================================================================

-- Previews table indexes
CREATE INDEX idx_previews_preview_id ON previews(preview_id);
CREATE INDEX idx_previews_session_id ON previews(session_id);
CREATE INDEX idx_previews_status ON previews(status);
CREATE INDEX idx_previews_expires_at ON previews(expires_at);
CREATE INDEX idx_previews_created_at ON previews(created_at);

-- Orders table indexes
CREATE INDEX idx_orders_order_id ON orders(order_id);
CREATE INDEX idx_orders_preview_id ON orders(preview_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_customer_email ON orders(customer_email);
CREATE INDEX idx_orders_created_at ON orders(created_at);

-- Generation jobs indexes
CREATE INDEX idx_jobs_job_id ON generation_jobs(job_id);
CREATE INDEX idx_jobs_reference_id ON generation_jobs(reference_id);
CREATE INDEX idx_jobs_status ON generation_jobs(status);
CREATE INDEX idx_jobs_job_type ON generation_jobs(job_type);

-- Rate limits indexes
CREATE INDEX idx_rate_limits_identifier ON rate_limits(identifier);
CREATE INDEX idx_rate_limits_window_start ON rate_limits(window_start);

-- ============================================================================
-- 4. FOREIGN KEY CONSTRAINTS
-- ============================================================================

-- Link orders to previews
ALTER TABLE orders
ADD CONSTRAINT orders_preview_id_fkey
FOREIGN KEY (preview_id) REFERENCES previews(preview_id);

-- ============================================================================
-- 5. FUNCTIONS AND TRIGGERS
-- ============================================================================

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers to auto-update updated_at
CREATE TRIGGER update_previews_updated_at
    BEFORE UPDATE ON previews
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_orders_updated_at
    BEFORE UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to cleanup expired previews (can be called manually or via cron)
CREATE OR REPLACE FUNCTION cleanup_expired_previews()
RETURNS void AS $$
BEGIN
    UPDATE previews
    SET status = 'expired'
    WHERE expires_at < NOW()
    AND status NOT IN ('purchased', 'expired');
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 6. ROW LEVEL SECURITY (Optional - can be enabled later)
-- ============================================================================

-- Enable RLS on tables (uncomment if needed for multi-tenant security)
-- ALTER TABLE previews ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE generation_jobs ENABLE ROW LEVEL SECURITY;

-- Example RLS policy (uncomment and modify as needed):
-- CREATE POLICY "Users can only see their own previews" ON previews
--   FOR ALL USING (customer_email = auth.email());

-- ============================================================================
-- 7. SAMPLE DATA (Optional - for testing)
-- ============================================================================

-- Uncomment to insert test data:
/*
INSERT INTO previews (
    preview_id, child_name, child_age, child_gender, theme, style,
    photo_url, photo_validated, status
) VALUES (
    uuid_generate_v4(),
    'Test Child',
    6,
    'female',
    'magic_castle',
    'artistic',
    'https://example.com/test_photo.jpg',
    true,
    'active'
);
*/

-- ============================================================================
-- SCHEMA SETUP COMPLETE
-- ============================================================================

-- Verify schema creation
DO $$
DECLARE
    table_count INTEGER;
    enum_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_name IN ('previews', 'orders', 'generation_jobs', 'rate_limits');

    SELECT COUNT(*) INTO enum_count
    FROM pg_type
    WHERE typtype = 'e'
    AND typname IN ('preview_status', 'order_status', 'job_status', 'job_type', 'book_style');

    RAISE NOTICE 'Schema setup verification:';
    RAISE NOTICE 'Tables created: %', table_count;
    RAISE NOTICE 'Enums created: %', enum_count;

    IF table_count = 4 AND enum_count = 5 THEN
        RAISE NOTICE 'SUCCESS: All tables and enums created successfully!';
    ELSE
        RAISE WARNING 'INCOMPLETE: Expected 4 tables and 5 enums';
    END IF;
END $$;