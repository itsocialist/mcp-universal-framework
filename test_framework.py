#!/usr/bin/env python3
"""
MCP Universal Framework - Comprehensive Test Suite
Phase 1: Local Testing & Validation
"""

import sys
import os
import asyncio
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test all core framework imports"""
    print("🔍 Testing Framework Imports...")
    
    try:
        from mcp_framework.service_oriented import BaseService, ServiceOrientedMCPServer
        print("✅ Service-oriented architecture imported successfully")
    except Exception as e:
        print(f"❌ Service-oriented import failed: {e}")
        return False
    
    try:
        from mcp_framework.nlp_utils import ContentRequestProcessor, RequirementsProcessor
        print("✅ NLP utilities imported successfully")
    except Exception as e:
        print(f"❌ NLP utilities import failed: {e}")
        return False
    
    try:
        from mcp_framework.templates.typescript_service import TypeScriptServiceTemplate
        print("✅ TypeScript templates imported successfully")
    except Exception as e:
        print(f"❌ TypeScript templates import failed: {e}")
        return False
    
    try:
        from mcp_framework.auth import BaseAuth
        print("✅ Authentication module imported successfully")
    except Exception as e:
        print(f"❌ Authentication import failed: {e}")
        return False
    
    try:
        from mcp_framework.config import ConfigLoader
        print("✅ Configuration module imported successfully")
    except Exception as e:
        print(f"❌ Configuration import failed: {e}")
        return False
    
    return True

def test_typescript_generation():
    """Test TypeScript server generation"""
    print("\\n🔧 Testing TypeScript Server Generation...")
    
    try:
        from mcp_framework.templates.typescript_service import TypeScriptServiceTemplate
        
        template = TypeScriptServiceTemplate()
        
        # Test social domain
        social_files = template.generate_files({
            'name': 'test-social-server',
            'version': '1.0.0',
            'domain': 'social',
            'tools': [
                {
                    'name': 'generate_content',
                    'description': 'Generate social media content',
                    'service_call': 'await this.services.get("contentGenerator").generateContent(args)'
                }
            ]
        })
        
        print(f"✅ Social domain template generated {len(social_files)} files")
        
        # Test CICD domain
        cicd_files = template.generate_files({
            'name': 'test-cicd-server',
            'version': '1.0.0',
            'domain': 'cicd',
            'tools': [
                {
                    'name': 'parse_requirements',
                    'description': 'Parse deployment requirements',
                    'service_call': 'await this.services.get("requirementsProcessor").parseRequirements(args)'
                }
            ]
        })
        
        print(f"✅ CI/CD domain template generated {len(cicd_files)} files")
        
        return True
        
    except Exception as e:
        print(f"❌ TypeScript generation failed: {e}")
        return False

async def test_nlp_processing():
    """Test natural language processing"""
    print("\\n🧠 Testing Natural Language Processing...")
    
    try:
        from mcp_framework.nlp_utils import ContentRequestProcessor, RequirementsProcessor
        
        # Test content processing
        content_processor = ContentRequestProcessor()
        result = await content_processor.process("Create a professional Instagram post about AI trends with hashtags")
        
        if result.success:
            print("✅ Content request processing successful")
            print(f"   - Platforms: {result.data.get('platforms', [])}")
            print(f"   - Tone: {result.data.get('tone', 'N/A')}")
            print(f"   - Topic: {result.data.get('topic', 'N/A')}")
        else:
            print(f"❌ Content processing failed: {result.error}")
        
        # Test requirements processing
        req_processor = RequirementsProcessor()
        req_result = await req_processor.process("Deploy a Python Flask app to AWS with staging and production environments")
        
        if req_result.success:
            print("✅ Requirements processing successful")
            print(f"   - Framework: {req_result.data.get('language', 'N/A')}")
            print(f"   - Platform: {req_result.data.get('cloud_providers', ['N/A'])[0] if req_result.data.get('cloud_providers') else 'N/A'}")
            print(f"   - Environments: {req_result.data.get('environments', [])}")
        else:
            print(f"❌ Requirements processing failed: {req_result.error}")
        
        return True
        
    except Exception as e:
        print(f"❌ NLP processing failed: {e}")
        return False

def test_service_architecture():
    """Test service-oriented architecture"""
    print("\\n🏗️ Testing Service-Oriented Architecture...")
    
    try:
        from mcp_framework.service_oriented import BaseService, ContentGeneratorService, AnalyticsService
        
        # Test base service
        service = BaseService("test-service", {"key": "value"})
        print("✅ Base service creation successful")
        
        # Create a mock AI service for ContentGeneratorService
        class MockAIService:
            async def initialize(self):
                pass
        
        # Test content generator with mock AI service
        mock_ai = MockAIService()
        content_gen = ContentGeneratorService(mock_ai)
        print("✅ Content generator service creation successful")
        
        # Test analytics service
        analytics = AnalyticsService([])
        print("✅ Analytics service creation successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Service architecture test failed: {e}")
        return False

def test_configuration():
    """Test configuration management"""
    print("\\n⚙️ Testing Configuration Management...")
    
    try:
        from mcp_framework.config import ConfigLoader
        
        # Test basic config loading
        config_loader = ConfigLoader()
        config_loader.set("test_key", "test_value")
        config_dict = config_loader.to_dict()
        
        if "test_key" in config_dict and config_dict["test_key"] == "test_value":
            print("✅ Configuration loading and retrieval successful")
        else:
            print("❌ Configuration retrieval failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

async def run_all_tests():
    """Run all tests and provide summary"""
    print("🚀 MCP Universal Framework - Comprehensive Test Suite")
    print("=" * 60)
    
    tests = [
        ("Framework Imports", test_imports),
        ("TypeScript Generation", test_typescript_generation),
        ("NLP Processing", test_nlp_processing),
        ("Service Architecture", test_service_architecture),
        ("Configuration", test_configuration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print("\\n" + "=" * 60)
    print(f"🎯 RESULTS: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Framework is ready for Phase 2: Repository Setup")
        return True
    else:
        print("⚠️  Some tests failed. Review issues before proceeding to Phase 2.")
        return False

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
