import React, { useState, useEffect } from 'react';
import './RecommendationEngine.css';

export default function RecommendationEngine({ persona, recommendations, isLoading, errorStr, onSimulate }) {
  const [visibleCount, setVisibleCount] = useState(0);

  useEffect(() => {
    if (recommendations && recommendations.length > 0) {
      setVisibleCount(0);
      const timer1 = setTimeout(() => setVisibleCount(1), 600);
      const timer2 = setTimeout(() => setVisibleCount(2), 2400);
      const timer3 = setTimeout(() => setVisibleCount(3), 4200);
      return () => {
        clearTimeout(timer1);
        clearTimeout(timer2);
        clearTimeout(timer3);
      };
    } else {
      setVisibleCount(0);
    }
  }, [recommendations]);
  if (!persona) {
    return (
      <div className="recommender-empty">
        <span className="icon">🎯</span>
        <p>Select a persona from the pool to generate dynamic cross-domain recommendations.</p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="recommender-container">
        <div className="recommender-header">
          <h3>Task B: Intelligent Recommender</h3>
          <p>Analyzing Behavioral DNA and reasoning cross-domain preferences...</p>
        </div>
        <div className="recommendations-list">
          <div className="skeleton-box" style={{animationDelay: '0s'}}></div>
          <div className="skeleton-box" style={{animationDelay: '0.2s'}}></div>
          <div className="skeleton-box" style={{animationDelay: '0.4s'}}></div>
        </div>
      </div>
    );
  }

  if (errorStr) {
    return (
      <div className="recommender-error">
        <span className="icon">⚠️</span>
        <p>{errorStr}</p>
      </div>
    );
  }

  // If no recommendations and not loading/error, show nothing
  if (!isLoading && (!recommendations || recommendations.length === 0)) {
    return null;
  }

  return (
    <div className="recommender-container">
      <div className="recommender-header">
        <h3>Task B: Intelligent Recommender</h3>
        <p>Tailored specifically for <strong>{persona.name}</strong> based on extracted deal-breakers.</p>
      </div>

      <div className="recommendations-list">
        {recommendations.slice(0, visibleCount).map((rec, idx) => (
          <div 
            key={idx} 
            className="rec-card"
            style={{ animationDelay: '0s' }} // Remove delay since they are added dynamically
          >
            <h4 className="rec-title">{rec.product_name}</h4>
            <p className="rec-desc">{rec.product_attributes}</p>
            
            <div className="rec-reasoning">
              <strong>Agent Reasoning:</strong>
              <p>{rec.reasoning}</p>
            </div>

            <button 
              className="btn-simulate"
              onClick={() => onSimulate(rec.product_name, rec.product_attributes)}
            >
              Simulate Reaction with Foyce →
            </button>
          </div>
        ))}
        
        {/* Render skeletons for items that are not yet visible, but only if not fully done */}
        {recommendations.length > 0 && visibleCount < 3 && (
          Array(3 - visibleCount).fill(0).map((_, i) => (
            <div key={`skel-${i}`} className="skeleton-box" style={{animationDelay: '0s'}}></div>
          ))
        )}
      </div>
    </div>
  );
}
