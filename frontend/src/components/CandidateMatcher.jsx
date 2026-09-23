import React, { useState } from 'react';
import './CandidateMatcher.css';

const CandidateMatcher = ({ jobId, jobDescription, onMatchesFound }) => {
  const [loading, setLoading] = useState(false);
  const [matches, setMatches] = useState(null);
  const [error, setError] = useState(null);

  const findMatches = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:8000/Api/mike/match', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          job_description: jobDescription,
          job_id: jobId
        }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setMatches(data);
      
      if (onMatchesFound) {
        onMatchesFound(data);
      }
    } catch (err) {
      setError(err.message);
      console.error('Error finding matches:', err);
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'high';
    if (score >= 60) return 'medium';
    return 'low';
  };

  return (
    <div className="candidate-matcher">
      <button 
        className="find-matches-btn"
        onClick={findMatches}
        disabled={loading}
      >
        {loading ? (
          <>
            <span className="spinner"></span>
            Analyzing...
          </>
        ) : (
          '🔍 Find Matches'
        )}
      </button>
      
      {error && (
        <div className="error-message">
          ⚠️ Error: {error}
        </div>
      )}
      
      {matches && (
        <div className="results-panel">
          <div className="results-header">
            <h3>🏆 Top Candidates</h3>
            <div className="stats">
              <span>📊 {matches.total_candidates_considered} candidates analyzed</span>
              <span>⚡ {matches.query_time_ms}ms</span>
            </div>
          </div>
          
          <div className="job-requirements-badge">
            <strong>Required Role:</strong> {matches.job_requirements.role} | 
            <strong> Experience:</strong> {matches.job_requirements.experience_band} | 
            <strong> Location:</strong> {matches.job_requirements.location}
            <details>
              <summary>Required Skills ({matches.job_requirements.skills.length})</summary>
              <div className="skills-list">
                {matches.job_requirements.skills.map((skill, idx) => (
                  <span key={idx} className="skill-tag">{skill}</span>
                ))}
              </div>
            </details>
          </div>
          
          <div className="candidates-list">
            {matches.top_candidates.map((match, index) => (
              <div key={match.candidate.id} className="candidate-card">
                <div className="candidate-rank">#{index + 1}</div>
                <div className="candidate-info">
                  <div className="candidate-name">
                    {match.candidate.name}
                    <span className={`match-score ${getScoreColor(match.match_score)}`}>
                      {match.match_score}% Match
                    </span>
                  </div>
                  <div className="candidate-details">
                    <span>💼 {match.candidate.current_role || 'N/A'}</span>
                    <span>⭐ {match.candidate.experience_years} years</span>
                    <span>📍 {match.candidate.location}</span>
                    <span>🎓 {match.candidate.education || 'N/A'}</span>
                  </div>
                  <div className="candidate-skills">
                    {match.candidate.skills.slice(0, 5).map((skill, idx) => (
                      <span key={idx} className="skill-badge">{skill}</span>
                    ))}
                    {match.candidate.skills.length > 5 && (
                      <span className="skill-badge more">+{match.candidate.skills.length - 5}</span>
                    )}
                  </div>
                  <div className="match-rationale">
                    <strong>Match Analysis:</strong> {match.match_rationale}
                  </div>
                  <div className="match-details">
                    <div className="detail-item">
                      <span>Skills Match:</span>
                      <div className="progress-bar">
                        <div 
                          className="progress-fill"
                          style={{ width: `${match.skill_match_percentage}%` }}
                        ></div>
                      </div>
                      <span>{match.skill_match_percentage}%</span>
                    </div>
                    <div className="detail-item">
                      <span>Experience:</span>
                      {match.experience_match ? '✅ Meets requirements' : '⚠️ Gap detected'}
                    </div>
                    <div className="detail-item">
                      <span>Location:</span>
                      {match.location_match ? '✅ Compatible' : '❌ Mismatch'}
                    </div>
                  </div>
                  <button className="contact-btn">📧 Contact Candidate</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default CandidateMatcher;