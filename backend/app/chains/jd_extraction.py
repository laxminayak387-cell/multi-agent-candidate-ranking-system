# app/chains/jd_extraction.py - Mock version without OpenAI
from app.models.schemas import JDRequirements, ExperienceBand
import re
from typing import Dict, Any

class JDExtractionChain:
    def __init__(self):
        # No OpenAI needed
        pass
    
    def extract_requirements(self, job_description: str) -> JDRequirements:
        """Extract requirements from JD using pattern matching"""
        jd_lower = job_description.lower()
        
        # Extract role
        role = "Software Engineer"
        if "senior" in jd_lower:
            role = "Senior Software Engineer"
        elif "lead" in jd_lower:
            role = "Lead Software Engineer"
        elif "junior" in jd_lower:
            role = "Junior Software Engineer"
        elif "python" in jd_lower:
            role = "Python Developer"
        elif "react" in jd_lower:
            role = "Frontend Developer"
        
        # Extract skills
        common_skills = [
            "python", "javascript", "java", "react", "angular", "vue", "node",
            "fastapi", "django", "flask", "spring", "sql", "postgresql", "mysql",
            "mongodb", "aws", "docker", "kubernetes", "typescript", "go", "rust"
        ]
        
        skills = []
        for skill in common_skills:
            if skill in jd_lower:
                skills.append(skill.title())
        
        if not skills:
            skills = ["Python", "JavaScript", "SQL"]
        
        # Extract experience band
        experience_band = ExperienceBand.MID
        years_min = 3
        
        if "senior" in jd_lower or "lead" in jd_lower:
            experience_band = ExperienceBand.SENIOR
            years_min = 5
        elif "junior" in jd_lower or "entry" in jd_lower:
            experience_band = ExperienceBand.JUNIOR
            years_min = 1
        elif "principal" in jd_lower:
            experience_band = ExperienceBand.PRINCIPAL
            years_min = 10
        
        # Extract location
        location = "remote"
        if "in " in jd_lower and "remote" not in jd_lower:
            location_match = re.search(r'in\s+([A-Za-z\s]+?)(?:\.|\s|$)', job_description)
            if location_match:
                location = location_match.group(1).strip()
        
        return JDRequirements(
            role=role,
            skills=skills,
            experience_band=experience_band,
            location=location,
            years_experience_min=years_min,
            years_experience_max=None,
            raw_description=job_description
        )

# Create instance
jd_extraction_chain = JDExtractionChain()