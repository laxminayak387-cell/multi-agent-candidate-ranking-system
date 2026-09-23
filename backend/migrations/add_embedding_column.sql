-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Add embedding column to candidates table
ALTER TABLE candidates 
ADD COLUMN IF NOT EXISTS embedding vector(1536);

-- Create index for faster similarity search
CREATE INDEX IF NOT EXISTS candidates_embedding_idx 
ON candidates 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Create function for vector similarity search
CREATE OR REPLACE FUNCTION match_candidates(
  query_embedding vector(1536),
  match_threshold float,
  match_count int
)
RETURNS TABLE(
  id uuid,
  name text,
  email text,
  skills text[],
  experience_years float,
  location text,
  current_role text,
  education text,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    candidates.id,
    candidates.name,
    candidates.email,
    candidates.skills,
    candidates.experience_years,
    candidates.location,
    candidates.current_role,
    candidates.education,
    1 - (candidates.embedding <=> query_embedding) as similarity
  FROM candidates
  WHERE candidates.embedding IS NOT NULL
    AND 1 - (candidates.embedding <=> query_embedding) > match_threshold
  ORDER BY candidates.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;

-- Script to backfill embeddings for existing candidates
-- Run this separately using a Python script