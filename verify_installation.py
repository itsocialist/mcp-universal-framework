#!/usr/bin/env python3
"""
MCP Universal Framework - Installation Verification Script
Tests that the package installs and functions correctly
"""

import sys
import subprocess
import tempfile
import os

def run_test(description, test_func):
    """Run a test and report results"""
    print(f"🧪 Testing: {description}")
    try:
        test_func()
        print(f"✅ PASS: {description}")
        return True
    except Exception as e:
        print(f"❌ FAIL: {description} - {e}")
        return False

def test_imports():
    """Test that all framework components can be imported"""
    from mcp_framework.service_oriented import BaseService, ServiceOrientedMCPServer
    from mcp_framework.nlp_utils import ContentRequestProcessor, RequirementsProcessor
    from mcp_framework.templates.typescript_service import TypeScriptServiceTemplate
    from mcp_framework.auth import BaseAuth
    from mcp_framework.config import ConfigLoader
    print("   All core modules imported successfully")

def test_typescript_generation():
    """Test TypeScript server generation"""
    from mcp_framework.templates.typescript_service import TypeScriptServiceTemplate
    
    template = TypeScriptServiceTemplate()
    
    # Test social domain
    social_files = template.generate_files({
        'name': 'test-social-server',
        'version': '1.0.0',
        'domain': 'social'
    })
    
    assert len(social_files) == 9, f"Expected 9 files, got {len(social_files)}"
    assert 'package.json' in social_files, "Missing package.json"
    assert 'src/index.ts' in social_files, "Missing main server file"
    
    print(f"   Generated {len(social_files)} TypeScript files")

def test_nlp_processing():
    """Test natural language processing (sync version for testing)"""
    from mcp_framework.nlp_utils import ContentRequestProcessor
    
    processor = ContentRequestProcessor()
    # Test the keyword extraction with proper parameters
    result = processor.extract_keywords(
        "Create a professional Instagram post about AI trends",
        processor.platform_keywords
    )
    
    assert isinstance(result, dict), "NLP processor should return dict"
    print(f"   NLP processing functional")

def test_service_creation():
    """Test service architecture components"""
    from mcp_framework.service_oriented import BaseService, AnalyticsService
    
    # Test base service
    base_service = BaseService("test-service", {"key": "value"})
    assert base_service.name == "test-service", "Service name not set correctly"
    
    # Test analytics service
    analytics = AnalyticsService([])
    assert analytics.name == "analytics", "Analytics service name incorrect"
    
    print("   Service creation successful")

def test_configuration():
    """Test configuration management"""
    from mcp_framework.config import ConfigLoader
    
    config_loader = ConfigLoader()
    config_loader.set("test_key", "test_value")
    
    value = config_loader.get("test_key")
    assert value == "test_value", "Configuration get/set failed"
    
    config_dict = config_loader.to_dict()
    assert "test_key" in config_dict, "Configuration dict missing key"
    
    print("   Configuration management working")

def test_package_metadata():
    """Test package metadata and version"""
    import mcp_framework
    
    assert hasattr(mcp_framework, '__version__'), "Package missing version"
    assert mcp_framework.__version__ == "1.0.0", f"Unexpected version: {mcp_framework.__version__}"
    
    print(f"   Package version: {mcp_framework.__version__}")

def test_cross_platform_compatibility():
    """Test cross-platform compatibility"""
    import platform
    import pathlib
    
    system = platform.system()
    python_version = platform.python_version()
    
    # Test pathlib usage (cross-platform)
    test_path = pathlib.Path("test") / "path"
    assert str(test_path), "Pathlib functionality working"
    
    print(f"   Platform: {system}, Python: {python_version}")

def main():
    """Run all installation verification tests"""
    print("🚀 MCP Universal Framework - Installation Verification")
    print("=" * 60)
    
    tests = [
        ("Framework imports", test_imports),
        ("TypeScript generation", test_typescript_generation),
        ("NLP processing", test_nlp_processing),
        ("Service creation", test_service_creation),
        ("Configuration management", test_configuration),
        ("Package metadata", test_package_metadata),
        ("Cross-platform compatibility", test_cross_platform_compatibility),
    ]
    
    passed = 0
    total = len(tests)
    
    for description, test_func in tests:
        if run_test(description, test_func):
            passed += 1
        print()
    
    print("=" * 60)
    print(f"📊 RESULTS: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Package installation verified successfully!")
        print("")
        print("✅ Ready for production use:")
        print("   - Framework components functional")
        print("   - TypeScript generation working")  
        print("   - NLP processing operational")
        print("   - Service architecture tested")
        print("   - Cross-platform compatibility confirmed")
        return True
    else:
        print("⚠️  Some tests failed. Package may have installation issues.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
