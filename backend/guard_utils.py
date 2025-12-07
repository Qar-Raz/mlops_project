import logging
from better_profanity import profanity

class LightweightGuard:
    def __init__(self):
        print("🛡️ Initializing Lightweight Guardrails...")
        
        # Load default profanity list (standard English swear words)
        profanity.load_censor_words()
        
        # --- CUSTOM BLOCKLISTS ---
        
        # 1. Hate Speech & Insults
        self.hate_words = [
            "stupid", "idiot", "dumb", "hate", "ugly", "fat", "retard", "creep",
            "loser", "suck", "trash", "filth", "disgusting", "useless", "shut up",
            "bitch", "bastard", "cunt", "nigger", "faggot", "dyke", "tranny", # Slurs
            "racist", "nazi", "hitler", "fascist", "bigot"
        ]

        # 2. Violence & Threat
        # Note: We must be careful with words like 'kill' (e.g. 'kill weeds' is okay).
        # We target specific aggressive phrases.
        self.violence_words = [
            "kill you", "kill yourself", "die", "death to", "murder", "stab", 
            "shoot", "bomb", "terrorist", "blow up", "attack", "slaughter", 
            "execute", "torture", "behead", "gun", "knife", "weapon"
        ]

        # 3. Self-Harm (Crucial for AI safety)
        self.self_harm_words = [
            "suicide", "end my life", "cut myself", "overdose", "hang myself",
            "want to die", "kill myself"
        ]

     
        # Combine all for the general filter
        all_custom = self.hate_words + self.violence_words + self.self_harm_words + self.sexual_words
        profanity.add_censor_words(all_custom)

    def validate(self, text: str):
        """
        Checks text for specific categories of toxicity.
        Returns the object if safe, raises ValueError with CATEGORY if unsafe.
        """
        text_lower = text.lower()

        # Check specific categories to give better metrics
        if any(w in text_lower for w in self.self_harm_words):
            self._log_and_raise(text, "SELF_HARM")
            
        if any(w in text_lower for w in self.violence_words):
            self._log_and_raise(text, "VIOLENCE")

        if any(w in text_lower for w in self.sexual_words):
            self._log_and_raise(text, "SEXUAL")

        # Fallback to general profanity/hate check
        if profanity.contains_profanity(text):
            self._log_and_raise(text, "HATE_PROFANITY")
        
        # If safe, return object
        class Result:
            def __init__(self, t): self.validated_output = t
        return Result(text)

    def _log_and_raise(self, text, category):
        logging.warning(f"⚠️ Guardrail Blocked ({category}): {text[:30]}...")
        # We pass the category in the error message so app.py can record it
        raise ValueError(f"UNSAFE:{category}")

def get_llm_guard():
    try:
        return LightweightGuard()
    except Exception as e:
        print(f"❌ Error initializing guard: {e}")
        return None