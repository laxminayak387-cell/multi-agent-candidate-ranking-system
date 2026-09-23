# Work360 Candidate Ranking System

AI-powered candidate matching system that uses LangChain, vector embeddings, and pgvector to rank candidates against job descriptions.

## Features

- 📝 **JD Extraction**: Automatically extracts role, skills, experience, and location from job descriptions
- 🔍 **Hybrid Search**: Combines SQL filtering with vector similarity search
- 🎯 **Smart Ranking**: Multi-factor scoring (skills, experience, location, semantic similarity)
- ⚡ **Real-time**: FastAPI backend with async support
- 🎨 **Modern UI**: React component with loading states and detailed match rationale

## Tech Stack

### Backend
- FastAPI (Python)
- LangChain with GPT-4
- OpenAI Embeddings (text-embedding-3-small, 1536 dimensions)
- Supabase with pgvector
- Pydantic for validation

### Frontend
- React 18
- Modern CSS with animations
- Responsive design

## Setup Instructions

### 1. Database Setup (Supabase)

Run the migration in `backend/migrations/add_embedding_column.sql`:
```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Add embedding column
ALTER TABLE candidates ADD COLUMN embedding vector(1536);

-- Create similarity search function
CREATE FUNCTION match_candidates(...)