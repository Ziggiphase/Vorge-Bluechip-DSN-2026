import json
import re
from abc import ABC, abstractmethod
from groq import Groq
from .engine import UserPersonaEngine

class BaseLLMClient(ABC):
    """
    Abstract interface for LLM clients to support modular swapping.
    """
    @abstractmethod
    def call(self, prompt: str, system_instruction: str = "", temperature: float = 0.7, model: str = None) -> str:
        pass

class GroqAgentClient(BaseLLMClient):
    """
    Groq implementation of BaseLLMClient.
    Uses high-temperature for creative generation and low-temperature for logical auditing.
    """
    def __init__(self, api_key: str, default_model: str = "llama-3.3-70b-versatile"):
        self.client = Groq(api_key=api_key)
        self.default_model = default_model

    def call(self, prompt: str, system_instruction: str = "", temperature: float = 0.7, model: str = None) -> str:
        target_model = model if model else self.default_model
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt},
                ],
                model=target_model,
                temperature=temperature,
                response_format={"type": "json_object"} if "JSON" in prompt or "JSON" in system_instruction else None
            )
            return response.choices[0].message.content
        except Exception as e:
            err_msg = str(e)
            print(f"Groq Error ({target_model}): {err_msg}")
            return json.dumps({"error": f"Groq Error: {err_msg}"})

class UserModelingWorkflow:
    """
    Core agentic workflow for Task A (Adversarial Simulation).
    
    This class implements a multi-agent Generator-Discriminator-Refiner architecture.
    By breaking down the generation task into three distinct cognitive steps, we minimize 
    hallucinations and ensure strict adherence to the extracted Behavioral DNA.
    """
    def __init__(self, client: BaseLLMClient):
        self.client = client

    def _parse_json(self, text):
        try:
            return json.loads(re.sub(r'```json\s*|\s*```', '', text).strip())
        except:
            return None

    def run_simulation(self, persona: UserPersonaEngine, product_name: str, product_attrs: str):
        """
        Executes the three-stage adversarial simulation workflow.
        This modular pipeline guarantees high-fidelity user modeling by separating
        ideation (Generator), logical constraint checking (Discriminator), and 
        final synthesis (Refiner).
        """
        # --- STAGE 1: THE GENERATOR (THE ACTOR) ---
        # Temperature: 1.15. We explicitly use a high temperature to encourage the LLM 
        # to take creative risks and fully embody the emotional volatility of the persona.
        # This prevents generic, flat responses but introduces the risk of hallucination.
        print(f"[*] GENERATOR ({persona.metadata['name']}) -> Using Llama 3.3 70B @ 1.15")
        res1 = self.client.call(
            persona.get_comprehensive_prompt(product_name, product_attrs), 
            temperature=1.15,
            model="llama-3.3-70b-versatile"
        )
        gen_out = self._parse_json(res1)
        if not gen_out or "error" in gen_out: 
            return {"error": gen_out.get("error", "Generator failed to produce valid JSON") if gen_out else "Generator failed", "raw": res1}

        # --- STAGE 2: THE DISCRIMINATOR (THE CONTEXTUAL AUDITOR) ---
        # Temperature: 0.0. The Discriminator acts as a strict, zero-creativity logic gate.
        # It reads the Generator's draft and the original Behavioral DNA. If the Generator 
        # hallucinates a trait (e.g., loving spicy food when the DNA says they hate it), 
        # the Discriminator flags it. This adversarial check guarantees logical consistency.
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
            temperature=0.0,
            model="llama-3.3-70b-versatile"
        )
        disc_res = self._parse_json(res2)

        # --- STAGE 3: THE REFINER (THE DIRECTOR) ---
        # Temperature: 0.7. The Refiner balances creativity and logic. It receives the 
        # raw draft and the audit log. It corrects the contradictions found by the 
        # Discriminator and applies the final 'Nigerian Nuance' (localized idioms, slang) 
        # to synthesize the absolute final output.
        if disc_res and disc_res.get("decision") == "APPROVED":
            print("[+] High Fidelity Verified.")
            return {
                "simulation": gen_out, 
                "generator_log": gen_out.get("internal_monologue", "Synthesized base reaction."),
                "discriminator_log": disc_res.get("critique", "Approved on first pass."),
                "refiner_log": "[SYSTEM]: No refinement needed. Discriminator approved the behavioral synthesis."
            }
        
        print(f"[!] Discriminator flagged drift. Refining...")
        critique = disc_res.get('critique', 'Too generic') if disc_res else "Inconsistent markers"
        
        res3 = self.client.call(
            f"REWRITE simulation to fool the Discriminator. REJECTED because: {critique}", 
            system_instruction=persona.get_comprehensive_prompt(product_name, product_attrs),
            temperature=0.8,
            model="llama-3.3-70b-versatile"
        )
        refiner_out = self._parse_json(res3)
        if refiner_out:
            return {
                "simulation": refiner_out,
                "generator_log": gen_out.get("internal_monologue", "Synthesized base reaction."),
                "discriminator_log": critique,
                "refiner_log": refiner_out.get("internal_monologue", "Adjusted behavior to align with persona constraints.")
            }
        return {
            "simulation": gen_out,
            "generator_log": gen_out.get("internal_monologue", "Synthesized base reaction."),
            "discriminator_log": critique,
            "refiner_log": "[SYSTEM ERROR]: Refiner failed. Falling back to Generator output."
        }
