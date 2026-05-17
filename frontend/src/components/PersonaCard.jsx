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

export default function PersonaCard({ persona, onClick }) {
  const { user_id, name, avg_stars, review_count, is_elite } = persona;
  
  return (
    <div className="persona-card" onClick={() => onClick(persona)}>
      <div className="card-avatar">
        <img src={`/avatars/${getAvatarId(user_id)}.jpg`} alt={name} />
        {is_elite && <div className="elite-badge">Elite</div>}
      </div>
      <div className="card-content">
        <h3>{name}</h3>
        <div className="card-stats">
          <span>⭐ {avg_stars.toFixed(1)} Avg</span>
          <span>•</span>
          <span>{review_count} Reviews</span>
        </div>
      </div>
      <div className="card-hover-overlay">
        <span>Initialize Target →</span>
      </div>
    </div>
  );
}
