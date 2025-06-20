# Natural Language Processing Utilities
# Based on AI-CICD and Social MCP Server patterns

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple, Union
import re
import json
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

# Base Types
@dataclass
class ProcessingResult:
    """Result of NLP processing"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    confidence: float = 0.0
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []

class ProcessingIntent(Enum):
    """Common intents for MCP servers"""
    GENERATE_CONTENT = "generate_content"
    ANALYZE_DATA = "analyze_data"
    CONFIGURE_SYSTEM = "configure_system"
    DEPLOY_APPLICATION = "deploy_application"
    SCHEDULE_TASK = "schedule_task"
    UNKNOWN = "unknown"

# Natural Language Processors
class BaseNLProcessor(ABC):
    """Base class for natural language processors"""
    
    def __init__(self, name: str):
        self.name = name
        self.patterns = {}
        self.keywords = {}
    
    @abstractmethod
    async def process(self, text: str, context: Optional[Dict[str, Any]] = None) -> ProcessingResult:
        """Process natural language input"""
        pass
    
    def extract_keywords(self, text: str, keyword_map: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Extract keywords based on predefined mappings"""
        found_keywords = {}
        text_lower = text.lower()
        
        for category, keywords in keyword_map.items():
            found = []
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    found.append(keyword)
            if found:
                found_keywords[category] = found
        
        return found_keywords
    
    def extract_with_regex(self, text: str, patterns: Dict[str, str]) -> Dict[str, Any]:
        """Extract data using regex patterns"""
        extracted = {}
        
        for key, pattern in patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                extracted[key] = matches[0] if len(matches) == 1 else matches
        
        return extracted

class RequirementsProcessor(BaseNLProcessor):
    """Process deployment requirements (AI-CICD pattern)"""
    
    def __init__(self):
        super().__init__("requirements_processor")
        
        # Keywords for different categories
        self.language_keywords = {
            'python': ['python', 'django', 'flask', 'fastapi', 'pip', 'requirements.txt'],
            'nodejs': ['node', 'nodejs', 'npm', 'yarn', 'package.json', 'express'],
            'java': ['java', 'spring', 'maven', 'gradle', 'jar'],
            'go': ['go', 'golang', 'mod'],
            'ruby': ['ruby', 'rails', 'gem', 'bundler'],
            'php': ['php', 'laravel', 'composer'],
            'dotnet': ['.net', 'dotnet', 'c#', 'csharp']
        }
        
        self.environment_keywords = {
            'development': ['dev', 'development', 'local'],
            'staging': ['staging', 'test', 'qa'],
            'production': ['prod', 'production', 'live']
        }
        
        self.trigger_keywords = {
            'push': ['push', 'commit', 'merge'],
            'pull_request': ['pr', 'pull request', 'review'],
            'schedule': ['schedule', 'cron', 'daily', 'weekly'],
            'manual': ['manual', 'on-demand', 'trigger']
        }
        
        self.cloud_keywords = {
            'aws': ['aws', 'amazon', 'ec2', 'lambda', 'ecs'],
            'azure': ['azure', 'microsoft'],
            'gcp': ['gcp', 'google cloud', 'gke'],
            'kubernetes': ['k8s', 'kubernetes', 'kubectl']
        }
        
        # Regex patterns
        self.patterns = {
            'app_name': r'(?:app|application|service)(?:\s+(?:called|named))?\s+([a-zA-Z0-9-_]+)',
            'version': r'version\s+([0-9]+(?:\.[0-9]+)*)',
            'port': r'port\s+(\d+)',
            'database': r'(postgres|mysql|mongodb|redis)',
            'packages': r'(?:with|include|install)\s+([a-zA-Z0-9\s,-]+?)(?:\s+packages?)?(?:\s|$)',
        }
    
    async def process(self, text: str, context: Optional[Dict[str, Any]] = None) -> ProcessingResult:
        """Process deployment requirements text"""
        try:
            # Extract basic information
            app_name = self._extract_app_name(text)
            language = self._extract_language(text)
            environments = self._extract_environments(text)
            triggers = self._extract_triggers(text)
            cloud_providers = self._extract_cloud_providers(text)
            
            # Extract additional details
            extracted_data = self.extract_with_regex(text, self.patterns)
            
            # Determine security and monitoring requirements
            security_required = self._requires_security(text)
            monitoring_required = self._requires_monitoring(text)
            
            # Calculate confidence based on extracted information
            confidence = self._calculate_confidence({
                'app_name': app_name,
                'language': language,
                'environments': environments,
                'triggers': triggers
            })
            
            result_data = {
                'application': app_name,
                'language': language,
                'environments': environments,
                'triggers': triggers,
                'cloud_providers': cloud_providers,
                'security_required': security_required,
                'monitoring_required': monitoring_required,
                'extracted_details': extracted_data,
                'raw_text': text
            }
            
            return ProcessingResult(
                success=True,
                data=result_data,
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"Requirements processing failed: {e}")
            return ProcessingResult(
                success=False,
                errors=[str(e)]
            )
    
    def _extract_app_name(self, text: str) -> str:
        """Extract application name"""
        match = re.search(self.patterns['app_name'], text, re.IGNORECASE)
        return match.group(1) if match else 'my-app'
    
    def _extract_language(self, text: str) -> str:
        """Extract programming language"""
        found_languages = self.extract_keywords(text, self.language_keywords)
        if found_languages:
            # Return the first language found
            return list(found_languages.keys())[0]
        return 'nodejs'  # Default
    
    def _extract_environments(self, text: str) -> List[str]:
        """Extract target environments"""
        found_envs = self.extract_keywords(text, self.environment_keywords)
        if found_envs:
            return list(found_envs.keys())
        return ['staging', 'production']  # Default
    
    def _extract_triggers(self, text: str) -> List[str]:
        """Extract CI/CD triggers"""
        found_triggers = self.extract_keywords(text, self.trigger_keywords)
        if found_triggers:
            return list(found_triggers.keys())
        return ['push']  # Default
    
    def _extract_cloud_providers(self, text: str) -> List[str]:
        """Extract cloud providers"""
        found_providers = self.extract_keywords(text, self.cloud_keywords)
        return list(found_providers.keys())
    
    def _requires_security(self, text: str) -> bool:
        """Check if security scanning is required"""
        security_keywords = ['security', 'scan', 'audit', 'vulnerability', 'secure']
        return any(keyword in text.lower() for keyword in security_keywords)
    
    def _requires_monitoring(self, text: str) -> bool:
        """Check if monitoring is required"""
        monitoring_keywords = ['monitor', 'alert', 'observability', 'metrics', 'logging']
        return any(keyword in text.lower() for keyword in monitoring_keywords)
    
    def _calculate_confidence(self, extracted_data: Dict[str, Any]) -> float:
        """Calculate confidence score based on extracted data"""
        score = 0.0
        max_score = 4.0
        
        if extracted_data['app_name'] != 'my-app':
            score += 1.0
        
        if extracted_data['language'] != 'nodejs':
            score += 1.0
        
        if extracted_data['environments']:
            score += 1.0
        
        if extracted_data['triggers']:
            score += 1.0
        
        return score / max_score

class ContentRequestProcessor(BaseNLProcessor):
    """Process social media content requests (Social MCP pattern)"""
    
    def __init__(self):
        super().__init__("content_processor")
        
        self.platform_keywords = {
            'instagram': ['instagram', 'ig', 'insta', 'photo', 'story', 'reel'],
            'twitter': ['twitter', 'tweet', 'x.com', 'thread'],
            'tiktok': ['tiktok', 'video', 'short', 'viral'],
            'linkedin': ['linkedin', 'professional', 'business'],
            'facebook': ['facebook', 'fb', 'post']
        }
        
        self.tone_keywords = {
            'professional': ['professional', 'business', 'formal', 'corporate'],
            'casual': ['casual', 'friendly', 'relaxed', 'informal'],
            'funny': ['funny', 'humorous', 'joke', 'meme', 'witty'],
            'inspirational': ['inspirational', 'motivational', 'uplifting', 'positive'],
            'educational': ['educational', 'learn', 'teach', 'explain', 'informative']
        }
        
        self.content_type_keywords = {
            'photo': ['photo', 'image', 'picture', 'pic'],
            'video': ['video', 'clip', 'movie', 'recording'],
            'story': ['story', 'stories', 'temporary'],
            'carousel': ['carousel', 'multiple', 'gallery', 'slideshow'],
            'live': ['live', 'streaming', 'broadcast']
        }
        
        self.patterns = {
            'hashtag_count': r'(\d+)\s*hashtags?',
            'character_limit': r'(?:under|max|maximum)\s*(\d+)\s*(?:characters?|chars?)',
            'mention': r'@([a-zA-Z0-9_]+)',
            'emoji_request': r'(?:with|add|include)\s+emojis?',
        }
    
    async def process(self, text: str, context: Optional[Dict[str, Any]] = None) -> ProcessingResult:
        """Process content generation request"""
        try:
            # Extract platform information
            platforms = self._extract_platforms(text)
            
            # Extract tone and style
            tone = self._extract_tone(text)
            
            # Extract content type
            content_type = self._extract_content_type(text)
            
            # Extract topic/subject
            topic = self._extract_topic(text)
            
            # Extract specific requirements
            extracted_data = self.extract_with_regex(text, self.patterns)
            
            # Determine additional requirements
            include_image = self._should_include_image(text)
            include_hashtags = self._should_include_hashtags(text)
            
            confidence = self._calculate_content_confidence({
                'platforms': platforms,
                'tone': tone,
                'topic': topic
            })
            
            result_data = {
                'platforms': platforms if platforms else ['instagram'],
                'tone': tone,
                'content_type': content_type,
                'topic': topic,
                'include_image': include_image,
                'include_hashtags': include_hashtags,
                'hashtag_count': int(extracted_data.get('hashtag_count', 5)),
                'character_limit': int(extracted_data.get('character_limit', 0)) if extracted_data.get('character_limit') else None,
                'mentions': extracted_data.get('mention', []),
                'extracted_details': extracted_data,
                'raw_text': text
            }
            
            return ProcessingResult(
                success=True,
                data=result_data,
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"Content request processing failed: {e}")
            return ProcessingResult(
                success=False,
                errors=[str(e)]
            )
    
    def _extract_platforms(self, text: str) -> List[str]:
        """Extract target platforms"""
        found_platforms = self.extract_keywords(text, self.platform_keywords)
        return list(found_platforms.keys())
    
    def _extract_tone(self, text: str) -> str:
        """Extract content tone"""
        found_tones = self.extract_keywords(text, self.tone_keywords)
        if found_tones:
            return list(found_tones.keys())[0]
        return 'casual'  # Default
    
    def _extract_content_type(self, text: str) -> str:
        """Extract content type"""
        found_types = self.extract_keywords(text, self.content_type_keywords)
        if found_types:
            return list(found_types.keys())[0]
        return 'photo'  # Default
    
    def _extract_topic(self, text: str) -> str:
        """Extract main topic/subject"""
        # Remove platform and tone keywords to isolate topic
        cleaned_text = text.lower()
        
        # Remove known keywords
        all_keywords = []
        for keyword_group in [self.platform_keywords, self.tone_keywords, self.content_type_keywords]:
            for keywords in keyword_group.values():
                all_keywords.extend(keywords)
        
        for keyword in all_keywords:
            cleaned_text = cleaned_text.replace(keyword, '')
        
        # Remove common instruction words
        instruction_words = ['create', 'generate', 'make', 'post', 'about', 'for', 'with', 'the', 'a', 'an']
        for word in instruction_words:
            cleaned_text = cleaned_text.replace(f' {word} ', ' ')
        
        # Clean up and return
        topic = cleaned_text.strip()
        return topic if topic else 'general content'
    
    def _should_include_image(self, text: str) -> bool:
        """Determine if image should be included"""
        image_indicators = ['image', 'photo', 'picture', 'visual', 'graphic']
        return any(indicator in text.lower() for indicator in image_indicators)
    
    def _should_include_hashtags(self, text: str) -> bool:
        """Determine if hashtags should be included"""
        hashtag_indicators = ['hashtag', '#', 'tag']
        return any(indicator in text.lower() for indicator in hashtag_indicators) or True  # Default to True
    
    def _calculate_content_confidence(self, extracted_data: Dict[str, Any]) -> float:
        """Calculate confidence score for content processing"""
        score = 0.0
        max_score = 3.0
        
        if extracted_data['platforms']:
            score += 1.0
        
        if extracted_data['tone'] != 'casual':
            score += 1.0
        
        if extracted_data['topic'] and extracted_data['topic'] != 'general content':
            score += 1.0
        
        return score / max_score

# Intent Classification
class IntentClassifier:
    """Classify user intent for MCP tools"""
    
    def __init__(self):
        self.intent_patterns = {
            ProcessingIntent.GENERATE_CONTENT: [
                r'(?:create|generate|make|write).*(?:post|content|tweet|story)',
                r'(?:social|media).*(?:content|post)',
                r'write.*(?:caption|description)'
            ],
            ProcessingIntent.ANALYZE_DATA: [
                r'(?:analyze|analyze|check|review).*(?:data|analytics|metrics)',
                r'(?:performance|engagement|stats)',
                r'(?:how.*(?:performing|doing))'
            ],
            ProcessingIntent.CONFIGURE_SYSTEM: [
                r'(?:configure|setup|set up|install)',
                r'(?:config|configuration|settings)',
                r'(?:connect|integrate).*(?:api|service)'
            ],
            ProcessingIntent.DEPLOY_APPLICATION: [
                r'(?:deploy|build|release).*(?:app|application|service)',
                r'(?:ci/cd|pipeline|workflow)',
                r'(?:docker|container|kubernetes)'
            ],
            ProcessingIntent.SCHEDULE_TASK: [
                r'(?:schedule|plan|queue).*(?:post|content|task)',
                r'(?:calendar|timeline|later)',
                r'(?:automate|automation)'
            ]
        }
    
    def classify_intent(self, text: str) -> Tuple[ProcessingIntent, float]:
        """Classify user intent from text"""
        text_lower = text.lower()
        best_intent = ProcessingIntent.UNKNOWN
        best_score = 0.0
        
        for intent, patterns in self.intent_patterns.items():
            score = 0.0
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    score += 1.0
            
            # Normalize score by number of patterns
            normalized_score = score / len(patterns)
            
            if normalized_score > best_score:
                best_score = normalized_score
                best_intent = intent
        
        return best_intent, best_score

# Utility Functions
def standardize_response_format(data: Any, response_type: str = "text") -> Dict[str, Any]:
    """Standardize response format for MCP tools"""
    if response_type == "json":
        content = json.dumps(data, indent=2, default=str)
    else:
        if isinstance(data, dict):
            content = json.dumps(data, indent=2, default=str)
        elif isinstance(data, list):
            content = '\n'.join(str(item) for item in data)
        else:
            content = str(data)
    
    return {
        'content': [
            {
                'type': 'text',
                'text': content
            }
        ]
    }

def extract_structured_data(text: str, schema: Dict[str, Any]) -> Dict[str, Any]:
    """Extract structured data based on a schema"""
    # This would use more sophisticated NLP in a real implementation
    extracted = {}
    
    for field, field_config in schema.items():
        field_type = field_config.get('type', 'string')
        keywords = field_config.get('keywords', [])
        required = field_config.get('required', False)
        
        # Simple keyword-based extraction
        for keyword in keywords:
            if keyword.lower() in text.lower():
                if field_type == 'boolean':
                    extracted[field] = True
                elif field_type == 'array':
                    # Extract comma-separated values after keyword
                    pattern = f"{keyword}[:\s]*([^.!?]*)"
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        values = [v.strip() for v in match.group(1).split(',')]
                        extracted[field] = values
                else:
                    # Extract value after keyword
                    pattern = f"{keyword}[:\s]*([^.!?]*)"
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        extracted[field] = match.group(1).strip()
                break
    
    return extracted

# Example schemas for common use cases
DEPLOYMENT_SCHEMA = {
    'app_name': {
        'type': 'string',
        'keywords': ['app', 'application', 'service', 'project'],
        'required': True
    },
    'language': {
        'type': 'string',
        'keywords': ['python', 'node', 'java', 'go', 'language'],
        'required': True
    },
    'environments': {
        'type': 'array',
        'keywords': ['environments', 'deploy to', 'stages'],
        'required': False
    },
    'database': {
        'type': 'string',
        'keywords': ['database', 'db', 'postgres', 'mysql'],
        'required': False
    }
}

CONTENT_SCHEMA = {
    'platforms': {
        'type': 'array',
        'keywords': ['instagram', 'twitter', 'tiktok', 'platforms'],
        'required': True
    },
    'tone': {
        'type': 'string',
        'keywords': ['professional', 'casual', 'funny', 'tone'],
        'required': False
    },
    'include_image': {
        'type': 'boolean',
        'keywords': ['image', 'photo', 'picture', 'visual'],
        'required': False
    }
}
