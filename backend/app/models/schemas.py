from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ExperienceBand(str, Enum):
    ENTRY = "entry"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    PRINCIPAL = "principal"

class JDRequirements(BaseModel):
    role: str
    skills: List[str]
    experience_band: ExperienceBand
    location: str
    years_experience_min: Optional[int] = None
    years_experience_max: Optional[int] = None
    raw_description: str

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
    match_score: float = Field(..., ge=0, le=100)
    match_rationale: str
    skill_match_percentage: float
    experience_match: bool
    location_match: bool

class MatchRequest(BaseModel):
    job_description: str
    job_id: Optional[str] = None

class MatchResponse(BaseModel):
    job_requirements: JDRequirements
    top_candidates: List[CandidateMatch]
    total_candidates_considered: int
    query_time_ms: float

class CandidateWithEmbedding(Candidate):
    embedding: Optional[List[float]] = None