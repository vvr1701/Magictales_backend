-- ============================================================================
-- Migration: Add cartoon_3d to book_style enum
-- ============================================================================
-- Run this in Supabase SQL Editor:
-- Dashboard > SQL Editor > New Query > Paste this > Run
-- ============================================================================

-- Add 'cartoon_3d' value to the book_style enum
ALTER TYPE book_style ADD VALUE IF NOT EXISTS 'cartoon_3d';

-- Verify the enum now has all values
SELECT enum_range(NULL::book_style);
