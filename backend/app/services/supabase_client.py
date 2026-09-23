import os
from supabase import create_client, Client
from typing import Dict, Any, List, Optional
import json
from dotenv import load_dotenv

load_dotenv()

class SupabaseClient:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
    
    def get_candidates_with_filters(
        self, 
        skills: List[str] = None,
        location: str = None,
        min_experience: float = None,
        limit: int = 50
    ) -> List[Dict]:
        """Get candidates with basic SQL filters"""
        query = self.supabase.table("candidates").select("*")
        
        if location:
            query = query.ilike("location", f"%{location}%")
        
        if min_experience:
            query = query.gte("experience_years", min_experience)
        
        # Note: Skills filtering is more complex as it's an array
        # We'll fetch and filter in memory for simplicity
        
        response = query.limit(limit).execute()
        candidates = response.data
        
        # Filter by skills (partial match)
        if skills:
            filtered = []
            for candidate in candidates:
                candidate_skills = candidate.get('skills', [])
                if any(skill.lower() in [s.lower() for s in candidate_skills] for skill in skills):
                    filtered.append(candidate)
            candidates = filtered
        
        return candidates
    
    def vector_similarity_search(
        self, 
        query_embedding: List[float],
        match_threshold: float = 0.7,
        match_count: int = 50
    ) -> List[Dict]:
        """Perform vector similarity search using pgvector"""
        # Convert embedding to string format for Postgres
        embedding_str = f"[{','.join(map(str, query_embedding))}]"
        
        # Call the match_candidates function we'll create in Supabase
        response = self.supabase.rpc(
            'match_candidates',
            {
                'query_embedding': embedding_str,
                'match_threshold': match_threshold,
                'match_count': match_count
            }
        ).execute()
        
        return response.data
    
    def update_candidate_embedding(self, candidate_id: str, embedding: List[float]):
        """Update candidate's embedding vector"""
        embedding_str = f"[{','.join(map(str, embedding))}]"
        response = self.supabase.table("candidates").update({
            "embedding": embedding_str
        }).eq("id", candidate_id).execute()
        return response.data

# Singleton instance
supabase_client = SupabaseClient()