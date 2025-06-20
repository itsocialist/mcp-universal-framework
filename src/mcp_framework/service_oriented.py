# Service-Oriented Architecture Template
# Based on Social MCP Server patterns

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, TypeVar, Generic, Union
import logging
import asyncio
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

# Type definitions
T = TypeVar('T')

class ServiceResponse(Generic[T]):
    """Standardized service response wrapper"""
    def __init__(self, success: bool, data: Optional[T] = None, error: Optional[Dict[str, Any]] = None, metadata: Optional[Dict[str, Any]] = None):
        self.success = success
        self.data = data
        self.error = error
        self.metadata = metadata or {}

@dataclass
class ErrorInfo:
    code: str
    message: str
    timestamp: datetime
    details: Optional[Any] = None

class ServiceError(Exception):
    """Base service error"""
    def __init__(self, code: str, message: str, details: Optional[Any] = None):
        self.code = code
        self.message = message
        self.details = details
        self.timestamp = datetime.utcnow()
        super().__init__(message)

# Base Service Classes
class BaseService(ABC):
    """Base service class with common functionality"""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"service.{name}")
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the service"""
        if self._initialized:
            return
        
        await self._setup()
        self._initialized = True
        self.logger.info(f"{self.name} service initialized")
    
    async def _setup(self) -> None:
        """Service-specific setup logic - default implementation"""
        pass
    
    def _create_error_response(self, code: str, message: str, details: Optional[Any] = None) -> ServiceResponse[None]:
        """Create standardized error response"""
        error = ErrorInfo(code=code, message=message, timestamp=datetime.utcnow(), details=details)
        return ServiceResponse(success=False, error=asdict(error))
    
    def _create_success_response(self, data: T, metadata: Optional[Dict[str, Any]] = None) -> ServiceResponse[T]:
        """Create standardized success response"""
        return ServiceResponse(
            success=True, 
            data=data, 
            metadata={
                **({'requestId': f"{self.name}_{int(datetime.utcnow().timestamp() * 1000)}"} if metadata is None else {}),
                **(metadata or {})
            }
        )

class PlatformService(BaseService):
    """Base class for platform-specific services (Instagram, Twitter, etc.)"""
    
    def __init__(self, platform_name: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(f"{platform_name}_service", config)
        self.platform_name = platform_name
        self.api_client = None
        self.rate_limits = {}
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the platform"""
        pass
    
    @abstractmethod
    async def post_content(self, content: Dict[str, Any]) -> ServiceResponse[Dict[str, Any]]:
        """Post content to the platform"""
        pass
    
    @abstractmethod
    async def get_analytics(self, timeframe: str, metrics: List[str]) -> ServiceResponse[Dict[str, Any]]:
        """Get analytics from the platform"""
        pass
    
    async def _check_rate_limits(self) -> bool:
        """Check if we're within rate limits"""
        # Implementation would check against self.rate_limits
        return True

class ContentGeneratorService(BaseService):
    """Content generation service with AI integration"""
    
    def __init__(self, ai_service, config: Optional[Dict[str, Any]] = None):
        super().__init__("content_generator", config)
        self.ai_service = ai_service
        self.platform_limits = {
            'instagram': {'caption': 2200, 'bio': 150, 'hashtags': 30},
            'twitter': {'tweet': 280, 'bio': 160, 'hashtags': 10},
            'tiktok': {'description': 2200, 'bio': 80, 'hashtags': 100}
        }
    
    async def _setup(self) -> None:
        """Setup content generator"""
        await self.ai_service.initialize()
    
    async def generate_content(self, request: Dict[str, Any]) -> ServiceResponse[Dict[str, Any]]:
        """Generate content based on request"""
        try:
            platform = request.get('platform', 'instagram')
            topic = request.get('topic', '')
            tone = request.get('tone', 'professional')
            
            # Generate base content
            ai_response = await self.ai_service.generate_text(request)
            if not ai_response.success:
                return self._create_error_response(
                    'AI_GENERATION_FAILED',
                    'Failed to generate content',
                    ai_response.error
                )
            
            # Platform-specific optimization
            optimized_content = await self._optimize_for_platform(
                ai_response.data, platform
            )
            
            # Generate variations for A/B testing
            variations = await self._generate_variations(optimized_content, request)
            
            result = {
                'content': optimized_content,
                'variations': variations,
                'platform': platform,
                'metadata': {
                    'topic': topic,
                    'tone': tone,
                    'character_count': len(optimized_content.get('text', '')),
                    'hashtag_count': len(optimized_content.get('hashtags', []))
                }
            }
            
            return self._create_success_response(result)
            
        except Exception as e:
            self.logger.error(f"Content generation failed: {e}")
            return self._create_error_response(
                'CONTENT_GENERATION_ERROR',
                str(e),
                {'request': request}
            )
    
    async def _optimize_for_platform(self, content: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """Optimize content for specific platform"""
        limits = self.platform_limits.get(platform, {})
        optimized = content.copy()
        
        # Apply platform-specific optimizations
        if platform == 'instagram':
            optimized = await self._add_instagram_formatting(optimized)
        elif platform == 'twitter':
            optimized = await self._optimize_for_twitter(optimized)
        elif platform == 'tiktok':
            optimized = await self._add_tiktok_trends(optimized)
        
        return optimized
    
    async def _add_instagram_formatting(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Add Instagram-specific formatting"""
        # Implementation would add line breaks, emojis, etc.
        return content
    
    async def _optimize_for_twitter(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize for Twitter character limits"""
        # Implementation would shorten text, optimize hashtags
        return content
    
    async def _add_tiktok_trends(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Add TikTok-specific trends and formatting"""
        # Implementation would add trendy phrases, calls-to-action
        return content
    
    async def _generate_variations(self, content: Dict[str, Any], request: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate content variations for A/B testing"""
        variations = []
        
        for i in range(2):  # Generate 2 variations
            variation_request = {
                **request,
                'topic': f"Create a variation of: {content.get('text', '')}"
            }
            
            response = await self.ai_service.generate_text(variation_request)
            if response.success:
                variations.append(response.data)
        
        return variations

class AnalyticsService(BaseService):
    """Analytics aggregation service"""
    
    def __init__(self, platform_services: List[PlatformService], config: Optional[Dict[str, Any]] = None):
        super().__init__("analytics", config)
        self.platform_services = {service.platform_name: service for service in platform_services}
    
    async def _setup(self) -> None:
        """Setup analytics service"""
        for service in self.platform_services.values():
            await service.initialize()
    
    async def get_cross_platform_analytics(self, platforms: List[str], timeframe: str, metrics: List[str]) -> ServiceResponse[Dict[str, Any]]:
        """Get analytics across multiple platforms"""
        try:
            results = {}
            
            # Gather analytics from each platform
            tasks = []
            for platform in platforms:
                if platform in self.platform_services:
                    service = self.platform_services[platform]
                    task = service.get_analytics(timeframe, metrics)
                    tasks.append((platform, task))
            
            # Execute in parallel
            for platform, task in tasks:
                try:
                    response = await task
                    if response.success:
                        results[platform] = response.data
                    else:
                        results[platform] = {'error': response.error}
                except Exception as e:
                    results[platform] = {'error': str(e)}
            
            # Aggregate results
            aggregated = await self._aggregate_analytics(results, metrics)
            
            return self._create_success_response({
                'aggregated': aggregated,
                'by_platform': results,
                'timeframe': timeframe,
                'metrics': metrics
            })
            
        except Exception as e:
            self.logger.error(f"Analytics aggregation failed: {e}")
            return self._create_error_response(
                'ANALYTICS_AGGREGATION_ERROR',
                str(e)
            )
    
    async def _aggregate_analytics(self, platform_results: Dict[str, Any], metrics: List[str]) -> Dict[str, Any]:
        """Aggregate analytics across platforms"""
        aggregated = {}
        
        for metric in metrics:
            total = 0
            count = 0
            
            for platform, data in platform_results.items():
                if isinstance(data, dict) and metric in data:
                    total += data[metric]
                    count += 1
            
            aggregated[metric] = {
                'total': total,
                'average': total / count if count > 0 else 0,
                'platforms_contributing': count
            }
        
        return aggregated

class SchedulerService(BaseService):
    """Content scheduling service"""
    
    def __init__(self, platform_services: List[PlatformService], config: Optional[Dict[str, Any]] = None):
        super().__init__("scheduler", config)
        self.platform_services = {service.platform_name: service for service in platform_services}
        self.scheduled_posts = []
    
    async def _setup(self) -> None:
        """Setup scheduler service"""
        for service in self.platform_services.values():
            await service.initialize()
    
    async def schedule_content(self, posts: List[Dict[str, Any]], options: Optional[Dict[str, Any]] = None) -> ServiceResponse[Dict[str, Any]]:
        """Schedule content for future posting"""
        try:
            scheduled_items = []
            
            for post in posts:
                platform = post.get('platform')
                content = post.get('content', {})
                scheduled_time = post.get('scheduled_time')
                
                if not platform or platform not in self.platform_services:
                    continue
                
                scheduled_item = {
                    'id': f"sched_{int(datetime.utcnow().timestamp() * 1000)}",
                    'platform': platform,
                    'content': content,
                    'scheduled_time': scheduled_time,
                    'status': 'scheduled',
                    'created_at': datetime.utcnow().isoformat()
                }
                
                self.scheduled_posts.append(scheduled_item)
                scheduled_items.append(scheduled_item)
            
            return self._create_success_response({
                'scheduled_posts': scheduled_items,
                'total_scheduled': len(scheduled_items)
            })
            
        except Exception as e:
            self.logger.error(f"Content scheduling failed: {e}")
            return self._create_error_response(
                'SCHEDULING_ERROR',
                str(e)
            )

# MCP Server Integration
class ServiceOrientedMCPServer:
    """MCP Server with service-oriented architecture"""
    
    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version
        self.services: Dict[str, BaseService] = {}
        self.logger = logging.getLogger(f"mcp.{name}")
    
    def register_service(self, service: BaseService) -> None:
        """Register a service with the server"""
        self.services[service.name] = service
        self.logger.info(f"Registered service: {service.name}")
    
    async def initialize_services(self) -> None:
        """Initialize all registered services"""
        for service in self.services.values():
            await service.initialize()
    
    def get_service(self, name: str) -> Optional[BaseService]:
        """Get a service by name"""
        return self.services.get(name)
    
    async def shutdown_services(self) -> None:
        """Shutdown all services"""
        for service in self.services.values():
            if hasattr(service, 'shutdown'):
                await service.shutdown()

# Example Usage Template
"""
# Example: Social Media MCP Server using Service Architecture

from mcp_framework.service_oriented import *

class InstagramService(PlatformService):
    async def _setup(self):
        # Setup Instagram API client
        pass
    
    async def authenticate(self):
        # Instagram authentication
        return True
    
    async def post_content(self, content):
        # Post to Instagram
        return self._create_success_response({'post_id': '123'})
    
    async def get_analytics(self, timeframe, metrics):
        # Get Instagram analytics
        return self._create_success_response({'engagement': 100})

class TwitterService(PlatformService):
    # Similar implementation for Twitter
    pass

# Setup server
server = ServiceOrientedMCPServer("social-media", "1.0.0")

# Register services
instagram = InstagramService("instagram")
twitter = TwitterService("twitter")
content_gen = ContentGeneratorService(ai_service)
analytics = AnalyticsService([instagram, twitter])

server.register_service(instagram)
server.register_service(twitter)
server.register_service(content_gen)
server.register_service(analytics)

# Initialize
await server.initialize_services()

# Use in MCP tool handlers
content_service = server.get_service("content_generator")
response = await content_service.generate_content({
    'platform': 'instagram',
    'topic': 'AI trends',
    'tone': 'professional'
})
"""
