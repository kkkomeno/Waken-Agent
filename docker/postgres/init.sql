-- Enable pgvector extension for vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify extension is enabled (optional logging)
DO $$
BEGIN
    RAISE NOTICE 'pgvector extension enabled successfully';
END $$;
