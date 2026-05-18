import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional

from .engine import UserPersonaEngine
from .workflow import GroqAgentClient, UserModelingWorkflow
from .recommender import RecommendationEngine

app = FastAPI(title="DSN X BCT - Task A Agent")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state for data
raw_data = []
users_summary = []

class SimulationRequest(BaseModel):
    user_id: str
    product_name: str
    product_attributes: str
    api_key: str

@app.on_event("startup")
def load_data():
    global raw_data, users_summary
    data_path = os.path.join(os.path.dirname(__file__), "..", "task_a_filtered_data.json")
    if os.path.exists(data_path):
        with open(data_path, 'r') as f:
            raw_data = json.load(f)
            
        # Create a lightweight summary for the frontend to prevent loading 39MB JSON
        seen = set()
        for r in raw_data:
            if r['user_id'] not in seen:
                seen.add(r['user_id'])
                users_summary.append({
                    "user_id": r['user_id'],
                    "name": r['user_name'],
                    "avg_stars": r['user_avg_stars'],
                    "review_count": r['user_review_count'],
                    "is_elite": len(str(r['user_elite'])) > 0 and str(r['user_elite']) != 'None'
                })
        print(f"Loaded {len(raw_data)} records for {len(users_summary)} unique users.")
    else:
        print(f"Warning: Data file not found at {data_path}")

@app.get("/api/users")
def get_users(limit: int = 500, skip: int = 0):
    """Returns a lightweight list of users for the frontend Persona selector."""
    return {"users": users_summary[skip:skip+limit], "total": len(users_summary)}

@app.post("/api/simulate")
def simulate_review(req: SimulationRequest):
    """Runs the adversarial workflow for a given user and product."""
    api_key = req.api_key or os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=400, detail="Groq API Key is required (via UI or server ENV)")
        
    try:
        engine = UserPersonaEngine(req.user_id, raw_data)
        client = GroqAgentClient(api_key=api_key)
        workflow = UserModelingWorkflow(client)
        
        result = workflow.run_simulation(engine, req.product_name, req.product_attributes)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
            
        return {
            "persona": engine.metadata,
            "dna": engine.behavioral_dna,
            "linguistics": engine.linguistic_dna,
            "simulation": result.get("simulation"),
            "generator_log": result.get("generator_log"),
            "discriminator_log": result.get("discriminator_log"),
            "refiner_log": result.get("refiner_log")
        }
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class RecommendRequest(BaseModel):
    user_id: str
    api_key: str

@app.post("/api/recommend")
def get_recommendations(req: RecommendRequest):
    """Runs the Task B recommendation workflow."""
    api_key = req.api_key or os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=400, detail="Groq API Key is required (via UI or server ENV)")
        
    try:
        engine = UserPersonaEngine(req.user_id, raw_data)
        client = GroqAgentClient(api_key=api_key)
        recommender = RecommendationEngine(client)
        
        result = recommender.generate_recommendations(engine)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
            
        return result
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Serve React Frontend ---
# In Docker, the React build output is placed in ./frontend/dist
frontend_dist_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")

if os.path.exists(frontend_dist_path):
    print(f"Serving frontend from {frontend_dist_path}")
    # Mount all static assets (JS, CSS, images) under /assets, etc.
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist_path, "assets")), name="assets")
    
    # Optional: If you have a public/avatars folder that Vite built
    if os.path.exists(os.path.join(frontend_dist_path, "avatars")):
        app.mount("/avatars", StaticFiles(directory=os.path.join(frontend_dist_path, "avatars")), name="avatars")
        
    @app.get("/{catchall:path}")
    def serve_frontend(catchall: str):
        # Fallback for React Router single-page app
        file_path = os.path.join(frontend_dist_path, catchall)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist_path, "index.html"))
else:
    print("Warning: Frontend build directory not found. API only mode.")
