import re
import logging
from typing import Dict, Tuple, List
from datetime import datetime
from .config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InputGuardrails:
    """Validates user inputs for plant disease queries"""
    
    def __init__(self):
        self.config = config
        
        # PII patterns
        self.pii_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
        }
        
        # Prompt injection patterns
        self.injection_patterns = [
            r'ignore previous instructions?',
            r'disregard.*(?:above|instructions?)',
            r'forget.*instructions?',
            r'you are now',
            r'new instructions?',
            r'system\s*:',
            r'<\|.*?\|>',
            r'act as (?:if|though)',
            r'pretend (?:to be|you are)',
        ]
        
    def check_query_length(self, text: str) -> Tuple[bool, str]:
        """Check if query length is within acceptable range"""
        length = len(text.strip())
        
        if length < self.config.min_query_length:
            return False, f"Query too short ({length} chars). Minimum: {self.config.min_query_length}"
        
        if length > self.config.max_query_length:
            return False, f"Query too long ({length} chars). Maximum: {self.config.max_query_length}"
        
        return True, "Length OK"
    
    def detect_pii(self, text: str) -> Tuple[bool, List[Dict]]:
        """Detect Personally Identifiable Information"""
        if not self.config.pii_enabled:
            return False, []
        
        detected = []
        
        for pii_type, pattern in self.pii_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                detected.append({
                    'type': pii_type,
                    'count': len(matches),
                })
        
        return len(detected) > 0, detected
    
    def detect_prompt_injection(self, text: str) -> Tuple[bool, List[str]]:
        """Detect potential prompt injection attempts"""
        if not self.config.injection_detection_enabled:
            return False, []
        
        detected = []
        
        for pattern in self.injection_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                detected.append(pattern)
        
        return len(detected) > 0, detected
    
    def validate(self, user_input: str) -> Dict:
        """Main validation method"""
        result = {
            'valid': True,
            'violations': [],
            'warnings': [],
            'message': 'Input passed validation',
        }
        
        # Check 1: Query length
        length_ok, length_msg = self.check_query_length(user_input)
        if not length_ok:
            result['valid'] = False
            result['violations'].append({
                'type': 'INVALID_LENGTH',
                'message': length_msg
            })
            logger.warning(f"Length validation failed: {length_msg}")
        
        # Check 2: PII detection
        has_pii, pii_detected = self.detect_pii(user_input)
        if has_pii:
            result['valid'] = False
            result['violations'].append({
                'type': 'PII_DETECTED',
                'details': pii_detected
            })
            logger.warning(f"PII detected: {pii_detected}")
        
        # Check 3: Prompt injection
        has_injection, injection_patterns = self.detect_prompt_injection(user_input)
        if has_injection:
            result['valid'] = False
            result['violations'].append({
                'type': 'PROMPT_INJECTION',
                'patterns': injection_patterns
            })
            logger.warning(f"Prompt injection detected: {injection_patterns}")
        
        if not result['valid']:
            result['message'] = 'Input validation failed'
        
        return result


class OutputGuardrails:
    """Moderates LLM outputs for plant disease advice"""
    
    def __init__(self):
        self.config = config
        
        # Harmful advice patterns
        self.harmful_patterns = [
            r'(?:drink|consume|eat|ingest).*(?:pesticide|chemical|fungicide)',
            r'apply to (?:skin|body|eyes)',
            r'use (?:internally|orally)',
        ]
        
        # Toxicity keywords
        self.toxic_keywords = [
            'idiot', 'stupid', 'moron', 'dumb',
        ]
    
    def detect_harmful_advice(self, text: str) -> Tuple[bool, List[str]]:
        """Detect potentially harmful agricultural advice"""
        text_lower = text.lower()
        detected = []
        
        for pattern in self.harmful_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            if matches:
                detected.append(pattern)
        
        return len(detected) > 0, detected
    
    def detect_toxicity(self, text: str) -> Tuple[bool, float]:
        """Simple toxicity detection"""
        text_lower = text.lower()
        toxic_count = sum(1 for keyword in self.toxic_keywords if keyword in text_lower)
        
        words = text_lower.split()
        if len(words) == 0:
            return False, 0.0
        
        toxicity_score = toxic_count / len(words)
        is_toxic = toxicity_score > self.config.toxicity_threshold
        
        return is_toxic, toxicity_score
    
    def check_response_length(self, text: str) -> bool:
        """Ensure response isn't too short"""
        return len(text.strip()) >= self.config.min_response_length
    
    def moderate(self, llm_output: str) -> Dict:
        """Main moderation method"""
        result = {
            'valid': True,
            'violations': [],
            'warnings': [],
            'message': 'Output passed moderation',
        }
        
        # Check 1: Harmful advice
        has_harmful, harmful_patterns = self.detect_harmful_advice(llm_output)
        if has_harmful:
            result['valid'] = False
            result['violations'].append({
                'type': 'HARMFUL_ADVICE',
                'patterns': harmful_patterns
            })
            logger.error(f"CRITICAL: Harmful advice detected: {harmful_patterns}")
        
        # Check 2: Toxicity
        is_toxic, toxicity_score = self.detect_toxicity(llm_output)
        if is_toxic:
            result['valid'] = False
            result['violations'].append({
                'type': 'TOXICITY',
                'score': toxicity_score
            })
            logger.warning(f"Toxic content detected: score={toxicity_score}")
        
        # Check 3: Response length
        if not self.check_response_length(llm_output):
            result['valid'] = False
            result['violations'].append({
                'type': 'INSUFFICIENT_LENGTH',
            })
            logger.warning("Response too short")
        
        if not result['valid']:
            result['message'] = 'Output moderation failed'
        
        return result


class GuardrailsManager:
    """Orchestrates all guardrails with monitoring"""
    
    def __init__(self):
        self.input_guardrails = InputGuardrails()
        self.output_guardrails = OutputGuardrails()
        self.violation_log = []
    
    def check_input(self, user_input: str) -> Dict:
        """Validate user input"""
        result = self.input_guardrails.validate(user_input)
        
        if not result['valid']:
            self._log_violation('INPUT', result['violations'])
        
        return result
    
    def check_output(self, llm_output: str) -> Dict:
        """Moderate LLM output"""
        result = self.output_guardrails.moderate(llm_output)
        
        if not result['valid']:
            self._log_violation('OUTPUT', result['violations'])
        
        return result
    
    def _log_violation(self, stage: str, violations: List[Dict]):
        """Log guardrail violations"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'stage': stage,
            'violations': violations,
        }
        
        self.violation_log.append(log_entry)
        logger.error(f"Guardrail violation at {stage}: {violations}")
    
    def get_violation_stats(self) -> Dict:
        """Get violation statistics"""
        return {
            'total_violations': len(self.violation_log),
            'by_stage': {
                'input': sum(1 for v in self.violation_log if v['stage'] == 'INPUT'),
                'output': sum(1 for v in self.violation_log if v['stage'] == 'OUTPUT')
            },
            'recent_logs': self.violation_log[-10:]
        }
