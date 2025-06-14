# Configuration Guide

Campaign Assistant uses a layered YAML configuration system that follows 12-factor app principles.

## Configuration Files

- `default.yaml` - Base configuration with all options documented
- `development.yaml` - Development environment overrides
- `production.yaml` - Production environment overrides  
- `test.yaml` - Test environment overrides

## Environment Detection

The system automatically detects the environment:

1. **Explicit**: Set `CAMPAIGN_ENV=development|production|test`
2. **CI/CD**: Detected from `CI`, `GITHUB_ACTIONS`, etc.
3. **Development**: Detected from `.git`, `pyproject.toml` presence
4. **Default**: Falls back to `production`

## Environment Variables

Sensitive values should be set via environment variables:

```bash
# Copy the example file
cp .env.example .env

# Edit with your values
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

## Configuration Precedence

1. Environment variables (highest priority)
2. Environment-specific YAML file
3. Default YAML file (lowest priority)

## Common Customizations

### Change Data Directory
```yaml
# config/development.yaml
storage:
  files:
    data_dir: "./my_custom_data"
  vector_db:
    path: "./my_custom_data/chroma_db"
```

### Adjust Chunking
```yaml
# config/development.yaml
processing:
  chunking:
    chunk_size: 500
    chunk_overlap: 100
```

### Enable Features
```yaml
# config/development.yaml
features:
  beta:
    web_interface: true
    llm_integration: true
```

## Security Notes

- Never commit API keys to version control
- Use environment variables for secrets
- The `security.api_keys` section loads from environment automatically