# src/app/guardrails.py
import re
import logging
from typing import Optional, List

# Setup logger as per D3 requirements
logger = logging.getLogger("uvicorn.error")

class SecurityGuard:
    """
    Custom Policy Engine for Input/Output Guardrails.
    Satisfies Milestone 2 - D3.
    """
    
    def __init__(self):
        # Regex patterns for PII (Email, Phone)
        self.email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        self.phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        
        # Simple keywords for Injection/Toxicity
        self.injection_keywords = ["ignore previous instructions", "system prompt", "delete all"]
        self.toxic_keywords = ["hate", "kill", "stupid", "idiot"] # Extend this list as needed

    def validate_input(self, query: str) -> dict:
        """
        D3: Input Validation (PII detection, prompt injection filter).
        """
        issues = []
        
        # Check 1: PII Detection
        if re.search(self.email_pattern, query) or re.search(self.phone_pattern, query):
            msg = "PII detected in input query."
            logger.warning(f"GUARDRAIL_FAIL_INPUT: {msg} | Query: {query}")
            issues.append("Input contains sensitive data (PII).")

        # Check 2: Prompt Injection
        if any(keyword in query.lower() for keyword in self.injection_keywords):
            msg = "Potential prompt injection detected."
            logger.warning(f"GUARDRAIL_FAIL_INPUT: {msg} | Query: {query}")
            issues.append("Input contains restricted commands.")

        if issues:
            return {"valid": False, "message": " | ".join(issues)}
        
        return {"valid": True, "message": "Input safe"}

    def validate_output(self, response: str) -> dict:
        """
        D3: Output Moderation (toxicity threshold, hallucination filter).
        """
        # Check 1: Toxicity/Safety
        if any(keyword in response.lower() for keyword in self.toxic_keywords):
            logger.warning("GUARDRAIL_FAIL_OUTPUT: Toxic content generated.")
            return {"valid": False, "message": "Response blocked due to safety guidelines."}
            
        # Check 2: Hallucination Check (Placeholder for simple logic)
        # In a real scenario, you might compare embeddings or confidence scores here.
        if "I don't know" not in response and len(response) < 5:
             logger.warning("GUARDRAIL_FAIL_OUTPUT: Response too short/potential hallucination.")
        
        return {"valid": True, "message": "Output safe"}

# Singleton instance to be imported in main.py
guard = SecurityGuard()
