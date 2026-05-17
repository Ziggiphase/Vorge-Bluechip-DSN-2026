# Cell
# # This Python 3 environment comes with many helpful analytics libraries installed
# # It is defined by the kaggle/python Docker image: https://github.com/kaggle/docker-python
# # For example, here's several helpful packages to load

# import numpy as np # linear algebra
# import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

# # Input data files are available in the read-only "../input/" directory
# # For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory

# import os
# for dirname, _, filenames in os.walk('/kaggle/input'):
#     for filename in filenames:
#         print(os.path.join(dirname, filename))

# # You can write up to 20GB to the current directory (/kaggle/working/) that gets preserved as output when you create a version using "Save & Run All" 
# # You can also write temporary files to /kaggle/temp/, but they won't be saved outside of the current session

# Cell
import json
import pandas as pd
import os

def surface_eda(file_path, num_samples=5):
    """
    Reads the first few lines of a Yelp JSON file and returns a summary.
    """
    samples = []
    total_lines = 0
    
    print(f"--- Analyzing: {os.path.basename(file_path)} ---")
    
    with open(file_path, 'r') as f:
        for i, line in enumerate(f):
            if i < num_samples:
                samples.append(json.loads(line))
            total_lines += 1
            
    df_samples = pd.DataFrame(samples)
    
    print(f"Total approximate records: {total_lines:,}")
    print("\nColumns available:")
    print(df_samples.columns.tolist())
    
    print("\nSample Data (First 2 rows):")
    display(df_samples.head(2))
    print("-" * 50 + "\n")
    return df_samples

# Cell
# In Kaggle, the paths will look like this:
REVIEW_PATH = '/kaggle/input/datasets/organizations/yelp-dataset/yelp-dataset/yelp_academic_dataset_review.json'
USER_PATH = '/kaggle/input/datasets/organizations/yelp-dataset/yelp-dataset/yelp_academic_dataset_user.json'
BIZ_PATH = '/kaggle/input/datasets/organizations/yelp-dataset/yelp-dataset/yelp_academic_dataset_business.json'

# Run EDA
biz_samples = surface_eda(BIZ_PATH)
user_samples = surface_eda(USER_PATH)
review_samples = surface_eda(REVIEW_PATH)

# Cell
import json
import pandas as pd
import numpy as np
import os
from collections import Counter

def get_column_stats(file_path, numeric_cols, categorical_cols, chunk_size=50000):
    """
    Calculates detailed statistics for specific columns using streaming/chunking.
    """
    print(f"--- Calculating Statistics for: {os.path.basename(file_path)} ---")
    
    stats = {col: [] for col in numeric_cols}
    counts = {col: Counter() for col in categorical_cols}
    total_processed = 0
    
    # We use chunks to avoid RAM spikes
    chunks = pd.read_json(file_path, lines=True, chunksize=chunk_size)
    
    for chunk in chunks:
        # Numeric Stats
        for col in numeric_cols:
            if col in chunk.columns:
                stats[col].extend(chunk[col].dropna().tolist())
        
        # Categorical Stats (Top 5 only to save memory)
        for col in categorical_cols:
            if col in chunk.columns:
                counts[col].update(chunk[col].dropna().tolist())
        
        total_processed += len(chunk)
        if total_processed >= 500000: # Limit EDA to first 500k rows for speed
            break

    # Final Summaries
    print(f"Processed {total_processed:,} records for EDA.")
    
    for col in numeric_cols:
        data = np.array(stats[col])
        print(f"\n[{col}] Statistics:")
        print(f"  Mean:   {np.mean(data):.2f}")
        print(f"  Std:    {np.std(data):.2f}")
        print(f"  Min:    {np.min(data)}")
        print(f"  Max:    {np.max(data)}")
        print(f"  Median: {np.median(data)}")

    for col in categorical_cols:
        print(f"\n[{col}] Top 5 Values:")
        for val, count in counts[col].most_common(5):
            print(f"  {val}: {count:,}")
    print("-" * 50 + "\n")

# Run Stats
# Note: These are specific columns relevant to Task A/B
get_column_stats(USER_PATH, 
                 numeric_cols=['review_count', 'average_stars', 'fans'], 
                 categorical_cols=[])

get_column_stats(REVIEW_PATH, 
                 numeric_cols=['stars', 'useful'], 
                 categorical_cols=[])

get_column_stats(BIZ_PATH, 
                 numeric_cols=['stars', 'review_count'], 
                 categorical_cols=['city', 'state'])

# Cell
import json
import pandas as pd
from tqdm import tqdm
import os

# --- CONFIGURATION FOR DEVELOPMENT PHASE ---
MIN_REVIEWS = 15      # N: Minimum reviews to ensure a distinct "voice"
MAX_USERS = 500       # K: Number of users to model for development
INPUT_DIR = '/kaggle/input/datasets/organizations/yelp-dataset/yelp-dataset'
OUTPUT_FILE = 'task_a_filtered_data.json'

def filter_and_join():
    """
    Implements the 'Filter First, Join Second' strategy to create a Task A dataset.
    """
    
    # 1. IDENTIFY TARGET USERS
    print(f"Step 1: Identifying {MAX_USERS} users with >= {MIN_REVIEWS} reviews...")
    target_users = {}
    user_path = os.path.join(INPUT_DIR, 'yelp_academic_dataset_user.json')
    
    try:
        with open(user_path, 'r') as f:
            for line in tqdm(f, desc="Scanning Users", total=1987897):
                user = json.loads(line)
                if user['review_count'] >= MIN_REVIEWS:
                    target_users[user['user_id']] = {
                        'user_name': user['name'],
                        'user_avg_stars': user['average_stars'],
                        'user_review_count': user['review_count'],
                        'user_elite': user['elite']
                    }
                    if len(target_users) >= MAX_USERS:
                        break
    except FileNotFoundError:
        print(f"Error: Could not find {user_path}. Check your Kaggle input paths.")
        return None
    
    selected_ids = set(target_users.keys())

    # 2. COLLECT RELEVANT REVIEWS
    print(f"Step 2: Collecting reviews for the {len(selected_ids)} selected users...")
    review_path = os.path.join(INPUT_DIR, 'yelp_academic_dataset_review.json')
    reviews_list = []
    relevant_business_ids = set()
    
    with open(review_path, 'r') as f:
        for line in tqdm(f, desc="Scanning Reviews", total=6990280):
            rev = json.loads(line)
            if rev['user_id'] in selected_ids:
                reviews_list.append({
                    'user_id': rev['user_id'],
                    'business_id': rev['business_id'],
                    'stars': rev['stars'],
                    'text': rev['text'],
                    'date': rev['date']
                })
                relevant_business_ids.add(rev['business_id'])

    # 3. GET BUSINESS METADATA
    print(f"Step 3: Mapping business metadata for contextual review simulation...")
    biz_path = os.path.join(INPUT_DIR, 'yelp_academic_dataset_business.json')
    business_lookup = {}
    
    with open(biz_path, 'r') as f:
        for line in tqdm(f, desc="Scanning Businesses", total=150346):
            biz = json.loads(line)
            if biz['business_id'] in relevant_business_ids:
                business_lookup[biz['business_id']] = {
                    'biz_name': biz['name'],
                    'biz_categories': biz['categories'],
                    'biz_attributes': biz['attributes']
                }

    # 4. CONSOLIDATE DATA
    print("Step 4: Consolidating and saving data...")
    final_data = []
    for rev in reviews_list:
        user_meta = target_users.get(rev['user_id'], {})
        biz_meta = business_lookup.get(rev['business_id'], {})
        # Merge review data with user and business metadata
        entry = {**rev, **user_meta, **biz_meta}
        final_data.append(entry)
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(final_data, f)
        
    print(f"Success! Saved {len(final_data)} total records for {len(selected_ids)} users to {OUTPUT_FILE}.")
    return final_data

if __name__ == "__main__":
    # Ensure this runs in the Kaggle environment
    processed_data = filter_and_join()

# Cell
!pip install groq

# Cell
import json
import time
import re
import numpy as np
import pandas as pd
from collections import Counter
from abc import ABC, abstractmethod

# Ensure groq is installed: !pip install groq
from groq import Groq

# --- PHASE 2: PERSONA ENGINE (DYNAMIC DOMAIN ADAPTATION) ---

class UserPersonaEngine:
    def __init__(self, user_id, raw_data):
        self.user_id = user_id
        self.df = pd.DataFrame([r for r in raw_data if r['user_id'] == user_id])
        if self.df.empty: raise ValueError(f"No data for {user_id}")

        self.metadata = {
            'name': self.df['user_name'].iloc[0],
            'avg_stars': self.df['user_avg_stars'].iloc[0],
            'elite_years': self.df['user_elite'].iloc[0],
            'review_count': self.df['user_review_count'].iloc[0]
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
            "sophistication": "High" if len(self.metadata['elite_years']) > 0 else "Standard",
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
  "predicted_rating": int, 
  "review_text": "A natural, culturally-nuanced review." 
}}
"""

# --- PHASE 3: MODULAR LLM ADAPTER ---

class BaseLLMClient(ABC):
    @abstractmethod
    def call(self, prompt: str, system_instruction: str = "", temperature: float = 0.7) -> str:
        pass

# --- UPDATE 1: MODIFY THE CLIENT TO SUPPORT DYNAMIC MODELS ---

class GroqAgentClient(BaseLLMClient):
    def __init__(self, api_key: str, default_model: str = "llama-3.3-70b-versatile"):
        self.client = Groq(api_key=api_key)
        self.default_model = default_model

    def call(self, prompt: str, system_instruction: str = "", temperature: float = 0.7, model: str = None) -> str:
        # Use the specific model if provided, otherwise fallback to default
        target_model = model if model else self.default_model
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt},
                ],
                model=target_model,
                temperature=temperature,
                response_format={"type": "json_object"} if "JSON" in prompt else None
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Groq Error ({target_model}): {e}")
            return "ERROR_LLM_CALL"

# --- UPDATE 2: ASSIGN MODELS AND TEMPERATURES IN THE WORKFLOW ---

class UserModelingWorkflow:
    def __init__(self, client: BaseLLMClient):
        self.client = client

    def _parse_json(self, text):
        try:
            return json.loads(re.sub(r'```json\s*|\s*```', '', text).strip())
        except:
            return None

    def run_simulation(self, persona: UserPersonaEngine, product_name: str, product_attrs: str):
        # --- STAGE 1: THE GENERATOR (THE ACTOR) ---
        # Strategy: High Chaos/Creativity to mimic human randomness
        print(f"[*] GENERATOR ({persona.metadata['name']}) -> Using Qwen 32B @ 1.15")
        res1 = self.client.call(
            persona.get_comprehensive_prompt(product_name, product_attrs), 
            temperature=1.15,           # High Chaos
            model="qwen/qwen3-32b"      # Creative Persona Model
        )
        gen_out = self._parse_json(res1)
        if not gen_out: return {"error": "Generator failed"}

        # --- STAGE 2: THE DISCRIMINATOR (THE JUDGE) ---
        # Strategy: Zero Chaos/Strict Logic to catch AI artifacts
        print(f"[*] DISCRIMINATOR (Evaluating Fidelity) -> Using Llama 3.3 70B @ 0.0")
        disc_sys = f"""
        Adversarial Discriminator. 
        CONTEXT: User shifting from Yelp (Service) to {product_name}.
        Target DNA: {json.dumps(persona.behavioral_dna)}
        """
        disc_task = f"Analyze simulation: {json.dumps(gen_out)}. Return JSON: {{'decision': 'APPROVED'/'REJECTED', 'synthetic_prob': float, 'critique': 'str'}}"
        
        res2 = self.client.call(
            disc_task, 
            system_instruction=disc_sys, 
            temperature=0.0,                    # Absolute Strictness
            model="llama-3.3-70b-versatile"     # Logic Powerhouse Model
        )
        disc_res = self._parse_json(res2)

        # --- STAGE 3: THE REFINER (THE DIRECTOR) ---
        # Strategy: Balanced correction to fix errors without losing persona
        if disc_res and disc_res.get("decision") == "APPROVED":
            print("[+] High Fidelity Verified.")
            return {**gen_out, "fidelity": 1 - disc_res.get("synthetic_prob", 0.5)}
        
        print(f"[!] Discriminator flagged drift. Refining...")
        critique = disc_res.get('critique', 'Too generic') if disc_res else "Inconsistent markers"
        
        res3 = self.client.call(
            f"REWRITE simulation to fool the Discriminator. REJECTED because: {critique}", 
            system_instruction=persona.get_comprehensive_prompt(product_name, product_attrs),
            temperature=0.8,                    # Balanced Correction
            model="llama-3.3-70b-versatile"      # High Reasoning for complex fixes
        )
        return self._parse_json(res3) or gen_out

# Cell
# --- EXECUTION ---
if __name__ == "__main__":
    # To use Groq:
    # 1. Get API Key from https://console.groq.com/
    # 2. Update the variable below
    GROQ_API_KEY = "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" 
    
    # Switch clients easily here:
    llm_client = GroqAgentClient(api_key=GROQ_API_KEY)
    workflow = UserModelingWorkflow(llm_client)
    
    

# Cell
import json

# 1. Load the filtered data generated from the preprocessing step
with open('/kaggle/working/task_a_filtered_data.json', 'r') as f:
    raw_data = json.load(f)

# 2. Select a user_id from the dataset to model
# For this example, we pick the first user in the list
sample_user_id = raw_data[4]['user_id']

# 3. Initialize the UserPersonaEngine
# This will trigger the behavioral and linguistic DNA extraction
engine = UserPersonaEngine(sample_user_id, raw_data)

print(f"Engine initialized for user: {engine.metadata['name']}")
print(f"Persona DNA extracted: {engine.behavioral_dna['bias']} rater with {engine.behavioral_dna['sophistication']} sophistication.")

# Cell
result = workflow.run_simulation(engine, "Nigerian Bank App", "Slow login, good interest rates")

# Cell
result

# Cell
import json
import time
import random
import pandas as pd
from tqdm import tqdm

# --- CLASS DEFINITIONS ---
# Ensure the UserPersonaEngine, GroqAgentClient, and UserModelingWorkflow 
# classes we built previously are defined above this line in your Kaggle cell.

class TaskABatchProcessor:
    def __init__(self, workflow: 'UserModelingWorkflow', raw_data: list):
        """
        Manages batch simulations for Task A.
        """
        self.workflow = workflow
        self.raw_data = raw_data
        self.results = []

    def run_batch(self, num_users=20, product_name="ZestPay Mobile App", 
                  product_attrs="Instant transfers, high transaction fees, dark mode UI, frequent OTP delays"):
        """
        Selects random users and runs the adversarial simulation.
        """
        # Get unique user IDs from the dataset
        all_unique_users = list(set([r['user_id'] for r in self.raw_data]))
        
        # Randomly sample users as requested
        num_to_sample = min(num_users, len(all_unique_users))
        selected_users = random.sample(all_unique_users, num_to_sample)
        
        print(f"--- Starting Batch Simulation for {len(selected_users)} Random Users ---")
        print(f"Product Context: {product_name}")
        
        for user_id in tqdm(selected_users, desc="Processing Batch"):
            try:
                # 1. Initialize Persona Engine for this specific user
                engine = UserPersonaEngine(user_id, self.raw_data)
                
                # 2. Run the Adversarial Simulation (Generator -> Discriminator -> Refiner)
                simulation = self.workflow.run_simulation(engine, product_name, product_attrs)
                
                # 3. Handle potential error responses from the workflow
                if "error" in simulation:
                    print(f" [!] Skipping {user_id} due to workflow error: {simulation['error']}")
                    continue

                # 4. Consolidate result for analysis
                self.results.append({
                    "user_id": user_id,
                    "user_name": engine.metadata['name'],
                    "actual_avg_stars": engine.metadata['avg_stars'],
                    "predicted_rating": simulation.get("predicted_rating"),
                    "review_text": simulation.get("review_text"),
                    "internal_monologue": simulation.get("internal_monologue"),
                    "fidelity_score": simulation.get("fidelity", 0.0),
                    "is_elite": len(engine.metadata['elite_years']) > 0,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                })
                
                # Respect Groq's RPM limits - adjust based on your tier
                time.sleep(2) 

            except Exception as e:
                print(f" [!] Critical error processing user {user_id}: {e}")
                continue

    def save_results(self, filename="task_a_batch_results.json"):
        """
        Saves the batch output to a JSON file.
        """
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=4)
        print(f"\n--- Batch Complete. {len(self.results)} results saved to {filename} ---")

# --- EXECUTION BLOCK ---
# This block assumes your GROQ_API_KEY and raw data are ready.

if __name__ == "__main__":
    # 1. Initialize Infrastructure
    # Replace with your actual key or use apiKey variable if defined in environment
    GROQ_KEY = "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"
    
    client = GroqAgentClient(api_key=GROQ_KEY)
    workflow = UserModelingWorkflow(client)

    # 2. Load the Dataset (Ensure the path is correct for your Kaggle environment)
    try:
        with open('task_a_filtered_data.json', 'r') as f:
            filtered_data = json.load(f)
            
        # 3. Instantiate Processor and Execute
        processor = TaskABatchProcessor(workflow, filtered_data)
        
        # Running for 20 random users on a Nigerian Fintech prompt
        processor.run_batch(
            num_users=20, 
            product_name="ZestPay Mobile App", 
            product_attrs="Fast transfers, 100 Naira per transaction fee, dark mode, sometimes OTP takes 5 minutes"
        )

        # 4. Persist Results
        processor.save_results("task_a_20_user_results.json")
        
    except FileNotFoundError:
        print("Error: 'task_a_filtered_data.json' not found. Ensure the preprocessing cell ran successfully.")

# Cell
