# Unified DevOS MVP - Implementation Plan

## 🎯 Vision

**Unified DevOS** - An orchestration-first project management platform that doesn't replace Cursor/VS Code/GitHub, but orchestrates them into a single flow: **Spec → Code → PR → Tests → Deploy → Metrics**.

### Core Philosophy
- **Orchestration, not replacement**: Use best-of-breed tools as-is
- **Unified decision-making**: One view across all tools
- **"Spec → Evidence" automation**: Every decision linked to PR, tests, deploy proof

---

## ✅ Phase 1: MVP Foundation (COMPLETED)

### 1.1 Action Bus ✅
**Location**: `server/services/action_bus.py`

**Features**:
- Event emission and routing
- Action execution with idempotency
- Action/event history tracking
- Handler registration system

**Event Types**:
- `SPEC_CREATED`, `SPEC_APPROVED`
- `PR_CREATED`, `PR_MERGED`, `PR_CHECK_FAILED`
- `DEPLOYMENT_STARTED`, `DEPLOYMENT_COMPLETED`, `DEPLOYMENT_FAILED`
- `TEST_PASSED`, `TEST_FAILED`

**Action Types**:
- `create_spec` - Create specification document
- `create_branch` - Create git branch
- `create_pr` - Create pull request
- `run_check` - Run policy checks

### 1.2 Extended GitHub Integration ✅
**Location**: `server/services/integrations/github_extended.py`

**Endpoints**:
- `list_repos()` - List all repositories
- `get_repo(owner, repo)` - Get repo details
- `list_issues()` - List issues
- `create_issue()` - Create issue
- `list_prs()` - List pull requests
- `create_pr()` - Create PR
- `get_checks()` - Get check runs
- `list_releases()` - List releases
- `create_release()` - Create release
- `list_webhooks()` - List webhooks
- `create_webhook()` - Create webhook
- `get_flow_status()` - **Unified flow view**

### 1.3 Workflow API ✅
**Location**: `server/api/routes/workflow.py`

**Endpoints**:
```
GET  /api/workflow/workitems       - List work items
GET  /api/workflow/flow/:owner/:repo  - Get flow status
GET  /api/workflow/actions         - List actions
POST /api/workflow/actions         - Execute action
GET  /api/workflow/actions/:id     - Get action
GET  /api/workflow/events          - List events
POST /api/workflow/events          - Emit event
GET  /api/workflow/specs           - List specs
POST /api/workflow/specs           - Create spec
```

---

## 🔄 Phase 2: Work Item Graph (IN PROGRESS)

### 2.1 Database Schema
**Entities**:
- `Team`, `Project`
- `Spec`, `WorkItem`
- `PR`, `Check`, `TestSuite`
- `Deployment`, `Incident`
- `Metric`

**Relations**:
- Spec → PR
- PR → Checks
- PR → Tests
- Deploy → Incident
- All → Metrics

### 2.2 State Machine
**Work Item States**:
- Spec: `draft` → `review` → `approved` → `implemented`
- PR: `draft` → `open` → `review` → `approved` → `merged`
- Deployment: `queued` → `building` → `deploying` → `live` / `failed`

---

## ⏳ Phase 3: Automation Paths (PENDING)

### 3.1 Spec-to-PR Automation
```
Input: Approved Spec
→ Create branch (feature/spec-id)
→ Scaffold code structure
→ Generate test skeleton
→ Create PR with spec link
→ Set labels and reviewers
```

### 3.2 PR Guardian
- **Policy checks**: max diff size, forbidden directories
- **Cost limits**: tokens per PR, compute budgets
- **Security checks**: secret scanning
- **Eval gateway**: AI quality gates

### 3.3 Release Automation
```
Input: Release tag
→ Generate semver
→ Create release notes
→ Create changelog
→ Tag release
→ Publish release
→ Sync docs
```

---

## 📊 Phase 4: Views & Dashboards

### 4.1 Flow Board ✅
**Status**: Partially implemented

**View**: Spec → In Progress → PR → Review → Merge → Deployed

**Current**:
- `/api/workflow/flow/:owner/:repo`
- Shows: issues, PRs, checks, releases

### 4.2 Risk & SLA Dashboard
**Metrics**:
- PR lead time
- Flaky test rate
- Rollback rate
- p95 build/deploy time

### 4.3 Cost Guard Dashboard
**Metrics**:
- Tokens per build
- Cost per PR
- Agent compute usage

---

## 🔒 Phase 5: Security & Compliance

### 5.1 Policy Layer (PENDING)
**Location**: `server/api/middleware/policy.py` (exists, needs extension)

**Policies**:
- Max diff size per PR
- Forbidden directories
- Secret guardian
- Compute budgets

### 5.2 Budget Controls
- Per-user token budgets
- Per-team compute budgets
- Per-project cost limits

### 5.3 Audit Trail
- All agent actions signed
- Full traceability
- Compliance reporting

---

## 🧪 Testing & Quality

### Test Coverage
- Unit tests for Action Bus
- Integration tests for GitHub
- E2E tests for automation flows

### Error Handling
- Sentry integration ✅
- Retry logic
- Dead letter queue

---

## 📈 ROI Metrics

### Time Savings
- **20-40%** reduction in dev cycle time
- **2-4 weeks** to MVP
- **<3 months** payback for 3+ active devs

### Quality Improvements
- Proof-linked decisions
- Automated compliance
- Cost awareness

---

## 🚀 Next Steps

1. ✅ Action Bus - DONE
2. ✅ Extended GitHub Integration - DONE
3. ✅ Workflow API - DONE
4. 🔄 Work Item Graph Database - IN PROGRESS
5. ⏳ Policy Middleware Extension - PENDING
6. ⏳ Spec-to-PR Automation - PENDING
7. ⏳ Flow Board UI - PENDING

---

## 📚 API Documentation

**Live**: http://localhost:8000/api/docs

**Key Endpoints**:
- `GET /api/workflow/flow/:owner/:repo` - Unified flow view
- `POST /api/workflow/actions` - Execute automation
- `POST /api/workflow/events` - Emit event
- `GET /api/workflow/actions` - List actions
- `GET /api/workflow/events` - List events

---

## 🔗 Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│                  Unified DevOS                      │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐     │
│  │   UI     │    │ Action   │    │ Work     │     │
│  │ Dashboard│◄──►│   Bus    │◄──►│  Item    │     │
│  └──────────┘    └──────────┘    │  Graph   │     │
│       ▲               ▲           └──────────┘     │
│       │               │                 ▲          │
│  ┌────┴────┐    ┌─────┴─────┐    ┌─────┴────┐     │
│  │ GitHub  │    │  OpenAI   │    │ Policy   │     │
│  │Integration│  │  Client   │    │ Engine   │     │
│  └──────────┘    └──────────┘    └──────────┘     │
│                                                     │
└─────────────────────────────────────────────────────┘
        ▲                    ▲                    ▲
        │                    │                    │
    GitHub API          OpenAI API            Database
```

---

## 🎉 Status: MVP Foundations Complete

**Completed**:
- ✅ Action Bus infrastructure
- ✅ Extended GitHub integration
- ✅ Workflow API endpoints
- ✅ Event/action history
- ✅ Flow status API

**In Progress**:
- 🔄 Work Item Graph database
- 🔄 Frontend dashboard

**Next**:
- ⏳ Policy enforcement
- ⏳ Automation recipes
- ⏳ Cost tracking
- ⏳ Release automation

---

## 📝 License

MIT License - See LICENSE file

