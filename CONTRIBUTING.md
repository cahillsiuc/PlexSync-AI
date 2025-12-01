# Contributing to PlexSync AI

Thank you for your interest in contributing to PlexSync AI! 🎉

---

## 🤝 How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/yourusername/PlexSync-AI/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)
   - Error messages or logs

### Suggesting Features

1. Check existing feature requests
2. Create a new issue with:
   - Clear description of the feature
   - Use case and benefits
   - Proposed implementation (if you have ideas)

### Code Contributions

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Make your changes**
   - Follow the code style (see below)
   - Write tests for new features
   - Update documentation

4. **Run tests**
   ```bash
   cd backend
   pytest tests/ -v
   ```

5. **Commit your changes**
   ```bash
   git commit -m "Add amazing feature"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```

7. **Create a Pull Request**
   - Clear title and description
   - Reference related issues
   - Include test results

---

## 📝 Code Style

### Python

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints
- Maximum line length: 120 characters
- Use `black` for formatting
- Use `flake8` for linting

### Formatting

```bash
# Format code
black backend/

# Check formatting
black --check backend/
```

### Linting

```bash
# Run linter
flake8 backend/

# Type checking
mypy backend/
```

---

## 🧪 Testing

### Writing Tests

- Write tests for all new features
- Follow existing test patterns
- Use descriptive test names
- Mock external dependencies

### Test Structure

```python
def test_feature_name():
    """Test description"""
    # Arrange
    # Act
    # Assert
```

### Running Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_models.py -v

# With coverage
pytest tests/ --cov=backend --cov-report=html
```

### Test Coverage

- Aim for 80%+ coverage
- Focus on critical paths
- Test edge cases and error handling

---

## 📚 Documentation

### Code Documentation

- Use docstrings for all functions and classes
- Follow Google-style docstrings
- Include parameter and return type descriptions

Example:
```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief description of function.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    """
```

### Documentation Updates

- Update README.md for user-facing changes
- Update API documentation
- Add examples for new features
- Update CHANGELOG.md

---

## 🔍 Pull Request Process

1. **Ensure tests pass**
   - All existing tests must pass
   - New tests must be included
   - Coverage should not decrease

2. **Code review**
   - Address review comments
   - Make requested changes
   - Keep PR focused and small

3. **CI/CD checks**
   - All CI/CD checks must pass
   - Fix any linting errors
   - Ensure code quality

4. **Merge**
   - Maintainer will review and merge
   - PR will be squashed and merged
   - Commit message should be clear

---

## 🏗️ Project Structure

```
backend/
├── api/          # API endpoints
├── core/         # Core business logic
├── db/           # Database session
├── models/       # Database models
├── services/     # Service layer
└── tests/        # Test suite
```

### Adding New Features

1. **Models** → `backend/models/`
2. **Core Logic** → `backend/core/`
3. **API Endpoints** → `backend/api/`
4. **Services** → `backend/services/`
5. **Tests** → `backend/tests/`

---

## 🐛 Debugging

### Local Development

```bash
# Run with debug logging
LOG_LEVEL=DEBUG python main.py

# Run tests with verbose output
pytest tests/ -v -s
```

### Common Issues

- **Import errors:** Make sure you're in the `backend/` directory
- **Database errors:** Check `.env` configuration
- **Test failures:** Run with `-v` for verbose output

---

## 📋 Checklist

Before submitting a PR:

- [ ] Code follows style guidelines
- [ ] Tests added/updated and passing
- [ ] Documentation updated
- [ ] CHANGELOG.md updated (if applicable)
- [ ] No linting errors
- [ ] All CI/CD checks passing
- [ ] Commit messages are clear

---

## 💡 Tips

- Start small - fix one thing at a time
- Ask questions if unsure
- Be patient with reviews
- Learn from feedback
- Have fun! 🎉

---

## 📞 Getting Help

- **Documentation:** Check README.md and other docs
- **Issues:** Search existing issues
- **Discussions:** Use GitHub Discussions
- **Questions:** Open a question issue

---

Thank you for contributing! 🙏

