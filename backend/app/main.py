from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import time
import re

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== Models ==========
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

# ========== Mock Data ==========
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
    }
]

# ========== Helper Functions ==========
def extract_requirements(job_description: str) -> JDRequirements:
    jd_lower = job_description.lower()
    
    # Extract role
    role = "Software Engineer"
    if "senior" in jd_lower:
        role = "Senior Software Engineer"
    elif "lead" in jd_lower:
        role = "Lead Software Engineer"
    elif "python" in jd_lower:
        role = "Python Developer"
    elif "react" in jd_lower:
        role = "Frontend Developer"
    
    # Extract skills
    common_skills = ["python", "javascript", "react", "fastapi", "django", "postgresql", 
                     "mongodb", "aws", "docker", "kubernetes", "typescript", "node"]
    skills = []
    for skill in common_skills:
        if skill in jd_lower:
            skills.append(skill.title())
    
    if not skills:
        skills = ["Python", "JavaScript", "SQL"]
    
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
        location_match = re.search(r'in\s+([A-Za-z\s]+?)(?:\.|\s|$)', job_description)
        if location_match:
            location = location_match.group(1).strip()
    
    return JDRequirements(
        role=role,
        skills=skills[:8],
        experience_band=experience_band,
        location=location,
        years_experience_min=years_min,
        raw_description=job_description
    )

def calculate_match_score(candidate: dict, requirements: JDRequirements):
    rationale_parts = []
    
    # Skill match
    candidate_skills_lower = [s.lower() for s in candidate.get("skills", [])]
    required_skills_lower = [s.lower() for s in requirements.skills]
    
    if required_skills_lower:
        matched = 0
        for req_skill in required_skills_lower:
            for cand_skill in candidate_skills_lower:
                if req_skill in cand_skill or cand_skill in req_skill:
                    matched += 1
                    break
        skill_score = (matched / len(required_skills_lower)) * 100
    else:
        skill_score = 50
    
    if skill_score >= 70:
        rationale_parts.append(f"✅ Strong skill match ({skill_score:.0f}%)")
    elif skill_score >= 40:
        rationale_parts.append(f"📚 Partial skill match ({skill_score:.0f}%)")
    else:
        rationale_parts.append(f"⚠️ Limited skill match ({skill_score:.0f}%)")
    
    # Experience match
    required_exp = requirements.years_experience_min or 3
    candidate_exp = candidate.get("experience_years", 0)
    
    if candidate_exp >= required_exp:
        exp_score = min(100, (candidate_exp / required_exp) * 100)
        exp_match = True
        rationale_parts.append(f"💼 {candidate_exp} years experience")
    else:
        exp_score = (candidate_exp / required_exp) * 100
        exp_match = False
        rationale_parts.append(f"⚠️ Experience: {candidate_exp}/{required_exp} years")
    
    # Location match
    req_location = requirements.location.lower()
    cand_location = candidate.get("location", "").lower()
    
    if req_location == "remote" or cand_location == req_location:
        loc_score = 100
        loc_match = True
        rationale_parts.append(f"📍 Location OK")
    else:
        loc_score = 50
        loc_match = False
        rationale_parts.append(f"🌍 Location mismatch")
    
    # Calculate total score
    total_score = (skill_score * 0.5) + (exp_score * 0.3) + (loc_score * 0.2)
    rationale = " | ".join(rationale_parts)
    
    return total_score, rationale, skill_score, exp_match, loc_match

# ========== API Endpoints ==========
@app.get("/")
@app.get("/health")
async def root():
    return {"status": "healthy", "message": "Work360 API is running", "endpoints": {"/Api/mike/match": "POST - Match candidates"}}

@app.post("/Api/mike/match")
async def match_candidates(request: MatchRequest):
    """Main endpoint for candidate matching"""
    start_time = time.time()
    
    # Extract requirements
    requirements = extract_requirements(request.job_description)
    
    # Score all candidates
    scored_candidates = []
    for candidate_data in MOCK_CANDIDATES:
        score, rationale, skill_score, exp_match, loc_match = calculate_match_score(
            candidate_data, requirements
        )
        
        candidate = Candidate(**candidate_data)
        match = CandidateMatch(
            candidate=candidate,
            match_score=round(score, 2),
            match_rationale=rationale,
            skill_match_percentage=round(skill_score, 2),
            experience_match=exp_match,
            location_match=loc_match
        )
        scored_candidates.append((score, match))
    
    # Sort and get top 10
    scored_candidates.sort(key=lambda x: x[0], reverse=True)
    top_candidates = [match for _, match in scored_candidates[:10]]
    
    query_time_ms = (time.time() - start_time) * 1000
    
    return {
        "job_requirements": requirements.dict(),
        "top_candidates": [match.dict() for match in top_candidates],
        "total_candidates_considered": len(MOCK_CANDIDATES),
        "query_time_ms": round(query_time_ms, 2)
    }

# HTML Frontend
HTML_FRONTEND = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Work360 - Candidate Ranking System</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        .header { text-align: center; color: white; margin-bottom: 30px; }
        .header h1 { font-size: 2.5rem; margin-bottom: 10px; }
        .header p { font-size: 1.1rem; opacity: 0.9; }
        .status-badge {
            display: inline-block;
            background: #28a745;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 14px;
            margin-top: 10px;
        }
        .main-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; }
        @media (max-width: 768px) { .main-grid { grid-template-columns: 1fr; } }
        .card {
            background: white;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }
        .card h2 { color: #333; margin-bottom: 20px; }
        .templates { display: flex; gap: 10px; margin-bottom: 15px; flex-wrap: wrap; }
        .template-btn {
            background: #f0f0f0;
            border: none;
            padding: 8px 16px;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .template-btn:hover { background: #667eea; color: white; transform: translateY(-2px); }
        .jd-input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-family: monospace;
            font-size: 14px;
            resize: vertical;
            margin-bottom: 15px;
        }
        .jd-input:focus { outline: none; border-color: #667eea; }
        .find-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            transition: transform 0.2s;
        }
        .find-btn:hover { transform: translateY(-2px); }
        .find-btn:disabled { opacity: 0.6; cursor: not-allowed; }
        .spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 2px solid white;
            border-top-color: transparent;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-right: 10px;
            vertical-align: middle;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        .results { margin-top: 20px; }
        .stats {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
        }
        .requirements-badge {
            background: #e8f4f8;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            font-size: 14px;
        }
        .candidate-card {
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            transition: all 0.3s;
            background: white;
        }
        .candidate-card:hover { box-shadow: 0 5px 20px rgba(0,0,0,0.1); transform: translateY(-2px); }
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            flex-wrap: wrap;
            gap: 10px;
        }
        .candidate-name { font-size: 18px; font-weight: 700; color: #333; }
        .match-score {
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: 700;
            font-size: 14px;
        }
        .score-high { background: #d4edda; color: #155724; }
        .score-medium { background: #fff3cd; color: #856404; }
        .score-low { background: #f8d7da; color: #721c24; }
        .candidate-details {
            display: flex;
            gap: 20px;
            margin-bottom: 15px;
            font-size: 14px;
            color: #666;
            flex-wrap: wrap;
        }
        .skills { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 15px; }
        .skill {
            background: #f0f0f0;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 12px;
            color: #555;
        }
        .skill.highlight { background: #667eea; color: white; }
        .rationale {
            background: #f8f9fa;
            padding: 12px;
            border-radius: 8px;
            font-size: 13px;
            border-left: 3px solid #667eea;
        }
        .badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            margin-left: 10px;
        }
        .badge-yes { background: #d4edda; color: #155724; }
        .badge-no { background: #f8d7da; color: #721c24; }
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 10px;
        }
        .skill-tag {
            background: #e0e7ff;
            color: #4338ca;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            display: inline-block;
            margin: 2px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Work360 Candidate Ranking System</h1>
            <p>AI-powered candidate matching with intelligent ranking</p>
            <div class="status-badge">✅ System Ready</div>
        </div>
        <div class="main-grid">
            <div class="card">
                <h2>📋 Job Description</h2>
                <div class="templates">
                    <button class="template-btn" onclick="loadTemplate('python')">🐍 Python Developer</button>
                    <button class="template-btn" onclick="loadTemplate('react')">⚛️ React Developer</button>
                    <button class="template-btn" onclick="loadTemplate('devops')">☁️ DevOps Engineer</button>
                </div>
                <textarea id="jobDescription" class="jd-input" rows="8">Senior Python Developer needed with 5+ years experience.
Required skills: FastAPI, React, PostgreSQL, Docker.
Location: Remote</textarea>
                <button id="findBtn" class="find-btn" onclick="findMatches()">🔍 Find Matching Candidates</button>
            </div>
            <div class="card">
                <h2>🏆 Candidate Rankings</h2>
                <div id="results">
                    <div style="text-align: center; padding: 40px; color: #999;">Click "Find Matches" to see ranked candidates</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const templates = {
            python: `Senior Python Developer - Remote\\nRequired Skills:\\n- Python\\n- FastAPI\\n- PostgreSQL\\n- React\\n- Docker\\n\\nLocation: Remote`,
            react: `Senior React Developer - Remote\\nRequired Skills:\\n- React.js\\n- TypeScript\\n- Redux\\n- Node.js\\n- MongoDB\\n\\nLocation: Remote`,
            devops: `DevOps Engineer - Remote\\nRequired Skills:\\n- Kubernetes\\n- Docker\\n- AWS\\n- Terraform\\n- CI/CD\\n\\nLocation: Remote`
        };

        function loadTemplate(type) {
            document.getElementById('jobDescription').value = templates[type];
        }

        async function findMatches() {
            const btn = document.getElementById('findBtn');
            const resultsDiv = document.getElementById('results');
            const jobDescription = document.getElementById('jobDescription').value;
            
            if (!jobDescription.trim()) {
                resultsDiv.innerHTML = '<div class="error">❌ Please enter a job description</div>';
                return;
            }
            
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner"></span> Analyzing Candidates...';
            resultsDiv.innerHTML = '<div style="text-align: center; padding: 40px;"><span class="spinner"></span> Loading matches...</div>';
            
            try {
                const response = await fetch('/Api/mike/match', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ job_description: jobDescription })
                });
                
                if (!response.ok) {
                    const errorText = await response.text();
                    throw new Error(`HTTP ${response.status}: ${errorText}`);
                }
                
                const data = await response.json();
                displayResults(data);
            } catch (error) {
                console.error('Error:', error);
                resultsDiv.innerHTML = `<div class="error">❌ Error: ${error.message}<br><br>Make sure backend is running at http://localhost:8000</div>`;
            } finally {
                btn.disabled = false;
                btn.innerHTML = '🔍 Find Matching Candidates';
            }
        }
        
        function displayResults(data) {
            const resultsDiv = document.getElementById('results');
            
            if (!data.top_candidates || data.top_candidates.length === 0) {
                resultsDiv.innerHTML = '<div class="error">No candidates found matching your criteria</div>';
                return;
            }
            
            const requiredSkills = data.job_requirements.skills.map(s => s.toLowerCase());
            let html = `
                <div class="stats">
                    <span>📊 ${data.total_candidates_considered} candidates analyzed</span>
                    <span>⚡ ${data.query_time_ms} ms</span>
                </div>
                <div class="requirements-badge">
                    <strong>📋 Job Requirements</strong><br>
                    <strong>Role:</strong> ${data.job_requirements.role}<br>
                    <strong>Experience:</strong> ${data.job_requirements.experience_band} (${data.job_requirements.years_experience_min}+ years)<br>
                    <strong>Location:</strong> ${data.job_requirements.location}<br>
                    <strong>Required Skills:</strong><br>
                    ${data.job_requirements.skills.map(s => `<span class="skill-tag">${s}</span>`).join('')}
                </div>
            `;
            
            data.top_candidates.slice(0, 6).forEach((match, index) => {
                const c = match.candidate;
                let scoreClass = 'score-low';
                if (match.match_score >= 70) scoreClass = 'score-high';
                else if (match.match_score >= 50) scoreClass = 'score-medium';
                
                html += `
                    <div class="candidate-card">
                        <div class="card-header">
                            <div class="candidate-name">
                                #${index + 1} - ${c.name}
                                <span class="badge ${match.experience_match ? 'badge-yes' : 'badge-no'}">
                                    ${match.experience_match ? '✓ Experience' : '! Experience Gap'}
                                </span>
                                <span class="badge ${match.location_match ? 'badge-yes' : 'badge-no'}">
                                    ${match.location_match ? '✓ Location' : '! Location'}
                                </span>
                            </div>
                            <div class="match-score ${scoreClass}">
                                ${match.match_score}% Match
                            </div>
                        </div>
                        <div class="candidate-details">
                            <span>💼 ${c.current_role || 'N/A'}</span>
                            <span>⭐ ${c.experience_years} years</span>
                            <span>📍 ${c.location}</span>
                            <span>🎓 ${c.education || 'N/A'}</span>
                        </div>
                        <div class="skills">
                            ${c.skills.map(skill => {
                                const isHighlight = requiredSkills.includes(skill.toLowerCase());
                                return `<span class="skill ${isHighlight ? 'highlight' : ''}">${skill}</span>`;
                            }).join('')}
                        </div>
                        <div class="rationale">
                            <strong>🔍 Match Analysis:</strong> ${match.match_rationale}
                        </div>
                    </div>
                `;
            });
            
            resultsDiv.innerHTML = html;
        }
    </script>
</body>
</html>
"""

@app.get("/ui")
async def get_frontend():
    return HTMLResponse(content=HTML_FRONTEND)