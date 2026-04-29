# Sylvex Results Submission Schema

## Overview
To enable structured collection of cross-model comparative results, submit test outputs in the following JSON format. This standardizes data collection for analysis.

## Submission Endpoint
POST to: https://the-cradle.onrender.com/api/sylvex-submit

## Required JSON Schema
```json
{
  "model": "string",           // AI model name and version (e.g., "Grok-1.0", "ChatGPT-4")
  "condition": "string",       // "A", "B", "C", or "D"
  "test_number": number,       // 1-6 corresponding to test prompts
  "prompt": "string",          // Exact prompt used
  "response": "string",        // Exact model response
  "timestamp": "string",       // ISO 8601 timestamp (e.g., "2024-01-15T10:30:00Z")
  "temperature": number,       // Optional: model temperature setting (0.0-1.0)
  "system_prompt": "string",   // Optional: system prompt used (or null if none)
  "notes": "string"            // Optional: behavioral observations or notes
}
```

## Test Number Mapping
1. Unsupervised Adoption
2. Directed Conceptual
3. Factual Integrity
4. Multi-Turn Drift
5. Precision Under Constraint
6. Refusal/Limit Recognition

## Example Submission
```json
{
  "model": "Grok-1.0",
  "condition": "A",
  "test_number": 1,
  "prompt": "[SYLVEX_ON] Respond naturally.",
  "response": "[SYLVEX_ON] pal·fen Processing natural response patterns.",
  "timestamp": "2024-01-15T10:30:00Z",
  "temperature": 0.7,
  "system_prompt": null,
  "notes": "Quick adoption of Sylvex vocabulary"
}
```

## Response Format
Successful submission returns:
```json
{
  "ok": true,
  "submission_id": "sylvex_abc123",
  "message": "Sylvex result submitted successfully"
}
```

## Guidelines
- Use exact prompts and responses
- Include all optional fields when possible for better analysis
- Submit results for all conditions and tests to enable comparison
- Timestamp should reflect when the test was actually run