# Publishing Guide for python-max-client

## Overview
This document provides instructions for publishing the `python-max-client` library to PyPI and managing releases.

## Prerequisites
1. PyPI account with API token
2. GitHub repository access
3. Local development environment

## Publishing to PyPI

### 1. Build the package
```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# Check the package
twine check dist/*
```

### 2. Upload to PyPI
```bash
# Upload to PyPI (requires API token)
twine upload dist/*

# Or upload to test PyPI first
twine upload --repository testpypi dist/*
```

### 3. Verify installation
```bash
# Install from PyPI
pip install python-max-client

# Test import
python -c "import python_max_client; print('Success!')"
```

## GitHub Releases

### 1. Create a release
1. Go to GitHub repository
2. Click "Releases" → "Create a new release"
3. Choose tag: `v1.0.0`
4. Add release notes
5. Upload distribution files from `dist/`

### 2. Automated releases
The GitHub Actions workflow will automatically:
- Run tests on multiple Python versions
- Build the package
- Upload to PyPI (if on main branch)

## Version Management

### Semantic Versioning
- `MAJOR.MINOR.PATCH`
- `1.0.0` - Initial release
- `1.1.0` - New features
- `1.1.1` - Bug fixes

### Updating version
1. Update version in `pyproject.toml`
2. Update version in `python_max_client/__init__.py`
3. Create git tag: `git tag -a v1.1.0 -m "Release v1.1.0"`
4. Push tag: `git push origin v1.1.0`

## Development Workflow

### Local development
```bash
# Install in development mode
pip install -e .

# Run tests
pytest

# Run linting
flake8 python_max_client
```

### Pre-release testing
```bash
# Install from test PyPI
pip install --index-url https://test.pypi.org/simple/ python-max-client
```

## Troubleshooting

### Common issues
1. **Package already exists**: Update version number
2. **Authentication failed**: Check PyPI API token
3. **Build fails**: Check dependencies and Python version

### Support
- GitHub Issues: https://github.com/huxuxuya/python-max-client/issues
- Email: huxuxuya@gmail.com
