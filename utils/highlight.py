import re
import html
from typing import List, Tuple

def default_spans(text: str) -> List[Tuple[str, int, int]]:
    """
    Find default highlighting spans for URLs, non-visitor phrases, and promo words.
    Returns list of (span_type, start, end) tuples.
    """
    spans = []
    
    # Find URLs
    url_pattern = re.compile(r'https?://[^\s]+|www\.[^\s]+')
    for match in url_pattern.finditer(text):
        spans.append(("url", match.start(), match.end()))
    
    # Find "never been" or "not visited" phrases
    novisit_pattern = re.compile(r'\b(never been|not visited|haven\'t been|havent been)\b', re.IGNORECASE)
    for match in novisit_pattern.finditer(text):
        spans.append(("novisit", match.start(), match.end()))
    
    # Find promo words
    promo_words = ['discount', 'promo', 'sale', 'coupon', 'deal']
    for word in promo_words:
        pattern = re.compile(rf'\b{re.escape(word)}\b', re.IGNORECASE)
        for match in pattern.finditer(text):
            spans.append(("promo", match.start(), match.end()))
    
    # Sort spans by start position for easier processing
    spans.sort(key=lambda x: x[1])
    
    return spans

def render_html_with_spans(text: str, spans: List[Tuple[str, int, int]]) -> str:
    """
    Render text as HTML with highlighted spans. Assumes non-overlapping spans.
    Span colors: url=#fde68a, novisit=#fecaca, promo=#bbf7d0
    """
    # Define colors for each span type
    span_colors = {
        'url': '#fde68a',      # Light yellow
        'novisit': '#fecaca',  # Light red
        'promo': '#bbf7d0'     # Light green
    }
    
    if not spans:
        return html.escape(text)
    
    # Sort spans by start position
    sorted_spans = sorted(spans, key=lambda x: x[1])
    
    result = []
    last_pos = 0
    
    for span_type, start, end in sorted_spans:
        # Add text before the span (escaped)
        if start > last_pos:
            result.append(html.escape(text[last_pos:start]))
        
        # Add the highlighted span
        span_text = html.escape(text[start:end])
        color = span_colors.get(span_type, '#f0f0f0')  # Default gray if unknown type
        result.append(f'<span style="background-color: {color}; padding: 1px 2px; border-radius: 2px;">{span_text}</span>')
        
        last_pos = end
    
    # Add remaining text after last span
    if last_pos < len(text):
        result.append(html.escape(text[last_pos:]))
    
    return ''.join(result)

class TextHighlighter:
    """Utility for highlighting specific patterns in review text"""
    
    def __init__(self):
        self.url_pattern = re.compile(r'https?://[^\s]+|www\.[^\s]+')
        self.never_been_pattern = re.compile(r'\b(never been|haven\'t been|havent been)\b', re.IGNORECASE)
        self.promo_words = ['discount', 'coupon', 'promo', 'sale', 'deal', 'offer', 'free', 'visit our website']
        
    def highlight_urls(self, text: str) -> str:
        """Highlight URLs in text"""
        return self.url_pattern.sub(r'<mark style="background-color: #ffeb3b;">\\g<0></mark>', text)
    
    def highlight_never_been(self, text: str) -> str:
        """Highlight 'never been' phrases"""
        return self.never_been_pattern.sub(r'<mark style="background-color: #f44336; color: white;">\\g<0></mark>', text)
    
    def highlight_promo_words(self, text: str) -> str:
        """Highlight promotional words"""
        for word in self.promo_words:
            pattern = re.compile(rf'\b{re.escape(word)}\b', re.IGNORECASE)
            text = pattern.sub(rf'<mark style="background-color: #ff9800; color: white;">{word}</mark>', text)
        return text
    
    def highlight_all(self, text: str) -> str:
        """Apply all highlighting"""
        text = self.highlight_urls(text)
        text = self.highlight_never_been(text)
        text = self.highlight_promo_words(text)
        return text
