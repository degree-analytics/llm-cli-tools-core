# 📦 DEPLOYMENT WORKFLOW RULES

**CRITICAL**: Different types of changes follow different deployment paths:

## Code Changes (apps/, scripts/, packages/):
1. **ALWAYS use GT workflow** → Create branch → PR to dev → Test → PR to main
2. **NEVER deploy code directly** to production without PR review
3. **Workflow**:
   ```bash
   gt create --all -m "fix: description"  # Create branch
   gt submit                              # Create PR to dev
   # After dev testing and approval
   gt checkout main && gt sync            # Switch to main
   gt create --all -m "merge: dev to main" # Create merge branch
   gt submit                              # Create PR to main
   ```

## Infrastructure Changes (sam/, CloudFormation):
1. **Dev environment**: Can use `just aws_deploy_* dev` directly
2. **Prod environment**: 
   - If changing running services → Follow code workflow (PR first)
   - If only infrastructure → Can deploy directly with approval
3. **Examples**:
   - Updating ECS task definition → PR workflow (affects running code)
   - Adding S3 bucket → Direct deploy OK (pure infrastructure)
   - Changing health checks → PR workflow (affects service behavior)

## GT ESSENTIALS (Minimal Reminders)
**Core Rule**: Use `gt` for branches, never `git`
- Before ANY operation: `git status && gt log --stack`

## 🚨 CRITICAL GT RESTACK RULES
**NEVER use rebase during gt restack operations!**
- When `gt restack` shows merge conflicts → Use merge resolution, NOT rebase
- FORBIDDEN: `git rebase` during any GT workflow
- REQUIRED: Let GT handle the merge strategy
- If tempted to rebase → STOP and ask user for guidance
- Rebase breaks GT's internal tracking and causes cascading conflicts