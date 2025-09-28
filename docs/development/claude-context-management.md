---
purpose:
  "Describe the modular CLAUDE.md context hierarchy and how to extend it."
audience: "Developers configuring AI instructions, reviewers"
owner: "Core AI Tools"
review: "Quarterly (Jan, Apr, Jul, Oct)"
status: "Active"
---

# CLAUDE.md Context Management System

## Purpose

Comprehensive guide to the modular AI context management system using @ file
references, nested inheritance, and domain-specific context organization for
enhanced AI development workflows.

## When to Use This

- Setting up AI context for new projects or domains
- Understanding how Claude Code processes context hierarchies
- Implementing modular, reusable instruction sets
- Debugging context loading or inheritance issues
- Maintaining consistent AI behavior across team members

## Prerequisites

- Access to the repository's `CLAUDE.md` files and referenced components.
- Working knowledge of the `@` include syntax and directory structure
  conventions.

**Keywords:** CLAUDE.md, context management, AI instructions, file references,
inheritance

---

## 🌟 System Overview

The Spacewalker project implements a sophisticated AI context management system
that provides:

- **Modular Components**: Reusable instruction sets via @ file references
- **Domain Inheritance**: Nested CLAUDE.md files for specialized contexts
- **Personal Preferences**: User-specific configurations separate from project
  rules
- **Automatic Discovery**: Claude Code's recursive directory traversal

### Architecture Benefits

- **DRY Principle**: Shared components eliminate instruction duplication
- **Maintainability**: Single source of truth for each instruction category
- **Scalability**: Easy addition of new domains and components
- **Team Consistency**: Standardized AI behavior across all developers

---

## 📁 Directory Structure

```text
spacewalker/
├── CLAUDE.md                           # Root context with @ references
├── docs/claude-components/             # Reusable instruction components
│   ├── safety-rules.md                # Production and security safety
│   ├── justfile-workflow.md           # Automation and command patterns
│   ├── verification-standards.md       # Testing and validation requirements
│   └── deployment-gt-workflow.md       # Git workflow and deployment rules
├── apps/admin/CLAUDE.md                # Frontend-specific context
├── apps/backend/CLAUDE.md              # API-specific context
├── apps/mobile/CLAUDE.md               # React Native-specific context
├── sam/CLAUDE.md                       # Infrastructure-specific context
└── ~/.claude/CLAUDE.md                 # Personal preferences (not in git)
```

---

## 🔗 @ File Reference System

### Syntax

```markdown
@docs/claude-components/safety-rules.md
@docs/claude-components/justfile-workflow.md
@docs/claude-components/verification-standards.md
@docs/claude-components/deployment-gt-workflow.md
```

### How It Works

1. **Claude Code Processing**: Automatically expands @ references during context
   loading
2. **Relative Paths**: All paths relative to current CLAUDE.md location
3. **Content Injection**: Referenced content inserted at @ reference location
4. **Recursive Processing**: @ references within referenced files are also
   expanded

### Best Practices

- **Place @ references early**: Load shared rules before specific overrides
- **Use descriptive filenames**: Component purpose should be clear from name
- **Maintain flat structure**: Keep components in single directory for
  simplicity
- **Document dependencies**: Note when components depend on each other

---

## 🏗️ Component Organization

### Current Components

#### `docs/claude-components/safety-rules.md`

**Purpose**: Universal safety patterns for production, git, and AWS operations

**Key Rules**:

- Never run production commands without permission
- Git read-only restrictions (status, diff only)
- AWS resource protection
- Production mode management

**When to Update**: New safety requirements, security policy changes

#### `docs/claude-components/justfile-workflow.md`

**Purpose**: Automation-first development patterns and command discovery

**Key Rules**:

- Justfile-first approach for all operations
- Standard command naming and organization
- Workflow automation principles

**When to Update**: New automation patterns, justfile enhancements

#### `docs/claude-components/verification-standards.md`

**Purpose**: Testing and validation requirements for task completion

**Key Rules**:

- Never claim "done" without verification
- Required verification methods (tests, manual validation)
- TaskMaster integration patterns

**When to Update**: New testing frameworks, validation requirements

#### `docs/claude-components/deployment-gt-workflow.md`

**Purpose**: Git workflow patterns and deployment procedures

**Key Rules**:

- GT CLI usage patterns
- Branch management workflows
- Deployment safety protocols

**When to Update**: Workflow changes, new deployment procedures

### Creating New Components

1. **Identify Reusable Patterns**: Look for instruction sets used across
   multiple domains
2. **Extract to Component**: Create focused, single-purpose instruction file
3. **Update References**: Add @ reference to all relevant CLAUDE.md files
4. **Test Inheritance**: Verify component loads correctly in all contexts
5. **Document Purpose**: Clear description and maintenance guidelines

---

## 🔄 Nested Context Inheritance

### How Inheritance Works

Claude Code automatically discovers CLAUDE.md files by traversing up the
directory tree:

```text
1. Current directory: apps/backend/CLAUDE.md
2. Parent directory: spacewalker/CLAUDE.md
3. Home directory: ~/.claude/CLAUDE.md (if exists)
```

### Context Layering Strategy

**Layer 1: Personal Preferences** (`~/.claude/CLAUDE.md`)

- Individual developer preferences
- Personal shortcuts and patterns
- Development environment customizations

**Layer 2: Project Root** (`CLAUDE.md`)

- Universal project rules and safety
- Shared component references
- Project-wide patterns

**Layer 3: Domain Specific** (`apps/*/CLAUDE.md`, `sam/CLAUDE.md`)

- Technology-specific patterns
- Domain workflows and standards
- Specialized testing and deployment rules

### Inheritance Best Practices

- **Most Specific Wins**: Domain rules override project rules
- **Additive by Default**: Domain contexts add to, don't replace project context
- **Explicit Overrides**: Use clear section headers when overriding parent rules
- **Document Inheritance**: Note which parent rules are being modified

---

## 📱 Domain-Specific Contexts

### Backend Context (`apps/backend/CLAUDE.md`)

**Focus Areas**:

- Python/FastAPI patterns
- Database and migration workflows
- API design standards (no trailing slashes!)
- Authentication and security patterns

**Key Sections**:

- Code standards and type hints
- Database testing with RLS verification
- Async patterns and error handling

### Admin Context (`apps/admin/CLAUDE.md`)

**Focus Areas**:

- React/Next.js development patterns
- Component architecture standards
- UI/UX consistency patterns
- Client-side testing approaches

**Key Sections**:

- TypeScript usage requirements
- Material-UI component consistency
- State management patterns

### Mobile Context (`apps/mobile/CLAUDE.md`)

**Focus Areas**:

- React Native/Expo patterns
- Mobile-specific API integration
- Build and deployment workflows
- Device-specific considerations

**Key Sections**:

- Offline-first architecture
- Performance optimization
- Platform-specific testing

### Infrastructure Context (`sam/CLAUDE.md`)

**Focus Areas**:

- CloudFormation/SAM patterns
- AWS deployment procedures
- Infrastructure security
- Monitoring and observability

**Key Sections**:

- Resource naming conventions
- Environment management
- Deployment order requirements

---

## 👤 Personal Preferences Management

### Setup Location: `~/.claude/CLAUDE.md`

**Note**: ENG-679 originally specified `CLAUDE.local.md`, but Claude Code
documentation shows that personal preferences should use `~/.claude/CLAUDE.md`
instead. This file is automatically discovered by Claude Code's recursive
directory traversal and is naturally excluded from git repositories.

**Personal preferences should include**:

- Individual coding style preferences
- Preferred debugging approaches
- Personal shortcuts and aliases
- Development environment specifics

**Example Personal Preferences**:

```markdown
# Personal Development Preferences

## Debugging Style

- Prefer verbose logging during development
- Use step-through debugging for complex issues
- Include performance timing in development builds

## Code Organization

- Prefer explicit imports over wildcard imports
- Use descriptive variable names over short forms
- Include TODO comments for future improvements

## Development Workflow

- Always run full test suite before committing
- Use git hooks for automated formatting
- Prefer feature branches for all work
```

### What NOT to Include in Personal Preferences

- Project-specific safety rules (belong in project context)
- Team coding standards (belong in domain contexts)
- Deployment procedures (belong in project/domain contexts)
- Security policies (belong in shared components)

---

## 🔧 Maintenance and Updates

### Regular Maintenance Tasks

**Monthly Review**:

- Check for outdated instructions in components
- Verify @ references are still valid
- Update domain contexts for new patterns
- Review personal preferences for relevance

**After Major Changes**:

- Update affected components
- Test context loading in all domains
- Verify inheritance works correctly
- Update documentation examples

### Component Update Workflow

1. **Identify Change Need**: New patterns, deprecated practices, etc.
2. **Assess Impact**: Which domains/files are affected
3. **Update Component**: Make changes to shared component
4. **Test Inheritance**: Verify changes work in all contexts
5. **Update Documentation**: Reflect changes in this guide

### Testing Context Loading

```bash
# Test context in different domains
cd apps/backend && claude --context-check
cd apps/admin && claude --context-check
cd apps/mobile && claude --context-check
cd sam && claude --context-check
```

---

## 🧪 Troubleshooting Context Issues

### Common Issues

#### @ Reference Not Found

- Check file path is relative to CLAUDE.md location
- Verify file exists and is readable
- Ensure no typos in filename

#### Context Not Loading

- Verify CLAUDE.md file is in expected location
- Check file permissions
- Test with minimal CLAUDE.md to isolate issue

#### Inheritance Not Working

- Confirm you're in correct directory
- Check for syntax errors in parent CLAUDE.md files
- Verify Claude Code version supports inheritance

### Debugging Commands

```bash
# Check current context loading
claude --debug-context

# Validate CLAUDE.md syntax
claude --validate-context

# Show inheritance chain
claude --show-inheritance
```

### Validation Checklist

- [ ] All @ references resolve to existing files
- [ ] No circular references between components
- [ ] Domain contexts inherit from project root
- [ ] Personal preferences are separate from project rules
- [ ] Safety rules are present in all contexts

---

## 📋 Implementation Checklist

### Setting Up New Domain Context

- [ ] Create domain-specific CLAUDE.md file
- [ ] Add @ references to relevant shared components
- [ ] Include domain-specific rules and patterns
- [ ] Document inheritance relationship
- [ ] Test context loading and inheritance
- [ ] Add domain to this documentation

### Creating New Shared Component

- [ ] Identify reusable instruction pattern
- [ ] Create focused component file in docs/claude-components/
- [ ] Add @ references to all relevant CLAUDE.md files
- [ ] Test component loading in all contexts
- [ ] Document component purpose and maintenance
- [ ] Update this guide with new component details

### Updating Existing Component

- [ ] Assess impact on all referencing contexts
- [ ] Make changes to component file
- [ ] Test inheritance in all affected domains
- [ ] Update component documentation
- [ ] Verify no breaking changes in behavior

---

## Verification

- Expand the root `CLAUDE.md` with Claude Code to confirm all `@` references
  resolve without errors.
- Spot-check a domain-specific `CLAUDE.md` to ensure inheritance produces the
  expected combined instructions.

## 🔗 Related Documentation

### Context System Architecture

- **Project Structure** – See the Spacewalker documentation for full repository
  layout guidance.
- **Development Tools** – Refer to the Spacewalker development tools guide for
  Claude Code setup and usage.

### Domain-Specific Guides

- **Backend API Development** – Follow the Spacewalker backend API context
  patterns.
- **Admin Development** – See the Spacewalker admin architecture guide for
  frontend context patterns.
- **Mobile Development** – Consult the Spacewalker mobile development patterns
  guidance.

### Workflow Integration

- **TaskMaster Commands** – Internal TaskMaster help (`@tm/help`) for AI-powered
  project management.
- **Testing Guide** – Spacewalker workflow guidance for verification standards
  implementation.

---

**Last Updated:** 2025-07-08 **Status:** Current **Maintainer:** Development
Team
