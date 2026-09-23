# app/services/embedding_service.py - Mock version without OpenAI
from typing import List
import random

class EmbeddingService:
    def __init__(self):
        self.model = "mock-embedding"
    
    def get_embedding(self, text: str) -> List[float]:
        """Return a mock embedding vector"""
        # Return a random vector of 1536 dimensions (for pgvector)
        return [random.uniform(-1, 1) for _ in range(1536)]
    
    def get_candidate_text_representation(self, candidate: dict) -> str:
        """Create a text representation of a candidate"""
        skills_text = " ".join(candidate.get('skills', []))
        text = f"""
        Role: {candidate.get('current_role', '')}
        Skills: {skills_text}
        Experience: {candidate.get('experience_years', 0)} years
        Location: {candidate.get('location', '')}
        Education: {candidate.get('education', '')}
        """
        return text.strip()
    
    def batch_get_embeddings(self, texts: List[str], batch_size: int = 20) -> List[List[float]]:
        """Generate mock embeddings for multiple texts"""
        return [self.get_embedding(text) for text in texts]

embedding_service = EmbeddingService()