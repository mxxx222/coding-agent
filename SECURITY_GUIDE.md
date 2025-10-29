# 🔐 Security Guide

## Secret Management

### ⚠️ CRITICAL: Never Commit Secrets

**DO NOT** commit the following to version control:
- API keys (OpenAI, Notion, Vercel)
- Database credentials
- Private keys
- Access tokens
- Passwords

### ✅ Safe Practices

1. **Use Environment Variables**
   ```bash
   # .env (NOT committed)
   NOTION_API_KEY=secret_xxx
   VERCEL_TOKEN=xxx
   OPENAI_API_KEY=sk-xxx
   ```

2. **Use .gitignore**
   ```bash
   # Always add to .gitignore
   .env
   .env.local
   .env.production
   *.key
   secrets/
   ```

3. **Use Pre-commit Hooks**
   - Automatically scans for secrets before commit
   - Blocks commit if secrets detected

## Pre-commit Setup

### Install Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### Configure Git Hooks

```bash
# Setup githooks
chmod +x .githooks/pre-commit
git config core.hooksPath .githooks
```

## BFG Repo-Cleaner

### Remove Secrets from Git History

If you accidentally committed secrets:

```bash
# 1. Clone a fresh copy
git clone --mirror git@github.com:your-org/coding-agent.git

# 2. Download BFG
wget https://repo1.maven.org/maven2/com/madgag/bfg/1.14.0/bfg-1.14.0.jar

# 3. Remove secrets
java -jar bfg-1.14.0.jar --delete-files .env
java -jar bfg-1.14.0.jar --delete-files config.json
java -jar bfg-1.14.0.jar --strip-blobs-bigger-than 100K

# 4. Clean up
cd coding-agent.git
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 5. Force push
git push --force

# 6. Notify team and rotate credentials!
```

### Alternative: filter-branch

```bash
# Remove file from history
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch .env' \
  --prune-empty --tag-name-filter cat -- --all

# Clean up
rm -rf .git/refs/original/
git reflog expire --expire=now --all
git gc --prune=now
```

## Secret Rotation

### If Secrets Were Exposed

1. **Immediate Actions**
   - Remove secrets from history (see BFG above)
   - Revoke and rotate all exposed credentials
   - Scan logs for exposure
   - Notify affected parties

2. **Update Environment Variables**
   ```bash
   # Generate new secrets
   # Update .env files
   # Deploy to all environments
   ```

3. **Update Vault/Secret Manager**
   - Update in HashiCorp Vault
   - Update in Cloud KMS
   - Update in CI/CD secrets

## Security Tools

### 1. detect-secrets

```bash
# Install
pip install detect-secrets

# Scan
detect-secrets scan --all-files . > .secrets.baseline

# Audit
detect-secrets audit .secrets.baseline

# Add to pre-commit
pre-commit install
```

### 2. TruffleHog

```bash
# GitHub Action (already configured)
- uses: trufflesecurity/trufflehog@main
  with:
    path: ./
```

### 3. GitGuardian

```bash
# Install
pip install ggshield

# Scan
ggshield secret scan

# Add to CI/CD
- uses: GitGuardian/ggshield-action@master
```

## Protected Branches

### Configure on GitHub

1. Go to Settings → Branches
2. Add rule for `main` and `deploy`
3. Enable:
   - ✅ Require pull request reviews
   - ✅ Require status checks to pass
   - ✅ Require branches to be up to date
   - ✅ Include administrators

### Required Status Checks

```
✅ Lint & Test
✅ Secret Scanning
✅ Security Scan
✅ Build Check
```

## Best Practices

### Development

- ✅ Always use `.env` files
- ✅ Never commit `.env` files
- ✅ Use pre-commit hooks
- ✅ Scan before pushing
- ✅ Use separate test credentials

### CI/CD

- ✅ Use secrets management (GitHub Secrets)
- ✅ Never log secrets
- ✅ Use masked outputs
- ✅ Rotate regularly
- ✅ Use least privilege

### Production

- ✅ Use vault/KMS
- ✅ Encrypt at rest
- ✅ Encrypt in transit (TLS)
- ✅ Audit logs
- ✅ Regular rotation

## Emergency Response

### If Breach Detected

1. **Immediate**: Revoke credentials
2. **Assess**: Check exposure scope
3. **Notify**: Inform stakeholders
4. **Remediate**: Fix vulnerabilities
5. **Document**: Record incident
6. **Learn**: Update practices

---

**Remember**: Security is everyone's responsibility! 🔒

