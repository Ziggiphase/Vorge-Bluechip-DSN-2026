import json
import re
from .engine import UserPersonaEngine
from .workflow import BaseLLMClient

class RecommendationEngine:
    def __init__(self, client: BaseLLMClient):
        self.client = client

    def _parse_json(self, text):
        try:
            return json.loads(re.sub(r'```json\s*|\s*```', '', text).strip())
        except:
            return None

    def generate_recommendations(self, persona: UserPersonaEngine):
        dna = persona.behavioral_dna
        
        system_instruction = f"""
        You are an advanced Contextual Recommendation Agent.
        Your task is to analyze a user's behavioral DNA (extracted from their Yelp history) and INVENT 3 entirely new, realistic products or services tailored specifically to them.
        Do not use real brands like Uber, Netflix, etc. Invent realistic-sounding companies with specific attributes (e.g. "TurboFoods - A 10-minute grocery delivery app").
        
        USER DNA:
        - Personality: {dna['sophistication']} consumer, {dna['bias']} rater ({dna['mean']} stars avg).
        - Deal-breakers they hate: {', '.join(dna['deal_breakers'])}.
        
        OUTPUT FORMAT (JSON ONLY):
        {{
            "recommendations": [
                {{
                    "product_name": "Invented Name",
                    "product_attributes": "A short, 1-sentence description of what the product is and its key features.",
                    "reasoning": "Explain exactly WHY this user will love it, specifically referencing their DNA and deal-breakers."
                }},
                ... (exactly 3 items)
            ]
        }}
        """

        res = self.client.call(
            "Analyze the user DNA and invent 3 highly personalized, cross-domain recommendations.",
            system_instruction=system_instruction,
            temperature=0.9,
            model="llama-3.3-70b-versatile"
        )
        
        parsed = self._parse_json(res)
        if not parsed or "recommendations" not in parsed:
            return {"error": "Failed to generate valid recommendations.", "raw": res}
            
        return parsed
