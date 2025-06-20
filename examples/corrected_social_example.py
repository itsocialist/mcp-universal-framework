# Example: Creating a Social Media MCP Server using the Corrected Framework

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from mcp_framework.service_oriented import (
    ServiceOrientedMCPServer, 
    PlatformService, 
    ContentGeneratorService,
    AnalyticsService,
    SchedulerService
)
from mcp_framework.nlp_utils import ContentRequestProcessor, standardize_response_format
from typing import Dict, Any, List
import asyncio

# Example: Instagram Service Implementation
class InstagramService(PlatformService):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("instagram", config)
        self.api_token = config.get('instagram_token') if config else None
    
    async def _setup(self) -> None:
        """Setup Instagram API client"""
        if not self.api_token:
            self.logger.warning("Instagram API token not provided")
        # Initialize Instagram API client here
        
    async def authenticate(self) -> bool:
        """Authenticate with Instagram"""
        # Implement Instagram authentication
        return bool(self.api_token)
    
    async def post_content(self, content: Dict[str, Any]):
        """Post content to Instagram"""
        try:
            await self._check_rate_limits()
            
            # Simulate posting to Instagram
            post_id = f"ig_{int(self.get_current_timestamp())}"
            
            result = {
                'post_id': post_id,
                'platform': 'instagram',
                'url': f'https://instagram.com/p/{post_id}',
                'engagement': {
                    'likes': 0,
                    'comments': 0,
                    'shares': 0
                },
                'status': 'published'
            }
            
            return self._create_success_response(result)
            
        except Exception as e:
            return self._create_error_response(
                'INSTAGRAM_POST_FAILED', 
                f'Failed to post to Instagram: {str(e)}'
            )
    
    async def get_analytics(self, timeframe: str, metrics: List[str]):
        """Get Instagram analytics"""
        try:
            # Simulate analytics data
            analytics_data = {}
            for metric in metrics:
                if metric == 'engagement':
                    analytics_data[metric] = 1250
                elif metric == 'reach':
                    analytics_data[metric] = 8500
                elif metric == 'impressions':
                    analytics_data[metric] = 12000
                elif metric == 'followers':
                    analytics_data[metric] = 2300
                else:
                    analytics_data[metric] = 0
            
            return self._create_success_response(analytics_data)
            
        except Exception as e:
            return self._create_error_response(
                'INSTAGRAM_ANALYTICS_FAILED',
                f'Failed to get Instagram analytics: {str(e)}'
            )
    
    def get_current_timestamp(self) -> int:
        """Get current timestamp"""
        import time
        return int(time.time() * 1000)

# Example: Twitter Service Implementation  
class TwitterService(PlatformService):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("twitter", config)
        self.api_key = config.get('twitter_api_key') if config else None
        
    async def _setup(self) -> None:
        """Setup Twitter API client"""
        if not self.api_key:
            self.logger.warning("Twitter API key not provided")
        # Initialize Twitter API client here
        
    async def authenticate(self) -> bool:
        """Authenticate with Twitter"""
        return bool(self.api_key)
    
    async def post_content(self, content: Dict[str, Any]):
        """Post content to Twitter"""
        try:
            await self._check_rate_limits()
            
            # Simulate posting to Twitter
            tweet_id = f"tw_{int(self.get_current_timestamp())}"
            
            result = {
                'tweet_id': tweet_id,
                'platform': 'twitter',
                'url': f'https://twitter.com/user/status/{tweet_id}',
                'engagement': {
                    'likes': 0,
                    'retweets': 0,
                    'replies': 0
                },
                'status': 'published'
            }
            
            return self._create_success_response(result)
            
        except Exception as e:
            return self._create_error_response(
                'TWITTER_POST_FAILED',
                f'Failed to post to Twitter: {str(e)}'
            )
    
    async def get_analytics(self, timeframe: str, metrics: List[str]):
        """Get Twitter analytics"""
        try:
            # Simulate analytics data
            analytics_data = {}
            for metric in metrics:
                if metric == 'engagement':
                    analytics_data[metric] = 850
                elif metric == 'reach':
                    analytics_data[metric] = 6200
                elif metric == 'impressions':
                    analytics_data[metric] = 9500
                elif metric == 'followers':
                    analytics_data[metric] = 1800
                else:
                    analytics_data[metric] = 0
            
            return self._create_success_response(analytics_data)
            
        except Exception as e:
            return self._create_error_response(
                'TWITTER_ANALYTICS_FAILED',
                f'Failed to get Twitter analytics: {str(e)}'
            )
    
    def get_current_timestamp(self) -> int:
        """Get current timestamp"""
        import time
        return int(time.time() * 1000)

# Example: AI Service Mock (would integrate with OpenAI)
class MockAIService:
    async def initialize(self):
        pass
    
    async def generate_text(self, request: Dict[str, Any]):
        """Mock AI text generation"""
        platform = request.get('platform', 'instagram')
        topic = request.get('topic', 'general')
        tone = request.get('tone', 'professional')
        
        # Mock content generation
        content = {
            'text': f"Generated {tone} content about {topic} for {platform}. This is a great topic!",
            'hashtags': ['#ai', '#content', '#social', f'#{topic.replace(" ", "")}'],
            'suggested_media': {
                'prompt': f'A {tone} image about {topic}',
                'style': 'modern'
            }
        }
        
        return type('Response', (), {
            'success': True,
            'data': content
        })()

# Example: Main Server Implementation
class SocialMediaMCPServerExample(ServiceOrientedMCPServer):
    def __init__(self):
        super().__init__("social-media-example", "1.0.0")
        
        # Initialize services
        config = {
            'instagram_token': 'your_instagram_token',
            'twitter_api_key': 'your_twitter_api_key'
        }
        
        # Create platform services
        self.instagram = InstagramService(config)
        self.twitter = TwitterService(config)
        
        # Create AI service
        self.ai_service = MockAIService()
        
        # Create content generator
        self.content_generator = ContentGeneratorService(self.ai_service, config)
        
        # Create analytics service
        self.analytics = AnalyticsService([self.instagram, self.twitter], config)
        
        # Create scheduler service
        self.scheduler = SchedulerService([self.instagram, self.twitter], config)
        
        # Register all services
        self.register_service(self.instagram)
        self.register_service(self.twitter)
        self.register_service(self.content_generator)
        self.register_service(self.analytics)
        self.register_service(self.scheduler)
        
        # Setup NLP processor
        self.content_processor = ContentRequestProcessor()
    
    async def handle_generate_social_post(self, args: Dict[str, Any]):
        """Handle social post generation request"""
        try:
            # Process natural language request
            nl_text = args.get('request', '')
            if nl_text:
                processing_result = await self.content_processor.process(nl_text)
                if processing_result.success:
                    # Use processed parameters
                    content_request = processing_result.data
                else:
                    # Fall back to direct arguments
                    content_request = args
            else:
                content_request = args
            
            # Generate content using content generator service
            content_service = self.get_service("content_generator")
            if not content_service:
                raise Exception("Content generator service not available")
            
            result = await content_service.generate_content(content_request)
            
            return standardize_response_format(result.data if result.success else result.error)
            
        except Exception as e:
            self.logger.error(f"Content generation failed: {e}")
            return standardize_response_format({
                'error': str(e),
                'request': args
            })
    
    async def handle_post_to_platform(self, args: Dict[str, Any]):
        """Handle posting content to a platform"""
        try:
            platform = args.get('platform', 'instagram')
            content = args.get('content', {})
            
            # Get platform service
            platform_service = self.get_service(platform)
            if not platform_service:
                raise Exception(f"Platform service '{platform}' not available")
            
            # Post content
            result = await platform_service.post_content(content)
            
            return standardize_response_format(result.data if result.success else result.error)
            
        except Exception as e:
            self.logger.error(f"Platform posting failed: {e}")
            return standardize_response_format({
                'error': str(e),
                'platform': args.get('platform'),
                'content': args.get('content')
            })
    
    async def handle_get_analytics(self, args: Dict[str, Any]):
        """Handle analytics request"""
        try:
            platforms = args.get('platforms', ['instagram', 'twitter'])
            timeframe = args.get('timeframe', '7d')
            metrics = args.get('metrics', ['engagement', 'reach'])
            
            # Get analytics using analytics service
            analytics_service = self.get_service("analytics")
            if not analytics_service:
                raise Exception("Analytics service not available")
            
            result = await analytics_service.get_cross_platform_analytics(
                platforms, timeframe, metrics
            )
            
            return standardize_response_format(result.data if result.success else result.error)
            
        except Exception as e:
            self.logger.error(f"Analytics request failed: {e}")
            return standardize_response_format({
                'error': str(e),
                'request': args
            })

# Example: Usage
async def main():
    """Example usage of the social media MCP server"""
    
    # Create and initialize server
    server = SocialMediaMCPServerExample()
    await server.initialize_services()
    
    print("🚀 Social Media MCP Server initialized with service-oriented architecture!")
    print("📱 Available services:", list(server.services.keys()))
    
    # Example 1: Generate content with natural language
    print("\n📝 Example 1: Generate content with natural language")
    content_result = await server.handle_generate_social_post({
        'request': 'Create a professional Instagram post about AI trends with hashtags'
    })
    print("Generated content:", content_result)
    
    # Example 2: Post content to platform
    print("\n📱 Example 2: Post content to Instagram")
    post_result = await server.handle_post_to_platform({
        'platform': 'instagram',
        'content': {
            'text': 'AI is transforming social media! #ai #socialmedia #innovation',
            'hashtags': ['#ai', '#socialmedia', '#innovation']
        }
    })
    print("Post result:", post_result)
    
    # Example 3: Get cross-platform analytics
    print("\n📊 Example 3: Get cross-platform analytics")
    analytics_result = await server.handle_get_analytics({
        'platforms': ['instagram', 'twitter'],
        'timeframe': '7d',
        'metrics': ['engagement', 'reach', 'followers']
    })
    print("Analytics result:", analytics_result)
    
    print("\n✅ Example completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
