# Coding Agent API Documentation

## Overview

The Coding Agent API provides comprehensive endpoints for code analysis, refactoring suggestions, test generation, and integration management. The API is built with FastAPI and follows RESTful principles.

## Base URL

```
Production: https://api.coding-agent.com
Staging: https://staging-api.coding-agent.com
Development: http://localhost:8000
```

## Authentication

All API requests require authentication using JWT tokens or API keys.

### Headers
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### API Key Authentication
```
X-API-Key: <api_key>
```

## Rate Limiting

- **Free Tier**: 100 requests/hour
- **Pro Tier**: 1000 requests/hour
- **Enterprise**: Custom limits

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## Error Handling

All errors follow a consistent format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "code",
      "issue": "Code cannot be empty"
    }
  }
}
```

### HTTP Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `429` - Too Many Requests
- `500` - Internal Server Error

## Endpoints

### Health Check

#### GET /api/health

Check API health and service status.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "database": "connected",
    "vector_store": "connected",
    "llm": "connected"
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Code Analysis

#### POST /api/analyze/code

Analyze code for quality, complexity, and suggestions.

**Request Body:**
```json
{
  "code": "function example() {\n  return 'hello';\n}",
  "language": "javascript",
  "context": "Optional context about the code"
}
```

**Response:**
```json
{
  "analysis": {
    "quality_score": 85.5,
    "complexity": 2,
    "maintainability": "good",
    "performance": "excellent"
  },
  "suggestions": [
    {
      "type": "style",
      "severity": "low",
      "title": "Add JSDoc comment",
      "description": "Consider adding documentation for this function",
      "line": 1
    }
  ],
  "metrics": {
    "lines_of_code": 3,
    "cyclomatic_complexity": 1,
    "cognitive_complexity": 1
  }
}
```

#### POST /api/analyze/refactor

Get AI-powered refactoring suggestions.

**Request Body:**
```json
{
  "code": "function example() {\n  return 'hello';\n}",
  "file_path": "src/example.js",
  "language": "javascript",
  "focus_areas": ["performance", "readability"]
}
```

**Response:**
```json
{
  "suggestions": [
    {
      "id": "refactor_1",
      "type": "performance",
      "severity": "medium",
      "title": "Optimize function",
      "description": "Consider using arrow function for better performance",
      "current_code": "function example() {\n  return 'hello';\n}",
      "suggested_code": "const example = () => 'hello';",
      "reasoning": "Arrow functions are more concise and performant",
      "line_number": 1,
      "confidence_score": 0.85
    }
  ],
  "refactored_code": "const example = () => 'hello';",
  "confidence_score": 0.85
}
```

### Test Generation

#### POST /api/generate/test

Generate tests for code.

**Request Body:**
```json
{
  "code": "function add(a, b) {\n  return a + b;\n}",
  "file_path": "src/math.js",
  "framework": "jest",
  "test_type": "unit",
  "coverage_target": 0.8
}
```

**Response:**
```json
{
  "tests": [
    {
      "name": "test_add_function",
      "description": "Test basic addition functionality",
      "test_code": "describe('add', () => {\n  it('should add two numbers', () => {\n    expect(add(2, 3)).toBe(5);\n  });\n});",
      "test_type": "unit",
      "expected_behavior": "Function should add two numbers correctly",
      "setup_required": false
    }
  ],
  "coverage_estimate": 0.85,
  "framework_used": "jest",
  "test_count": 1
}
```

#### POST /api/generate/coverage

Analyze test coverage.

**Request Body:**
```json
{
  "code": "function add(a, b) {\n  return a + b;\n}",
  "tests": ["describe('add', () => {\n  it('should add two numbers', () => {\n    expect(add(2, 3)).toBe(5);\n  });\n});"]
}
```

**Response:**
```json
{
  "line_coverage": 0.85,
  "function_coverage": 1.0,
  "branch_coverage": 0.75,
  "uncovered_lines": [3, 4],
  "recommendations": [
    "Add tests for edge cases",
    "Test error conditions"
  ]
}
```

### Code Explanation

#### POST /api/explain/code

Get AI explanation of code functionality.

**Request Body:**
```json
{
  "code": "function fibonacci(n) {\n  if (n <= 1) return n;\n  return fibonacci(n - 1) + fibonacci(n - 2);\n}",
  "language": "javascript",
  "detail_level": "high"
}
```

**Response:**
```json
{
  "explanation": {
    "overview": "This function calculates the nth Fibonacci number using recursion",
    "description": "The function implements the Fibonacci sequence where each number is the sum of the two preceding ones",
    "algorithm": "Recursive approach with base cases for n <= 1"
  },
  "components": [
    {
      "name": "fibonacci",
      "type": "function",
      "description": "Main recursive function"
    }
  ],
  "data_flow": "Input n → Base case check → Recursive calls → Return sum",
  "dependencies": [],
  "complexity": "O(2^n) - exponential time complexity"
}
```

### Code Optimization

#### POST /api/optimize/code

Get code optimization suggestions.

**Request Body:**
```json
{
  "code": "function fibonacci(n) {\n  if (n <= 1) return n;\n  return fibonacci(n - 1) + fibonacci(n - 2);\n}",
  "language": "javascript"
}
```

**Response:**
```json
{
  "optimizations": [
    {
      "type": "performance",
      "title": "Use memoization",
      "description": "Cache results to avoid redundant calculations",
      "original_code": "function fibonacci(n) {\n  if (n <= 1) return n;\n  return fibonacci(n - 1) + fibonacci(n - 2);\n}",
      "optimized_code": "const memo = {};\nfunction fibonacci(n) {\n  if (n <= 1) return n;\n  if (memo[n]) return memo[n];\n  return memo[n] = fibonacci(n - 1) + fibonacci(n - 2);\n}",
      "improvement": "Reduces time complexity from O(2^n) to O(n)"
    }
  ],
  "optimized_code": "const memo = {};\nfunction fibonacci(n) {\n  if (n <= 1) return n;\n  if (memo[n]) return memo[n];\n  return memo[n] = fibonacci(n - 1) + fibonacci(n - 2);\n}",
  "performance_gain": "Significant improvement in time complexity"
}
```

### Integrations

#### GET /api/integrations

Get available integrations.

**Response:**
```json
[
  {
    "service": "supabase",
    "enabled": true,
    "configured": true,
    "last_used": "2024-01-01T00:00:00Z"
  },
  {
    "service": "stripe",
    "enabled": false,
    "configured": false,
    "last_used": null
  }
]
```

#### POST /api/integrations/setup

Setup a new integration.

**Request Body:**
```json
{
  "service": "supabase",
  "config": {
    "url": "https://your-project.supabase.co",
    "anon_key": "your-anon-key"
  }
}
```

**Response:**
```json
{
  "success": true,
  "service": "supabase",
  "files_created": [
    "lib/supabase.ts",
    "lib/database.ts"
  ],
  "dependencies": ["@supabase/supabase-js"],
  "config_updated": true,
  "next_steps": [
    "Install dependencies: npm install",
    "Set up environment variables",
    "Test the integration"
  ]
}
```

#### POST /api/integrations/{service}/test

Test an integration connection.

**Response:**
```json
{
  "success": true,
  "message": "Connection successful",
  "details": {
    "response_time": 150,
    "version": "1.0.0"
  }
}
```

### Cost Tracking

#### GET /api/cost/summary

Get cost summary for user.

**Response:**
```json
{
  "total_cost": 25.50,
  "daily_cost": 5.25,
  "monthly_cost": 25.50,
  "remaining_quota": 74.50,
  "usage_breakdown": {
    "code_analysis": 15.00,
    "test_generation": 8.50,
    "refactoring": 2.00
  }
}
```

#### GET /api/cost/history

Get cost history.

**Query Parameters:**
- `start_date` (optional): Start date for history
- `end_date` (optional): End date for history
- `limit` (optional): Number of records to return

**Response:**
```json
{
  "history": [
    {
      "date": "2024-01-01",
      "cost": 5.25,
      "requests": 25,
      "tokens_used": 15000
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 50
}
```

## SDKs and Libraries

### JavaScript/TypeScript
```bash
npm install @coding-agent/sdk
```

```javascript
import { CodingAgent } from '@coding-agent/sdk';

const client = new CodingAgent({
  apiKey: 'your-api-key',
  baseUrl: 'https://api.coding-agent.com'
});

const analysis = await client.analyzeCode({
  code: 'function example() { return "hello"; }',
  language: 'javascript'
});
```

### Python
```bash
pip install coding-agent-sdk
```

```python
from coding_agent import CodingAgent

client = CodingAgent(
    api_key='your-api-key',
    base_url='https://api.coding-agent.com'
)

analysis = client.analyze_code(
    code='def example():\n    return "hello"',
    language='python'
)
```

### Go
```bash
go get github.com/coding-agent/sdk-go
```

```go
package main

import (
    "github.com/coding-agent/sdk-go"
)

func main() {
    client := codingagent.NewClient("your-api-key")
    
    analysis, err := client.AnalyzeCode(codingagent.AnalyzeCodeRequest{
        Code:     "function example() { return 'hello'; }",
        Language: "javascript",
    })
}
```

## Webhooks

### Event Types

- `code.analyzed` - Code analysis completed
- `test.generated` - Test generation completed
- `refactor.suggested` - Refactoring suggestions available
- `integration.setup` - Integration setup completed

### Webhook Payload

```json
{
  "event": "code.analyzed",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "analysis_id": "uuid",
    "user_id": "uuid",
    "project_id": "uuid",
    "results": {
      "quality_score": 85.5,
      "suggestions_count": 3
    }
  }
}
```

### Webhook Configuration

```json
{
  "url": "https://your-app.com/webhooks/coding-agent",
  "events": ["code.analyzed", "test.generated"],
  "secret": "your-webhook-secret"
}
```

## Rate Limits and Quotas

### Free Tier
- 100 requests/hour
- 10,000 tokens/month
- Basic features only

### Pro Tier
- 1,000 requests/hour
- 100,000 tokens/month
- All features included
- Priority support

### Enterprise
- Custom limits
- Dedicated infrastructure
- SLA guarantees
- Custom integrations

## Error Codes

| Code | Description |
|------|-------------|
| `INVALID_API_KEY` | API key is invalid or expired |
| `RATE_LIMIT_EXCEEDED` | Rate limit exceeded |
| `QUOTA_EXCEEDED` | Monthly quota exceeded |
| `INVALID_INPUT` | Request data is invalid |
| `SERVICE_UNAVAILABLE` | Service temporarily unavailable |
| `INTERNAL_ERROR` | Internal server error |

## Support

- **Documentation**: https://docs.coding-agent.com
- **Support Email**: support@coding-agent.com
- **Community**: https://github.com/coding-agent/community
- **Status Page**: https://status.coding-agent.com
