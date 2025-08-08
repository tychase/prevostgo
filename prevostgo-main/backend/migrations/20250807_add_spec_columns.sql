-- Safe additive migration for listings table fields used by frontend
ALTER TABLE listings
  ADD COLUMN IF NOT EXISTS model TEXT,
  ADD COLUMN IF NOT EXISTS chassis_type TEXT,
  ADD COLUMN IF NOT EXISTS mileage INTEGER,
  ADD COLUMN IF NOT EXISTS slide_count INTEGER,
  ADD COLUMN IF NOT EXISTS price INTEGER,
  ADD COLUMN IF NOT EXISTS price_contact BOOLEAN DEFAULT FALSE;