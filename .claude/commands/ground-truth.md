Verify what documentation claims versus what source code actually implements. Use this when you want to understand the real state of a feature, API, or system component.

## Usage
```
/ground-truth "topic or query"
```

## Examples
```
/ground-truth "CSRF authentication"
/ground-truth "JWT token handling"
/ground-truth "user registration flow"
/ground-truth "database migrations"
```

## Workflow

### 1. **Documentation Index Refresh**
First ensure documentation is up to date:
```bash
just docs status  # Verify search index is current
```

### 2. **Documentation Search**
Use AI-powered search for comprehensive coverage:
```bash
# AI-enhanced search with query expansion
just docs search "$ARGUMENTS" --mode llm --limit 10 --format llm

# Ask specific questions about the topic
just docs ask "How does $ARGUMENTS work in Spacewalker?"
just docs ask "What are the implementation details for $ARGUMENTS?"
```

### 3. **Source Code Analysis**
Use ast-grep (sg) to find actual implementations:
```bash
# Search for relevant code patterns
sg --pattern '$PATTERN' apps/
# Look for function definitions, imports, configurations
sg --pattern 'def $FUNC' apps/ | grep -i "$ARGUMENTS"
sg --pattern 'class $CLASS' apps/ | grep -i "$ARGUMENTS"
sg --pattern 'import $MODULE' apps/ | grep -i "$ARGUMENTS"
```

### 4. **Additional File Analysis**
Based on initial findings, examine specific files:
- Configuration files (settings, environment)
- Implementation files (identified from sg results)
- Test files (to understand expected behavior)
- Migration files (for database-related topics)

Use Read tool to examine key files identified in steps 2-3.

### 5. **Gap Analysis & Report**
Present findings in this structured format:

```
## Ground Truth Analysis: [Topic]

### 📚 Documentation Claims:
[What our docs say should happen]
- Key points from documentation search
- Documented workflows and patterns
- Configuration instructions

### 💻 Source Code Reality:
[What the code actually does]
- Actual implementations found via sg
- Current configuration values
- Real behavior patterns

### 🔍 Additional Context:
[Relevant files examined]
- Configuration files and their values
- Test files and expected behaviors
- Migration history or related changes

### ⚠️ Problems/Gaps Identified:
[Discrepancies between docs and implementation]
- Missing implementations
- Outdated documentation
- Configuration mismatches
- Behavioral differences

### ✅ Summary:
[Overall assessment]
- Is documentation accurate? (Yes/No/Partially)
- Are there implementation issues?
- What needs to be fixed?
- Recommended next steps
```

## Command Principles
- **Justfile First**: Always check `just help` before using direct commands
- **Safety Rules**: Follow verification standards and safety rules
- **Comprehensive**: Don't stop at first finding - get complete picture
- **Evidence-Based**: Use actual code and documentation, not assumptions
- **Problem-Focused**: Identify gaps and issues, not just describe current state

## Integration
- Use findings to inform TaskMaster task creation
- Reference results in Linear tickets or PR descriptions
- Document discovered gaps for future fixes
- Update CLAUDE.md or project docs if major discrepancies found

## Additional Resources
- **[Documentation Search Guide](../docs/workflows/documentation-search-guide.md)** - Comprehensive guide to AI-powered search modes and cost optimization
- **Search help**: `just docs search --help` and `just docs ask --help`
- **Performance monitoring**: All searches tracked in Grafana dashboards
