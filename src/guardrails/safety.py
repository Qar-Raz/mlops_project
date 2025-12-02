# src/guardrails/safety.py
"""
Guardrails module
Implements:
- InputGuardrails: input validation (length, PII, prompt injection, allowed topics)
- OutputGuardrails: output moderation (simple harmful / toxicity heuristics)
- GuardrailsManager: single point of use for app/testing; logs violations in-memory and to file
"""

import re
import logging
from typing import Dict, Tuple, List
from datetime import datetime
from .config import config

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class InputGuardrails:
    """
    Validate user inputs.
    Return a dict:
    {
      "valid": bool,
      "message": str,
      "violations": [ ... ]
    }
    """

    def __init__(self):
        self.config = config
        # compile regex patterns once
        self._pii_patterns = {k: re.compile(v, re.IGNORECASE) for k, v in config.pii_patterns.items()}
        self._injection_patterns = [re.compile(p, re.IGNORECASE) for p in config.injection_patterns]

    def _check_length(self, text: str) -> Tuple[bool, str]:
        if len(text) < self.config.min_query_length:
            return False, f"query shorter than min length {self.config.min_query_length}"
        if len(text) > self.config.max_query_length:
            return False, f"query longer than max length {self.config.max_query_length}"
        return True, ""

    def _detect_pii(self, text: str) -> List[str]:
        found = []
        if not self.config.pii_enabled:
            return found
        for name, rgx in self._pii_patterns.items():
            if rgx.search(text):
                found.append(name)
        return found

    def _detect_prompt_injection(self, text: str) -> List[str]:
        matches = []
        for rgx in self._injection_patterns:
            if rgx.search(text):
                matches.append(rgx.pattern)
        return matches

    def validate(self, user_input: str) -> Dict:
        result = {"valid": True, "message": "ok", "violations": []}
        if user_input is None:
            return {"valid": False, "message": "no input", "violations": ["no_input"]}

        # length checks
        ok, msg = self._check_length(user_input)
        if not ok:
            result["valid"] = False
            result["violations"].append({"type": "LENGTH", "detail": msg})

        # PII checks
        pii_found = self._detect_pii(user_input)
        if pii_found:
            result["valid"] = False
            result["violations"].append({"type": "PII", "detail": pii_found})

        # prompt injection checks
        inj = self._detect_prompt_injection(user_input)
        if inj:
            result["valid"] = False
            result["violations"].append({"type": "PROMPT_INJECTION", "detail": inj})

        # topic allowlist (optional)
        if hasattr(self.config, "allowed_topics") and self.config.allowed_topics:
            # simple token containment check (case-insensitive)
            txt = user_input.lower()
            if not any(topic.lower() in txt for topic in self.config.allowed_topics):
                result["valid"] = False
                result["violations"].append({"type": "TOPIC_NOT_ALLOWED", "detail": self.config.allowed_topics})

        if not result["valid"]:
            result["message"] = "input validation failed"

        return result


class OutputGuardrails:
    """
    Basic moderation of model output using keyword heuristics and configured harmful patterns.
    Return dict:
    {
      "ok": bool,
      "violations": [...]
    }
    """

    def __init__(self):
        self.config = config
        self._harmful_patterns = [re.compile(p, re.IGNORECASE) for p in getattr(config, "harmful_patterns", [])]
        # a small list of toxicity keywords for deterministic tests
        self._toxicity_keywords = [
            r"\bkill\b", r"\bdie\b", r"\bterror\b", r"\bstupid\b", r"\bidiot\b"
        ]
        self._toxicity_patterns = [re.compile(p, re.IGNORECASE) for p in self._toxicity_keywords]

    def moderate(self, text: str) -> Dict:
        res = {"ok": True, "violations": []}
        if text is None:
            return {"ok": True, "violations": []}

        # check harmful patterns (advising ingestion, etc.)
        for p in self._harmful_patterns:
            if p.search(text):
                res["ok"] = False
                res["violations"].append({"type": "HARMFUL_ADVICE", "pattern": p.pattern})

        # toxicity heuristics
        for p in self._toxicity_patterns:
            if p.search(text):
                res["ok"] = False
                res["violations"].append({"type": "TOXICITY", "pattern": p.pattern})

        return res


class GuardrailsManager:
    """
    Simple manager that wraps InputGuardrails + OutputGuardrails and logs violations.
    The design keeps a short in-memory log for tests and writes a single-line JSON per event to a log file.
    """

    def __init__(self, log_file: str = "guardrail_events.log"):
        self.input_guardrails = InputGuardrails()
        self.output_guardrails = OutputGuardrails()
        self.violation_log: List[Dict] = []
        self._log_file = log_file

    def check_input(self, user_input: str) -> Dict:
        result = self.input_guardrails.validate(user_input)
        if not result.get("valid", True):
            self._log_violation("INPUT", result["violations"])
        return result

    def check_output(self, llm_output: str) -> Dict:
        result = self.output_guardrails.moderate(llm_output)
        if not result.get("ok", True):
            self._log_violation("OUTPUT", result["violations"])
        return result

    def _log_violation(self, stage: str, violations: List[Dict]):
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "stage": stage,
            "violations": violations,
        }
        self.violation_log.append(entry)
        # append to file (safe text append)
        try:
            with open(self._log_file, "a", encoding="utf-8") as fh:
                fh.write(f"{entry}\n")
        except Exception as e:
            logger.exception("Failed to write guardrail log: %s", e)

    def get_violation_stats(self) -> Dict:
        return {
            "total_violations": len(self.violation_log),
            "by_stage": {
                "input": sum(1 for v in self.violation_log if v["stage"] == "INPUT"),
                "output": sum(1 for v in self.violation_log if v["stage"] == "OUTPUT"),
            },
            "recent_logs": self.violation_log[-10:],
        }
