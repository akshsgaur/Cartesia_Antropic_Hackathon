# Search Strategy Reference Guide

## ripgrep Command Reference

### Basic Patterns
```bash
# Exact word match
rg "\bword\b"

# Case insensitive
rg -i "pattern"

# Multiple patterns (OR logic)
rg "pattern1|pattern2|pattern3"

# File type filtering
rg --type py "pattern"
rg --type js "pattern"
rg --type-add 'config:*.{json,yaml,yml}' -t config "pattern"
```

### Context Control
```bash
# Lines before/after
rg "pattern" -A 5 -B 2    # 5 after, 2 before
rg "pattern" -C 3          # 3 before and after

# Maximum results
rg "pattern" --max-count 20

# File limits
rg "pattern" --max-filesize 1M
```

### Exclusion Patterns
```bash
# Exclude directories
rg "pattern" --glob '!node_modules'
rg "pattern" --glob '!__pycache__'
rg "pattern" --glob '!.git'

# Exclude files
rg "pattern" --glob '!*.min.js'
rg "pattern" --glob '!test_*'
```

## Language-Specific Patterns

### Python
```bash
# Function definitions
rg "def\s+\w+\s*\("
rg "class\s+\w+\s*\("

# Import statements
rg "^import\s+"
rg "^from\s+.*import"

# Decorators
rg "@\w+"
```

### JavaScript/TypeScript
```bash
# Function definitions
rg "function\s+\w+\s*\("
rg "const\s+\w+\s*=\s*\("
rg "=>\s*{"

# Import/Export
rg "^import\s+"
rg "^export\s+"

# Class definitions
rg "class\s+\w+"
```

### Go
```bash
# Function definitions
rg "func\s+\w+\s*\("
rg "func\s+\([^)]+\)\s*\w+\s*\("

# Struct definitions
rg "type\s+\w+\s+struct"

# Import statements
rg "^import\s+"
```

## Common Search Scenarios

### Finding Entry Points
```bash
# Main files
rg "(main|app|server|index)\.(py|js|ts|go)"
rg "if __name__ == '__main__'" --type py
rg "app\.listen|server\.listen" --type js
rg "func main" --type go
```

### Finding Database Operations
```bash
# SQL queries
rg "(SELECT|INSERT|UPDATE|DELETE)" -i
rg "FROM\s+\w+"
rg "WHERE\s+"

# Database connections
rg "(db\.|database\.|connection\.)"
rg "(query|execute|fetch)"
rg "(connect|disconnect|close)"
```

### Finding API Endpoints
```bash
# Route definitions
rg "@app\.|@router\.|router\." --type py
rg "(get|post|put|delete|patch)\s*\(" --type js
rg "endpoint|route|path" -i

# HTTP methods
rg "\b(GET|POST|PUT|DELETE|PATCH)\b"
```

### Finding Configuration
```bash
# Config files
rg "(config|settings|env)" -i
rg "(port|host|url|endpoint)"
rg "(database|db|connection)"

# Environment variables
rg "\$\{?\w+\}?"
rg "process\.env\."
rg "os\.getenv"
```

## Search Optimization Tips

### Performance
- Use file type filters (`--type py`, `--type js`)
- Exclude large directories (`--glob '!node_modules'`)
- Limit results for initial searches (`--max-count 20`)
- Use word boundaries for exact matches (`\bword\b`)

### Quality
- Combine related concepts with OR logic (`auth|login|signin`)
- Use case sensitivity appropriately (`-i` for user terms, exact for code)
- Search for related terms when primary search fails
- Consider multiple naming conventions (camelCase, snake_case)

### Strategy
- Start broad, then narrow down
- Use multiple complementary patterns
- Search for imports and dependencies
- Look for test files to understand usage
