from typing import List, Dict, Tuple
import numpy as np
from app.models.schemas import Candidate, CandidateMatch, JDRequirements
from app.services.embedding_service import embedding_service
import math

class RankingService:
    def __init__(self):
        self.skill_weight = 0.4
        self.experience_weight = 0.3
        self.location_weight = 0.1
        self.semantic_weight = 0.2
    
    def calculate_skill_match(self, candidate_skills: List[str], required_skills: List[str]) -> float:
        """Calculate percentage of required skills matched"""
        if not required_skills:
            return 100.0
        
        candidate_skills_lower = [s.lower() for s in candidate_skills]
        matched = 0
        for req_skill in required_skills:
            if any(req_skill.lower() in cand_skill for cand_skill in candidate_skills_lower):
                matched += 1
            elif any(cand_skill in req_skill.lower() for cand_skill in candidate_skills_lower):
                matched += 1
        
        return (matched / len(required_skills)) * 100
    
    def calculate_experience_match(
        self, 
        candidate_years: float, 
        min_years: int = None, 
        max_years: int = None,
        band: str = "mid"
    ) -> Tuple[bool, float]:
        """Calculate experience match score"""
        # Experience band ranges
        band_ranges = {
            "entry": (0, 2),
            "junior": (1, 4),
            "mid": (3, 6),
            "senior": (5, 9),
            "lead": (8, 13),
            "principal": (12, 30)
        }
        
        band_min, band_max = band_ranges.get(band, (3, 6))
        
        # Use specified min/max if provided
        actual_min = min_years if min_years else band_min
        actual_max = max_years if max_years else band_max
        
        if candidate_years < actual_min:
            # Underqualified - score decreases linearly
            score = max(0, (candidate_years / actual_min) * 100)
            return False, score
        elif candidate_years > actual_max:
            # Overqualified - slight penalty
            over_factor = min(1, actual_max / candidate_years)
            score = 80 * over_factor
            return True, score
        else:
            # Perfect match
            return True, 100.0
    
    def calculate_location_match(self, candidate_location: str, required_location: str) -> Tuple[bool, float]:
        """Calculate location match score"""
        if required_location.lower() == "remote":
            return True, 100.0
        
        if candidate_location.lower() == required_location.lower():
            return True, 100.0
        
        # Check for nearby locations (simplified)
        major_cities = {
            "new york": ["nyc", "brooklyn", "queens", "manhattan"],
            "san francisco": ["sf", "bay area", "oakland", "san jose"],
            "london": ["central london", "canary wharf"],
            "bangalore": ["bengaluru", "electronic city", "whitefield"]
        }
        
        for city, variants in major_cities.items():
            if required_location.lower() == city:
                if any(variant in candidate_location.lower() for variant in variants):
                    return True, 85.0
        
        return False, 0.0
    
    def calculate_semantic_similarity(self, candidate_text: str, jd_text: str) -> float:
        """Calculate semantic similarity using embeddings"""
        try:
            candidate_emb = embedding_service.get_embedding(candidate_text)
            jd_emb = embedding_service.get_embedding(jd_text)
            
            # Cosine similarity
            dot_product = np.dot(candidate_emb, jd_emb)
            norm_candidate = np.linalg.norm(candidate_emb)
            norm_jd = np.linalg.norm(jd_emb)
            
            if norm_candidate == 0 or norm_jd == 0:
                return 50.0
            
            similarity = dot_product / (norm_candidate * norm_jd)
            return similarity * 100
        except Exception as e:
            print(f"Error calculating semantic similarity: {e}")
            return 50.0
    
    def calculate_match_score(
        self,
        candidate: Dict,
        requirements: JDRequirements
    ) -> Tuple[float, str, Dict]:
        """Calculate overall match score with rationale"""
        scores = {}
        
        # Skill match
        skill_score = self.calculate_skill_match(
            candidate.get('skills', []),
            requirements.skills
        )
        scores['skill'] = skill_score
        
        # Experience match
        exp_match, exp_score = self.calculate_experience_match(
            candidate.get('experience_years', 0),
            requirements.years_experience_min,
            requirements.years_experience_max,
            requirements.experience_band.value
        )
        scores['experience'] = exp_score
        
        # Location match
        loc_match, loc_score = self.calculate_location_match(
            candidate.get('location', ''),
            requirements.location
        )
        scores['location'] = loc_score
        
        # Semantic similarity
        candidate_text = embedding_service.get_candidate_text_representation(candidate)
        semantic_score = self.calculate_semantic_similarity(
            candidate_text,
            requirements.raw_description
        )
        scores['semantic'] = semantic_score
        
        # Weighted total
        total_score = (
            scores['skill'] * self.skill_weight +
            scores['experience'] * self.experience_weight +
            scores['location'] * self.location_weight +
            scores['semantic'] * self.semantic_weight
        )
        
        # Generate rationale
        rationale = self.generate_rationale(
            candidate,
            requirements,
            scores,
            exp_match,
            loc_match
        )
        
        return total_score, rationale, scores
    
    def generate_rationale(
        self,
        candidate: Dict,
        requirements: JDRequirements,
        scores: Dict,
        exp_match: bool,
        loc_match: bool
    ) -> str:
        """Generate human-readable match rationale"""
        rationale_parts = []
        
        # Skill match
        if scores['skill'] >= 80:
            rationale_parts.append(f"✅ Strong skill match ({scores['skill']:.0f}% of required skills)")
        elif scores['skill'] >= 50:
            rationale_parts.append(f"📚 Partial skill match ({scores['skill']:.0f}% of required skills)")
        else:
            rationale_parts.append(f"⚠️ Limited skill match ({scores['skill']:.0f}% of required skills)")
        
        # Experience
        candidate_exp = candidate.get('experience_years', 0)
        if exp_match:
            if scores['experience'] >= 90:
                rationale_parts.append(f"💼 Experience aligns well ({candidate_exp} years)")
            else:
                rationale_parts.append(f"📊 Acceptable experience level ({candidate_exp} years)")
        else:
            rationale_parts.append(f"⚠️ Experience gap ({candidate_exp} years)")
        
        # Location
        candidate_loc = candidate.get('location', 'unknown')
        if loc_match:
            rationale_parts.append(f"📍 Location compatible ({candidate_loc})")
        else:
            rationale_parts.append(f"🌍 Location mismatch (requires {requirements.location})")
        
        # Top skills
        candidate_skills = candidate.get('skills', [])[:3]
        if candidate_skills:
            rationale_parts.append(f"🔧 Key skills: {', '.join(candidate_skills)}")
        
        return " | ".join(rationale_parts)

ranking_service = RankingService()