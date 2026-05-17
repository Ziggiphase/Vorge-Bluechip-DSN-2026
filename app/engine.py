import re
import numpy as np
import pandas as pd
from collections import Counter

class UserPersonaEngine:
    def __init__(self, user_id, raw_data):
        self.user_id = user_id
        # Filter raw_data for the specific user_id
        self.df = pd.DataFrame([r for r in raw_data if r['user_id'] == user_id])
        if self.df.empty: 
            raise ValueError(f"No data for {user_id}")

        self.metadata = {
            'name': str(self.df['user_name'].iloc[0]),
            'avg_stars': float(self.df['user_avg_stars'].iloc[0]),
            'elite_years': str(self.df['user_elite'].iloc[0]),
            'review_count': int(self.df['user_review_count'].iloc[0])
        }
        self.behavioral_dna = self._analyze_behavior()
        self.linguistic_dna = self._analyze_linguistics()
        
    def _analyze_behavior(self):
        ratings = self.df['stars'].values
        unique, counts = np.unique(ratings, return_counts=True)
        dist = dict(zip(unique.astype(str), [round(float(c) / len(ratings), 2) for c in counts]))
        mean_rating = np.mean(ratings)
        low_rated = self.df[self.df['stars'] <= 2]
        deal_breakers = []
        if not low_rated.empty:
            txt = " ".join(low_rated['text'].values).lower()
            deal_breakers = [w for w, c in Counter(re.findall(r'\w+', txt)).most_common(10) if len(w) > 4]

        return {
            "sophistication": "High" if len(str(self.metadata['elite_years'])) > 0 and self.metadata['elite_years'] != 'None' else "Standard",
            "dist": dist,
            "mean": round(float(mean_rating), 2),
            "bias": "Harsh" if mean_rating < 2.8 else "Moderate" if mean_rating < 4.2 else "Easy",
            "deal_breakers": deal_breakers[:5]
        }

    def _analyze_linguistics(self):
        """Analyzes syntax and voice while identifying domain-specific 'leakage' words."""
        texts = self.df['text'].values
        # Hospitality-specific words to watch for 'leakage'
        hospitality_keywords = {'food', 'restaurant', 'waiter', 'menu', 'table', 'staff', 'dinner', 'lunch', 'breakfast', 'delicious', 'tasty'}
        
        words = " ".join(texts).lower().split()
        bigrams = [" ".join(words[i:i+2]) for i in range(len(words)-1) if len(words[i]) > 3]
        
        # Capture 'Voice Bigrams' but note if they are domain-dependent
        raw_phrases = [bg for bg, count in Counter(bigrams).most_common(20)]
        clean_voice_traits = [bg for bg in raw_phrases if not any(word in hospitality_keywords for word in bg.split())]
        
        return {
            "avg_chars": int(np.mean([len(t) for t in texts])),
            "intensity": "High" if (sum(t.count('!') for t in texts)/len(texts)) > 1.2 else "Low",
            "phrases": clean_voice_traits[:5],
            "vocab": "Diverse" if len(set(words))/max(1, len(words)) > 0.4 else "Repetitive"
        }

    def get_comprehensive_prompt(self, product_name, product_attrs):
        dna, ling = self.behavioral_dna, self.linguistic_dna
        return f"""
### ROLE: NIGERIAN CONSUMER ({self.metadata['name']})
You are simulating a specific human persona in a new context. Avoid being a generic AI.

### YOUR DNA (Source Domain: Yelp/Service):
- Personality: {dna['sophistication']} consumer, {dna['bias']} rater ({dna['mean']} stars avg).
- Voice: {ling['intensity']} intensity. Frequently uses patterns like: {', '.join(ling['phrases'])}
- History: You are sensitive to these deal-breakers: {', '.join(dna['deal_breakers'])}.

### THE TASK:
Review the following: **{product_name}**
Attributes: {product_attrs}

### DYNAMIC DOMAIN ADAPTATION RULES:
1. Terminology: Use vocabulary appropriate for **{product_name}**. If it is an app, use tech terms. If it is a cinema, use entertainment terms.
2. Avoid Domain Leakage: Do not use restaurant-specific terms (like "waiter", "menu", "delicious") unless they actually apply to this product.
3. Nigerian Nuance: Reflect your personality through Nigerian English (e.g., Happy="Standard/No wahala", Angry="Not it/Waste").
4. Fidelity: Your rating MUST align with your historical bias ({dna['bias']}).

### OUTPUT ONLY VALID JSON:
{{ 
  "internal_monologue": "Reasoning about how your persona's traits apply to {product_name} attributes.", 
  "predicted_rating": "Integer rating 1-5", 
  "review_text": "A natural, culturally-nuanced review." 
}}
"""
