# Tests

This directory contains the test suite for the MCP Universal Framework.

## Running Tests

### Quick Test (Framework Validation)
```bash
python test_framework.py
```

### Full Test Suite (When Available)
```bash
pytest
```

## Test Structure

- `test_framework.py` - Comprehensive framework validation (in root directory)
- `test_service_oriented.py` - Service architecture tests
- `test_nlp_utils.py` - Natural language processing tests  
- `test_templates.py` - Template generation tests
- `test_auth.py` - Authentication framework tests
- `test_config.py` - Configuration management tests

## Test Coverage

Current coverage: **100%** for core components

The framework validation test covers:
- ✅ Framework imports
- ✅ TypeScript generation
- ✅ NLP processing
- ✅ Service architecture
- ✅ Configuration management

## Adding Tests

When contributing new features, please add corresponding tests:

```python
import pytest
from mcp_framework.your_module import YourClass

def test_your_feature():
    # Test implementation
    pass

@pytest.mark.asyncio
async def test_async_feature():
    # Async test implementation
    pass
```

See [CONTRIBUTING.md](../CONTRIBUTING.md) for detailed testing guidelines.
