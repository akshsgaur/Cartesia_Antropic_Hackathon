---
name: search-strategy
description: Optimizes ripgrep search patterns and file discovery for RepoBuddy's code exploration. Use when planning searches, finding relevant files, or when users ask "where is X implemented?"
user-invocable: true
allowed-tools: Grep, Read
---

# Code Search Strategy for RepoBuddy

## Search Pattern Generation

### 1. Analyze User Intent
Classify the search request type:
- **Function Location**: "Where is `calculate_total` defined?"
- **Feature Implementation**: "How does user authentication work?"
- **Configuration**: "Where are database settings stored?"
- **Dependencies**: "What uses the payment gateway?"

### 2. Build ripgrep Patterns

#### Function/Method Searches
```bash
# Function definitions (multiple languages)
rg "(def|function|func|class)\s+calculate_total"
rg "calculate_total\s*\("  # Function calls
rg "\.calculate_total"     # Method calls
```

#### Feature-Based Searches
```bash
# Authentication patterns
rg "(auth|login|signin|authenticate)" --type py
rg "(token|jwt|session|cookie)" --type js
rg "(middleware|guard|decorator)" --type ts
```

#### Configuration Searches
```bash
# Config files and settings
rg "(database|db|connection)" --type yaml --type json
rg "(port|host|url|endpoint)" --type env
rg "(config|settings|env)" -i
```

### 3. File Path Prediction

#### Common Directories by Pattern
```
Authentication:     auth/, security/, middleware/, guards/
Database:           models/, db/, database/, migrations/
API:                api/, routes/, endpoints/, controllers/
Configuration:      config/, settings/, .env*, *.config.*
Tests:              tests/, test/, __tests__/, spec/
Utilities:          utils/, helpers/, lib/, common/
Frontend:           client/, frontend/, web/, ui/, components/
Backend:            server/, backend/, api/, services/
```

#### File Naming Conventions
```bash
# Authentication files
auth.py, authentication.py, login.py, signin.py
auth.service.ts, auth.controller.js, auth.middleware.js

# Database files  
database.py, db.py, models.py, schema.py
user.model.ts, database.config.js, migration.sql

# API files
routes.py, api.py, endpoints.py, handlers.py
api.routes.ts, controller.js, endpoints.js
```

### 4. Search Scope Optimization

#### Broad Search (First Pass)
```bash
# Wide net for initial discovery
rg "payment" --type-add 'config:*.{json,yaml,yml,env,ini}' -t config -t py -t js -t ts
rg "user.*profile" -i  # Case insensitive for flexibility
```

#### Narrow Search (Focused)
```bash
# Targeted search after initial discovery
rg "class.*UserProfile" --type py
rg "export.*UserProfile" --type ts
rg "UserProfile.*{" --type js
```

#### Context Lines
```bash
# More context for complex patterns
rg "def.*payment" -A 5 -B 2  # 5 lines after, 2 lines before
rg "payment.*gateway" -C 3   # 3 lines before and after
```

## Search Execution Strategy

### Phase 1: Pattern Generation
1. Extract key terms from user query
2. Generate multiple ripgrep patterns
3. Prioritize by specificity (exact match > partial > fuzzy)

### Phase 2: Multi-Pattern Search
```bash
# Run searches in parallel for efficiency
rg "calculate_total" --type py &
rg "total.*calculation" --type js &
rg "calculate.*total" -i &
wait  # Wait for all to complete
```

### Phase 3: Result Analysis
1. **Deduplicate** overlapping findings
2. **Rank by relevance** (exact matches first)
3. **Group by file** to avoid context switching
4. **Extract context** around matches

### Phase 4: Evidence Collection
```bash
# Get surrounding code for context
rg "calculate_total" -A 10 -B 5 --type py
# Extract function signatures
rg "def.*calculate_total.*\(" --type py
# Find imports and dependencies
rg "import.*calculate_total|from.*calculate_total" --type py
```

## Optimization Guidelines

### Performance Tips
- **Use file type filters**: `--type py`, `--type js`
- **Exclude unnecessary files**: `--glob '!node_modules'`, `--glob '!__pycache__'`
- **Limit results**: `--max-count 20` for initial searches
- **Use word boundaries**: `\bword\b` for exact matches

### Quality Improvements
- **Case sensitivity**: Use `-i` for user-facing terms, exact case for code
- **Multiple patterns**: Combine related concepts with OR logic
- **Context awareness**: Search related files when primary search fails

## Common Search Patterns

### Finding Entry Points
```bash
# Main application files
rg "(main|app|server|index)\.(py|js|ts)" 
rg "if __name__ == '__main__'" --type py
rg "app\.listen|server\.listen" --type js
```

### Finding Database Operations
```bash
# Database queries and connections
rg "(SELECT|INSERT|UPDATE|DELETE)" -i
rg "(db\.|database\.|connection\.)"
rg "(query|execute|fetch)" --type py
```

### Finding API Endpoints
```bash
# Route definitions
rg "@app\.|@router\.|router\." --type py
rg "(get|post|put|delete)\s*\(" --type js
rg "endpoint|route|path" -i
```

## Additional Resources
- For complete ripgrep reference, see [reference.md](reference.md)
- For search examples, see [examples.md](examples.md)
