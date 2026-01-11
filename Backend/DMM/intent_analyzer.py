"""
Intent Analyzer
Natural Language Understanding component for extracting user intent
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum


class IntentType(Enum):
    """Enumeration of intent types"""
    GENERATE = "generate"
    SEND = "send"
    SEARCH = "search"
    CONTROL = "control"
    QUERY = "query"
    MODIFY = "modify"
    DELETE = "delete"
    CREATE = "create"
    UNKNOWN = "unknown"


class IntentAnalyzer:
    """
    Natural Language Understanding module for intent extraction
    
    Features:
    - Entity recognition (names, dates, locations)
    - Intent classification
    - Parameter extraction
    - Context-aware parsing
    """
    
    def __init__(self):
        self.intent_patterns = self._load_intent_patterns()
        self.entity_extractors = self._load_entity_extractors()
        self.context_window = []
        self.max_context_length = 5
        
    def _load_intent_patterns(self) -> Dict[str, List[str]]:
        """
        Load regex patterns for intent matching
        
        Returns:
            Dictionary of intent patterns
        """
        patterns = {
            'generate': [
                r'(create|generate|make|build)\s+(a\s+)?(pdf|word|ppt|image|excel)',
                r'(write|compose)\s+(document|report|presentation)',
            ],
            'send': [
                r'(send|email|message|share)\s+.*\s+to',
                r'(forward|transmit)\s+',
            ],
            'search': [
                r'(search|find|look\s+for|locate)',
                r'(what|where|who)\s+is',
            ],
            'control': [
                r'(open|close|launch|start|stop)\s+(app|application|program)',
                r'(set|adjust|change)\s+(volume|brightness)',
            ]
        }
        return patterns
    
    def _load_entity_extractors(self) -> Dict[str, Any]:
        """
        Load entity extraction models
        
        Returns:
            Dictionary of entity extractors
        """
        extractors = {
            'person': self._extract_person_names,
            'date': self._extract_dates,
            'location': self._extract_locations,
            'email': self._extract_emails,
            'file': self._extract_file_references,
        }
        return extractors
    
    def analyze(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze user input to extract intent and entities
        
        Args:
            text: User input text
            context: Conversation context
            
        Returns:
            Analysis result containing:
                - intent_type: Primary intent
                - entities: Extracted entities
                - parameters: Extracted parameters
                - confidence: Confidence score
        """
        # Add to context window
        self.context_window.append(text)
        if len(self.context_window) > self.max_context_length:
            self.context_window.pop(0)
        
        # Extract intent
        intent_type = self._classify_intent(text)
        
        # Extract entities
        entities = self._extract_entities(text)
        
        # Extract parameters
        parameters = self._extract_parameters(text, intent_type)
        
        # Calculate confidence
        confidence = self._calculate_confidence(text, intent_type, entities)
        
        result = {
            'intent_type': intent_type.value,
            'entities': entities,
            'parameters': parameters,
            'confidence': confidence,
            'context': self.context_window.copy()
        }
        
        return result
    
    def _classify_intent(self, text: str) -> IntentType:
        """
        Classify intent using pattern matching and ML
        
        Args:
            text: Input text
            
        Returns:
            Classified intent type
        """
        text_lower = text.lower()
        
        # Try pattern matching
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return IntentType(intent)
        
        # Fallback to ML classifier
        # (Would use trained model in production)
        
        return IntentType.UNKNOWN
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract named entities from text
        
        Args:
            text: Input text
            
        Returns:
            Dictionary of entity types and values
        """
        entities = {
            'persons': self._extract_person_names(text),
            'dates': self._extract_dates(text),
            'locations': self._extract_locations(text),
            'emails': self._extract_emails(text),
            'files': self._extract_file_references(text),
        }
        
        # Remove empty lists
        entities = {k: v for k, v in entities.items() if v}
        
        return entities
    
    def _extract_parameters(self, text: str, intent: IntentType) -> Dict[str, Any]:
        """
        Extract parameters specific to intent type
        
        Args:
            text: Input text
            intent: Classified intent
            
        Returns:
            Extracted parameters
        """
        parameters = {}
        
        if intent == IntentType.GENERATE:
            parameters['topic'] = self._extract_topic(text)
            parameters['format'] = self._extract_format(text)
            parameters['pages'] = self._extract_page_count(text)
        
        elif intent == IntentType.SEND:
            parameters['recipient'] = self._extract_recipient(text)
            parameters['content'] = self._extract_content(text)
        
        return parameters
    
    def _extract_person_names(self, text: str) -> List[str]:
        """Extract person names using NER"""
        # Named Entity Recognition logic
        return []
    
    def _extract_dates(self, text: str) -> List[str]:
        """Extract dates and times"""
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{2,4}',
            r'\d{4}-\d{2}-\d{2}',
            r'(today|tomorrow|yesterday|next week)',
        ]
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text.lower())
            dates.extend(matches)
        return dates
    
    def _extract_locations(self, text: str) -> List[str]:
        """Extract location names"""
        return []
    
    def _extract_emails(self, text: str) -> List[str]:
        """Extract email addresses"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.findall(email_pattern, text)
    
    def _extract_file_references(self, text: str) -> List[str]:
        """Extract file names and references"""
        file_pattern = r'\b\w+\.(pdf|docx|pptx|xlsx|png|jpg|txt)\b'
        return re.findall(file_pattern, text.lower())
    
    def _extract_topic(self, text: str) -> str:
        """Extract topic for content generation"""
        # Topic extraction logic
        return ""
    
    def _extract_format(self, text: str) -> str:
        """Extract desired output format"""
        formats = ['pdf', 'word', 'ppt', 'excel', 'image']
        text_lower = text.lower()
        for fmt in formats:
            if fmt in text_lower:
                return fmt
        return "unknown"
    
    def _extract_page_count(self, text: str) -> int:
        """Extract page count from text"""
        match = re.search(r'(\d+)\s*(page|pages)', text.lower())
        if match:
            return int(match.group(1))
        return 10  # Default
    
    def _extract_recipient(self, text: str) -> str:
        """Extract message recipient"""
        # Look for patterns like "to John", "send to Alice"
        match = re.search(r'\bto\s+(\w+)', text.lower())
        if match:
            return match.group(1)
        return ""
    
    def _extract_content(self, text: str) -> str:
        """Extract message content"""
        return text
    
    def _calculate_confidence(self, text: str, intent: IntentType, entities: Dict) -> float:
        """
        Calculate confidence score for the analysis
        
        Args:
            text: Input text
            intent: Classified intent
            entities: Extracted entities
            
        Returns:
            Confidence score (0-1)
        """
        confidence = 0.7  # Base confidence
        
        # Increase confidence if intent matches pattern
        if intent != IntentType.UNKNOWN:
            confidence += 0.15
        
        # Increase confidence if entities found
        if entities:
            confidence += 0.15
        
        return min(confidence, 1.0)
