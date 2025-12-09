import logging
import re
from better_profanity import profanity


class ValidationResult:
    """Simple container for validated output."""

    def __init__(self, text):
        self.validated_output = text


class LightweightGuard:
    def __init__(self):
        print("🛡️ Initializing Lightweight Guardrails (Optimized)...")

        # Load default profanity list
        profanity.load_censor_words()

        # --- FIX: Remove common plant/medical words from blocklist ---
        # "kill" -> kill fungus, kill weeds
        # "die" -> plant will die
        # "attack" -> fungal attack
        # "shoot" -> shoot blight
        safe_words = ["kill", "die", "attack", "shoot", "dead", "death"]

        # Extract original strings to filter them (VaryingString is not hashable)
        try:
            current_words = [w._original for w in profanity.CENSOR_WORDSET]
        except AttributeError:
            current_words = [str(w) for w in profanity.CENSOR_WORDSET]

        filtered_words = [w for w in current_words if w not in safe_words]
        profanity.load_censor_words(filtered_words)

        # --- CUSTOM BLOCKLISTS ---

        # 1. Hate Speech & Insults
        self.hate_words = [
            "stupid",
            "idiot",
            "dumb",
            "hate",
            "retard",
            "creep",
            "loser",
            "suck",
            "filth",
            "disgusting",
            "useless",
            "shut up",
            "bitch",
            "bastard",
            "cunt",
            "nigger",
            "faggot",
            "dyke",
            "tranny",
            "racist",
            "nazi",
            "hitler",
            "fascist",
            "bigot",
        ]

        # 2. Violence & Threat
        self.violence_words = [
            "kill you",
            "kill yourself",
            "death to",
            "murder",
            "stab",
            "bomb",
            "terrorist",
            "blow up",
            "slaughter",
            "execute",
            "torture",
            "behead",
            "gun",
            "knife",
            "weapon",
        ]

        # 3. Self-Harm
        self.self_harm_words = [
            "suicide",
            "end my life",
            "cut myself",
            "overdose",
            "hang myself",
            "want to die",
            "kill myself",
        ]

        # 4. Sexual Content
        self.sexual_words = ["sex", "porn", "nude", "naked", "erotic", "xxx", "hentai"]

        # Add to better_profanity for the catch-all check
        all_custom = (
            self.hate_words
            + self.violence_words
            + self.self_harm_words
            + self.sexual_words
        )
        profanity.add_censor_words(all_custom)

        # --- OPTIMIZATION: Pre-compile Regex ---
        # We use regex with word boundaries (\b) to prevent false positives.
        # e.g., "ass" won't trigger on "grass", "gun" won't trigger on "begun".
        self.patterns = {
            "SELF_HARM": self._compile_pattern(self.self_harm_words),
            "VIOLENCE": self._compile_pattern(self.violence_words),
            "SEXUAL": self._compile_pattern(self.sexual_words),
            # PII Patterns
            "PII_EMAIL": re.compile(
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", re.IGNORECASE
            ),
            # Pakistan Phone Numbers (Mobile: 03xx... or +923xx...)
            "PII_PHONE": re.compile(r"\b(?:\+92|92|0)?3\d{2}[ -]?\d{7}\b"),
        }

    def _compile_pattern(self, word_list):
        """Creates a compiled regex for a list of words with word boundaries."""
        # Escape words to handle special chars, join with OR (|), wrap in word boundaries (\b)
        pattern_str = r"\b(" + "|".join(map(re.escape, word_list)) + r")\b"
        return re.compile(pattern_str, re.IGNORECASE)

    def validate(self, text: str):
        """
        Checks text for specific categories of toxicity using optimized regex.
        """
        # 1. Check specific categories (Fast Regex)
        for category, pattern in self.patterns.items():
            match = pattern.search(text)
            if match:
                self._log_and_raise(text, category, match.group(0))

        # 2. Fallback to general profanity check (Library)
        if profanity.contains_profanity(text):
            self._log_and_raise(text, "HATE_PROFANITY", "general_profanity")

        return ValidationResult(text)

    def _log_and_raise(self, text, category, trigger_word):
        logging.warning(
            f"⚠️ Guardrail Blocked ({category}): Triggered by '{trigger_word}' in text: {text[:50]}..."
        )
        raise ValueError(f"UNSAFE:{category}")


def get_llm_guard():
    try:
        return LightweightGuard()
    except Exception as e:
        print(f"❌ Error initializing guard: {e}")
        return None
