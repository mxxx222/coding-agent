# 📋 Merge Guide for Auto-Deploy Feature

## Protected Branch Requirements

### Before Merging to Main/Deploy

All of the following **MUST** pass:

- ✅ **CI Pipeline**: All tests pass
- ✅ **Secret Scanning**: No secrets detected
- ✅ **Security Scan**: No vulnerabilities
- ✅ **Build Check**: All components build successfully
- ✅ **Code Review**: At least 1 approval

## How to Merge

### 1. Create Pull Request

```bash
# Create feature branch
git checkout -b feature/your-feature

# Make changes
# ... do your work ...

# Commit
git add .
git commit -m "feat: your feature"

# Push
git push origin feature/your-feature
```

### 2. Open Pull Request

- Go to GitHub
- Click "New Pull Request"
- Select your branch
- Add description
- Request reviews
- Wait for CI to pass

### 3. CI Requirements

CI will automatically:
- ✅ Run linting
- ✅ Run tests
- ✅ Scan for secrets
- ✅ Check security
- ✅ Verify build

### 4. Code Review

- At least **1 reviewer** must approve
- All comments must be addressed
- CI must pass

### 5. Merge

**Options**:

#### Option A: Merge (Default)
- Preserves complete history
- Creates merge commit
- Good for small features

#### Option B: Squash and Merge (Recommended)
- Clean history
- Single commit
- Better for multiple commits

#### Option C: Rebase and Merge
- Linear history
- No merge commit
- Use sparingly

## Merge Checklist

Before clicking "Merge":

- [ ] CI pipeline passed
- [ ] All tests passing
- [ ] No secret scanning errors
- [ ] Code reviewed and approved
- [ ] Documentation updated
- [ ] Changelog updated (if needed)
- [ ] Environment variables updated (if needed)

## After Merge

### For Auto-Deploy Feature

1. **Verify Environment Variables**
   ```bash
   # Check these are set in production:
   - NOTION_API_KEY
   - VERCEL_TOKEN
   - OPENAI_API_KEY
   - DATABASE_URL
   ```

2. **Test Deployment**
   - Create test Notion page
   - Run automation pipeline
   - Verify Vercel deployment
   - Check logs for errors

3. **Monitor**
   - Watch error logs
   - Check metrics
   - Verify API calls
   - Monitor costs

## Rollback Procedure

If deployment fails:

```bash
# 1. Identify bad commit
git log --oneline

# 2. Revert commit
git revert <commit-sha>

# 3. Push
git push origin main

# 4. Or rollback to previous version
git reset --hard <previous-commit-sha>
git push --force origin main  # ⚠️ Only if necessary!
```

## Emergency Hotfix

For urgent fixes on main:

```bash
# 1. Create hotfix branch
git checkout -b hotfix/critical-fix main

# 2. Fix issue
# ... make changes ...

# 3. Commit
git add .
git commit -m "fix: critical issue"

# 4. Push and merge immediately
git push origin hotfix/critical-fix
# Merge via GitHub (bypass CI if truly critical)
```

**Note**: Hotfix should still go through proper review when possible.

---

## Git Workflow

```
main (protected)
  ↓
feature/auto-notion-vercel  (your branch)
  ↓
  Create PR
  ↓
  CI runs
  ↓
  Code review
  ↓
  Merge to main
  ↓
  Auto-deploy triggers
```

---

**Questions?** Contact the team or check the documentation.

