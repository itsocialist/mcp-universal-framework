#!/bin/bash
# Docker Installation Test for MCP Universal Framework
# Tests installation from GitHub repository

echo "🐳 MCP Universal Framework - Docker Installation Test"
echo "=================================================="

# Test 1: Install from GitHub repository  
echo "📦 Test 1: Installing from GitHub repository..."

docker run --rm -v "$(pwd)":/workspace -w /workspace python:3.9-slim bash -c "
set -e
echo '🔧 Setting up environment...'
apt-get update -q
apt-get install -y git -q

echo '🐍 Python environment:'
python --version
pip --version

echo '📥 Installing from GitHub...'
pip install git+https://github.com/itsocialist/mcp-universal-framework.git

echo '🧪 Testing framework functionality...'
python -c 'from mcp_framework.templates.typescript_service import TypeScriptServiceTemplate; print(\"✅ TypeScript templates imported\")'
python -c 'from mcp_framework.nlp_utils import ContentRequestProcessor; print(\"✅ NLP utilities imported\")'
python -c 'from mcp_framework.service_oriented import BaseService; print(\"✅ Service architecture imported\")'
python -c 'import mcp_framework; print(f\"✅ Package version: {mcp_framework.__version__}\")'

echo '🎯 Testing TypeScript generation...'
python -c \"
from mcp_framework.templates.typescript_service import TypeScriptServiceTemplate
template = TypeScriptServiceTemplate()
files = template.generate_files({'name': 'test-server', 'domain': 'social'})
print(f'✅ Generated {len(files)} TypeScript files successfully')
assert len(files) == 9, f'Expected 9 files, got {len(files)}'
print('✅ TypeScript generation test PASSED')
\"

echo '🧠 Testing NLP processing...'
python -c \"
from mcp_framework.nlp_utils import ContentRequestProcessor
processor = ContentRequestProcessor()
result = processor.extract_keywords(
    'Create a professional Instagram post about AI trends',
    processor.platform_keywords
)
assert isinstance(result, dict), 'NLP processor should return dict'
print('✅ NLP processing test PASSED')
\"

echo '🏗️ Testing service architecture...'
python -c \"
from mcp_framework.service_oriented import BaseService, AnalyticsService
service = BaseService('test-service', {'key': 'value'})
assert service.name == 'test-service', 'Service name not set correctly'
analytics = AnalyticsService([])
assert analytics.name == 'analytics', 'Analytics service name incorrect'
print('✅ Service architecture test PASSED')
\"

echo '⚙️ Testing configuration...'
python -c \"
from mcp_framework.config import ConfigLoader
config_loader = ConfigLoader()
config_loader.set('test_key', 'test_value')
value = config_loader.get('test_key')
assert value == 'test_value', 'Configuration get/set failed'
print('✅ Configuration test PASSED')
\"

echo ''
echo '🎉 ALL TESTS PASSED! GitHub installation successful!'
echo '✅ Framework is ready for community adoption'
"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Docker test SUCCESSFUL!"
    echo "📦 Package installs correctly from GitHub"
    echo "🧪 All functionality verified in clean environment"
    echo "🚀 Ready for PyPI distribution"
else
    echo ""
    echo "❌ Docker test FAILED!"
    echo "🔧 Issues need to be resolved before PyPI upload"
    exit 1
fi
