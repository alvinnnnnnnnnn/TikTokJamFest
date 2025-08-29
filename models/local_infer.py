import random
import re
from typing import Dict, List, Tuple
from utils.highlight import default_spans

class ReviewClassifier:
    """Local classifier matching API contract format"""
    
    def __init__(self):
        self.categories = ["valid", "ad", "irrelevant", "rant"]
        self.url_pattern = re.compile(r'https?://[^\s]+|www\.[^\s]+')
        self.promo_words = ['discount', 'coupon', 'promo', 'sale', 'deal', 'offer', 'free', 'visit our website']
        
    def _find_spans(self, text: str) -> List[List]:
        """Find highlighting spans in text"""
        spans = []
        
        # Find URLs
        for match in self.url_pattern.finditer(text):
            spans.append(["url", match.start(), match.end()])
            
        # Find promo words
        for word in self.promo_words:
            pattern = re.compile(rf'\b{re.escape(word)}\b', re.IGNORECASE)
            for match in pattern.finditer(text):
                spans.append(["promo", match.start(), match.end()])
                
        # Find "never been" phrases
        never_pattern = re.compile(r'\b(never been|haven\'t been|havent been)\b', re.IGNORECASE)
        for match in never_pattern.finditer(text):
            spans.append(["irrelevant", match.start(), match.end()])
            
        return spans
        
    def _get_violations(self, label: str, text: str) -> List[str]:
        """Get violation reasons based on classification"""
        violations = []
        
        if label == "ad":
            if any(word in text.lower() for word in self.promo_words):
                violations.append("Contains promotional content")
            if self.url_pattern.search(text):
                violations.append("Contains external links")
                
        elif label == "irrelevant":
            if "never been" in text.lower():
                violations.append("Review from non-visitor")
            if len(text.split()) < 5:
                violations.append("Insufficient content")
                
        elif label == "rant":
            if "!!!!" in text:
                violations.append("Excessive punctuation")
            if text.isupper():
                violations.append("All caps text")
                
        return violations
    
    def classify_review(self, text: str) -> Dict:
        """
        Classify single review matching API contract
        Returns: {label, scores, violations, spans}
        """
        # Determine primary label
        if "visit our website" in text.lower() or self.url_pattern.search(text):
            label = "ad"
            base_confidence = 0.85
        elif "never been" in text.lower():
            label = "irrelevant" 
            base_confidence = 0.78
        elif len(text.split()) < 5:
            label = "irrelevant"
            base_confidence = 0.65
        elif "!!!!" in text or text.isupper():
            label = "rant"
            base_confidence = 0.72
        else:
            label = "valid"
            base_confidence = random.uniform(0.6, 0.95)
            
        # Generate confidence scores for all categories
        scores = {}
        remaining_confidence = 1.0 - base_confidence
        
        scores[label] = base_confidence
        other_categories = [cat for cat in self.categories if cat != label]
        
        for i, cat in enumerate(other_categories):
            if i == len(other_categories) - 1:  # Last category gets remaining
                scores[cat] = remaining_confidence
            else:
                cat_score = random.uniform(0.01, remaining_confidence * 0.6)
                scores[cat] = cat_score
                remaining_confidence -= cat_score
                
        return {
            "label": label,
            "scores": scores,
            "violations": self._get_violations(label, text),
            "spans": self._find_spans(text)
        }
    
    def classify_batch(self, texts: List[str]) -> List[Dict]:
        """Classify multiple reviews matching API contract"""
        return [self.classify_review(text) for text in texts]

def infer_batch(texts: List[str]) -> List[Dict]:
    """
    Rule-based baseline classifier for testing.
    Returns list of classification results matching API contract.
    """
    results = []
    
    for text in texts:
        # Get spans using the utility function
        spans = default_spans(text)
        
        # Rule-based classification
        has_url = any(span[0] == "url" for span in spans)
        has_promo = any(span[0] == "promo" for span in spans)
        has_novisit = any(span[0] == "novisit" for span in spans)
        
        if has_url or has_promo:
            # Classify as ad
            label = "ad"
            scores = {"ad": 0.9, "valid": 0.05, "irrelevant": 0.03, "rant": 0.02}
            violations = ["No Advertisement"]
            
        elif has_novisit:
            # Classify as rant (per specification)
            label = "rant"  
            scores = {"rant": 0.85, "valid": 0.08, "irrelevant": 0.05, "ad": 0.02}
            violations = ["No Rant Without Visit"]
            
        else:
            # Valid review
            label = "valid"
            scores = {"valid": 0.88, "ad": 0.05, "irrelevant": 0.04, "rant": 0.03}
            violations = []
        
        # Convert spans from (type, start, end) to [type, start, end] format
        formatted_spans = [[span[0], span[1], span[2]] for span in spans]
        
        results.append({
            "label": label,
            "scores": scores,
            "violations": violations,
            "spans": formatted_spans
        })
    
    return results
