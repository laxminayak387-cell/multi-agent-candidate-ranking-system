from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict
import time
import re

router = APIRouter()

# Define Pydantic models
from pydantic import BaseModel

class MatchRequest(BaseModel):
    job_description: str
    job_id: Optional[str] = None

class Candidate(BaseModel):
    id: str
    name: str
    email: str
    skills: List[str]
    experience_years: float
    location: str
    current_role: Optional[str] = None
    education: Optional[str] = None

class CandidateMatch(BaseModel):
    candidate: Candidate
    match_score: float
    match_rationale: str
    skill_match_percentage: float
    experience_match: bool
    location_match: bool

class JDRequirements(BaseModel):
    role: str
    skills: List[str]
    experience_band: str
    location: str
    years_experience_min: Optional[int] = None
    raw_description: str

class MatchResponse(BaseModel):
    job_requirements: JDRequirements
    top_candidates: List[CandidateMatch]
    total_candidates_considered: int
    query_time_ms: float

# Mock candidate database
MOCK_CANDIDATES = [
    {
        "id": "1",
        "name": "Alice Johnson",
        "email": "alice@example.com",
        "skills": ["Python", "FastAPI", "PostgreSQL", "React", "AWS", "Docker"],
        "experience_years": 6.5,
        "location": "San Francisco",
        "current_role": "Senior Software Engineer",
        "education": "MS Computer Science"
    },
    {
        "id": "2",
        "name": "Bob Smith",
        "email": "bob@example.com",
        "skills": ["JavaScript", "React", "Node.js", "MongoDB", "Express"],
        "experience_years": 4.0,
        "location": "New York",
        "current_role": "Full Stack Developer",
        "education": "BS Computer Science"
    },
    {
        "id": "3",
        "name": "Carol Davis",
        "email": "carol@example.com",
        "skills": ["Python", "Django", "PostgreSQL", "Docker", "Kubernetes", "AWS"],
        "experience_years": 8.0,
        "location": "Remote",
        "current_role": "Lead Backend Engineer",
        "education": "PhD Computer Science"
    },
    {
        "id": "4",
        "name": "David Wilson",
        "email": "david@example.com",
        "skills": ["Java", "Spring Boot", "MySQL", "Microservices", "Kafka"],
        "experience_years": 5.0,
        "location": "Austin",
        "current_role": "Software Engineer",
        "education": "BS Computer Engineering"
    },
    {
        "id": "5",
        "name": "Emma Brown",
        "email": "emma@example.com",
        "skills": ["Python", "Machine Learning", "TensorFlow", "SQL", "Pandas"],
        "experience_years": 3.5,
        "location": "Seattle",
        "current_role": "ML Engineer",
        "education": "MS Data Science"
    },
    {
        "id": "6",
        "name": "Frank Miller",
        "email": "frank@example.com",
        "skills": ["Python", "FastAPI", "React", "TypeScript", "PostgreSQL", "Redis"],
        "experience_years": 7.0,
        "location": "Remote",
        "current_role": "Senior Full Stack Engineer",
        "education": "BS Computer Science"
    },
]

def extract_requirements(job_description: str) -> JDRequirements:
    """Extract requirements from job description"""
    jd_lower = job_description.lower()
    
    # Extract skills
    common_skills = [
        "python", "javascript", "react", "fastapi", "django", "postgresql",
        "mongodb", "aws", "docker", "kubernetes", "typescript", "sql"
    ]
    
    skills = []
    for skill in common_skills:
        if skill in jd_lower:
            skills.append(skill.title())
    
    if not skills:
        skills = ["Python", "JavaScript", "SQL"]
    
    # Extract role
    role = "Software Engineer"
    if "senior" in jd_lower:
        role = "Senior Software Engineer"
    elif "lead" in jd_lower:
        role = "Lead Software Engineer"
    
    # Extract experience
    experience_band = "mid"
    years_min = 3
    if "senior" in jd_lower:
        experience_band = "senior"
        years_min = 5
    elif "junior" in jd_lower:
        experience_band = "junior"
        years_min = 1
    
    # Extract location
    location = "remote"
    if "in " in jd_lower and "remote" not in jd_lower:
        loc_match = re.search(r'in\s+([A-Za-z\s]+?)(?:\.|\s|$)', job_description)
        if loc_match:
            location = loc_match.group(1).strip()
    
    return JDRequirements(
        role=role,
        skills=skills,
        experience_band=experience_band,
        location=location,
        years_experience_min=years_min,
        raw_description=job_description
    )

def calculate_match_score(candidate: Dict, requirements: JDRequirements):
    """Calculate match score"""
    # Skill match
    candidate_skills = [s.lower() for s in candidate.get("skills", [])]
    required_skills = [s.lower() for s in requirements.skills]
    
    if required_skills:
        matched = sum(1 for rs in required_skills if any(rs in cs or cs in rs for cs in candidate_skills))
        skill_score = (matched / len(required_skills)) * 100
    else:
        skill_score = 50
    
    # Experience match
    required_exp = requirements.years_experience_min or 3
    candidate_exp = candidate.get("experience_years", 0)
    
    if candidate_exp >= required_exp:
        exp_score = min(100, (candidate_exp / required_exp) * 100)
        exp_match = True
    else:
        exp_score = (candidate_exp / required_exp) * 100
        exp_match = False
    
    # Location match
    req_location = requirements.location.lower()
    cand_location = candidate.get("location", "").lower()
    
    if req_location == "remote" or cand_location == req_location:
        loc_score = 100
        loc_match = True
    else:
        loc_score = 50
        loc_match = False
    
    # Calculate total
    total_score = (skill_score * 0.5) + (exp_score * 0.3) + (loc_score * 0.2)
    
    # Generate rationale
    rationale_parts = []
    if skill_score >= 70:
        rationale_parts.append(f"✅ Strong skill match ({skill_score:.0f}%)")
    elif skill_score >= 40:
        rationale_parts.append(f"📚 Partial skill match ({skill_score:.0f}%)")
    else:
        rationale_parts.append(f"⚠️ Limited skill match ({skill_score:.0f}%)")
    
    if exp_match:
        rationale_parts.append(f"💼 {candidate_exp} years experience")
    else:
        rationale_parts.append(f"⚠️ Experience: {candidate_exp}/{required_exp} years")
    
    if loc_match:
        rationale_parts.append(f"📍 Location: {candidate.get('location', 'Unknown')}")
    else:
        rationale_parts.append(f"🌍 Location mismatch")
    
    rationale = " | ".join(rationale_parts)
    
    return total_score, rationale, skill_score, exp_match, loc_match

@router.post("/match", response_model=MatchResponse)
async def match_candidates(request: MatchRequest):
    """Match candidates against job description"""
    start_time = time.time()
    
    try:
        # Extract requirements
        requirements = extract_requirements(request.job_description)
        
        # Score all candidates
        scored = []
        for candidate in MOCK_CANDIDATES:
            score, rationale, skill_score, exp_match, loc_match = calculate_match_score(candidate, requirements)
            
            candidate_obj = Candidate(**candidate)
            match = CandidateMatch(
                candidate=candidate_obj,
                match_score=round(score, 2),
                match_rationale=rationale,
                skill_match_percentage=round(skill_score, 2),
                experience_match=exp_match,
                location_match=loc_match
            )
            scored.append((score, match))
        
        # Sort and get top 10
        scored.sort(key=lambda x: x[0], reverse=True)
        top_10 = [match for _, match in scored[:10]]
        
        query_time_ms = (time.time() - start_time) * 1000
        
        return MatchResponse(
            job_requirements=requirements,
            top_candidates=top_10,
            total_candidates_considered=len(MOCK_CANDIDATES),
            query_time_ms=round(query_time_ms, 2)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.options("/match")
async def options_match():
    """Handle OPTIONS requests for CORS"""
    return {"message": "OK"}