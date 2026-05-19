import React from 'react';
import './PersonaCard.css';

// Convert user_id into a unique integer 1-500
const getAvatarId = (id) => {
  if (!id) return 1;
  let hash = 0;
  for (let i = 0; i < id.length; i++) {
    hash = id.charCodeAt(i) + ((hash << 5) - hash);
  }
  return (Math.abs(hash) % 500) + 1;
};

export default function PersonaCard({ persona, isSelected, onClick }) {
  const { user_id, name, avg_stars, review_count, is_elite } = persona;
  
  return (
    <div className={`persona-card ${isSelected ? 'selected' : ''}`} onClick={onClick}>
      <div className="persona-card-inner">
        <img className="pc-avatar" src={`/avatars/${getAvatarId(user_id)}.jpg`} alt={name} />
        
        <div className="pc-details">
          <div className="pc-name">{name}</div>
          <div className="pc-stats">
            <span>⭐ {parseFloat(avg_stars).toFixed(1)} Avg</span>
            <span>•</span>
            <span>{review_count} Reviews</span>
            {is_elite && <span className="pc-elite-badge">Elite</span>}
          </div>
        </div>
      </div>
      
      {/* Modern Dynamic CTA Layer */}
      <div className="pc-cta-layer">
        <span>Select Profile &rarr;</span>
      </div>
    </div>
  );
}
