# Contributing to MCP Universal Framework

Thank you for your interest in contributing to the MCP Universal Framework! This project aims to accelerate MCP server development by providing reusable components extracted from real-world implementations.

## Getting Started

### Prerequisites
- Python 3.9 or higher
- Git
- Basic familiarity with MCP (Model Context Protocol)

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/[your-username]/mcp-universal-framework.git
   cd mcp-universal-framework
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Run Tests**
   ```bash
   python test_framework.py
   pytest  # When we add formal tests
   ```

## How to Contribute

### 🐛 Reporting Bugs
- Use the GitHub issue tracker
- Include Python version, OS, and error messages
- Provide minimal reproduction steps
- Check existing issues first

### 💡 Suggesting Features
- Open an issue with the "enhancement" label
- Describe the use case and expected behavior
- Consider if it fits the framework's scope

### 🔧 Code Contributions

#### Areas We Welcome Contributions
1. **New Domain Templates**
   - E-commerce servers
   - Analytics/reporting servers
   - Custom domain patterns

2. **Enhanced NLP Processing**
   - Multi-intent classification
   - Context-aware processing
   - Additional language patterns

3. **CLI Tools**
   - Server generation commands
   - Migration utilities
   - Analysis tools

4. **Documentation**
   - Tutorials and guides
   - API documentation
   - Example projects

5. **Testing**
   - Additional test cases
   - Integration tests
   - Performance benchmarks

#### Pull Request Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Follow existing code style
   - Add tests for new functionality
   - Update documentation as needed

3. **Test Your Changes**
   ```bash
   python test_framework.py  # Should pass 100%
   black src/ examples/     # Format code
   mypy src/               # Type checking
   ```

4. **Commit and Push**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   git push origin feature/your-feature-name
   ```

5. **Open Pull Request**
   - Describe what your PR does
   - Reference any related issues
   - Include testing information

## Code Style Guidelines

### Python Code Style
- Use **Black** for formatting (line length: 100)
- Follow **PEP 8** conventions
- Use **type hints** for all public functions
- Write **docstrings** for classes and methods

### TypeScript Template Style
- Use **consistent indentation** (2 spaces)
- Follow **modern ES6+** patterns
- Include **proper type annotations**
- Use **meaningful variable names**

### Documentation Style
- Use **clear, concise language**
- Include **working examples**
- Follow **Markdown best practices**
- Keep **README updated**

## Framework Architecture

Understanding the framework structure helps with contributions:

```
src/mcp_framework/
├── core/           # Base server classes
├── auth/           # Authentication providers  
├── config/         # Configuration management
├── errors/         # Error handling
├── service_oriented.py  # Service architecture patterns
├── nlp_utils.py    # Natural language processing
└── templates/      # Code generation templates
```

### Key Patterns

1. **Service-Oriented Architecture**
   - All services inherit from `BaseService`
   - Services are registered and managed by lifecycle
   - Clean separation of concerns

2. **Natural Language Processing**
   - Domain-specific processors inherit from `BaseNLProcessor`
   - Consistent result format with confidence scoring
   - Extensible keyword and pattern matching

3. **Template Generation**
   - Templates inherit from `BaseTemplate`
   - Configuration-driven file generation
   - Support for multiple output formats

## Adding New Features

### Adding a New Domain Template

1. **Create Template Class**
   ```python
   class EcommerceDomainTemplate(BaseTemplate):
       def __init__(self):
           super().__init__("ecommerce", "E-commerce MCP server template")
       
       def generate_files(self, config):
           # Implementation
           pass
   ```

2. **Add Domain-Specific Services**
   ```python
   class ProductService(BaseService):
       async def _setup(self):
           # Service setup
           pass
   ```

3. **Update Template Generator**
   - Add domain to TypeScriptServiceTemplate
   - Include new service imports and setup

4. **Add Tests**
   ```python
   def test_ecommerce_template():
       template = EcommerceDomainTemplate()
       files = template.generate_files({"name": "test-store"})
       assert len(files) > 0
   ```

### Adding NLP Processors

1. **Create Processor Class**
   ```python
   class EcommerceRequestProcessor(BaseNLProcessor):
       def __init__(self):
           super().__init__("ecommerce_processor")
           self.product_keywords = {...}
       
       async def process(self, text, context=None):
           # Implementation
           pass
   ```

2. **Add to Framework**
   - Export in `nlp_utils.py`
   - Add to main `__init__.py`
   - Update documentation

## Release Process

### Version Numbering
- Follow [Semantic Versioning](https://semver.org/)
- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

### Release Checklist
1. Update version in `src/mcp_framework/__init__.py`
2. Update `CHANGELOG.md`
3. Run full test suite
4. Create git tag
5. Build and upload to PyPI
6. Create GitHub release

## Community Guidelines

### Code of Conduct
- Be respectful and inclusive
- Focus on constructive feedback
- Help newcomers get started
- Collaborate openly

### Communication Channels
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Pull Requests**: Code review and collaboration

## Questions?

- Check existing [GitHub Issues](https://github.com/mcp-universal-framework/mcp-universal-framework/issues)
- Read the [documentation](https://github.com/mcp-universal-framework/mcp-universal-framework#readme)
- Look at [examples](./examples/) for guidance
- Open a new issue if you're stuck

Thank you for contributing to the MCP Universal Framework! 🚀
