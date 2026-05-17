import React from 'react';
import './ReviewDisplay.css';

const getAvatarId = (id) => {
  if (!id) return 1;
  let hash = 0;
  for (let i = 0; i < id.length; i++) {
    hash = id.charCodeAt(i) + ((hash << 5) - hash);
  }
  return (Math.abs(hash) % 500) + 1;
};

export default function ReviewDisplay({ simulation, persona, dna }) {
  if (!simulation || !simulation.simulation) return null;

  const { review_text, predicted_rating } = simulation.simulation;
  
  // Create stars array based on rating
  const rating = parseInt(predicted_rating) || 0;
  const stars = Array(5).fill(0).map((_, i) => i < rating);

  return (
    <div className="tripadvisor-card">
      <div className="ta-header">
        <div className="ta-user-info">
          <img src={`/avatars/${getAvatarId(persona?.user_id)}.jpg`} alt="Avatar" className="ta-avatar" />
          <div className="ta-user-details">
            <span className="ta-name">{persona?.name || 'User'}</span>
            <span className="ta-contributions">
              {persona?.review_count || 0} contributions
            </span>
          </div>
        </div>
      </div>

      <div className="ta-content">
        <div className="ta-rating-row">
          <div className="ta-stars">
            {stars.map((filled, i) => (
              <span key={i} className={`ta-star ${filled ? 'filled' : ''}`}>★</span>
            ))}
          </div>
          <span className="ta-rating-value">{rating} / 5</span>
          <span className="ta-date">Reviewed today</span>
        </div>

        <h3 className="ta-title">A detailed look at my experience</h3>
        
        <div className="ta-body">
          <p>{review_text}</p>
        </div>

        <div className="ta-date-visit">
          <strong>Date of experience:</strong> May 2026
        </div>

        <div className="ta-footer">
          <button className="ta-helpful-btn">
            👍 Helpful
          </button>
        </div>
      </div>
    </div>
  );
}
