# Hevy API – Machine-Friendly Reference

## 1. Overview

- Base URL: `https://api.hevyapp.com`
- Version: `v1`
- Protocol: REST
- Format: JSON
- Authentication: API Key (Hevy Pro required)

The Hevy API provides access to:

- Workouts
- Routines
- Exercises
- Folders
- Exercise history

Supports:

- CRUD operations (limited endpoints)
- Pagination
- Filtering (limited support)

---

## 2. Authentication

### Method

API Key via header:

Authorization: api-key:<HEVY_API_KEY>

### Notes

- API key available via Hevy developer settings
- Requires Hevy Pro subscription
- Requests without key → Unauthorized

---

## 3. Core Resources

### 3.1 Workouts

#### GET /v1/workouts

Get a paginated list of workouts

Query Params:

- page (int): page number (default value: 1)
- pageSize (int): number of items on the requested page (max 10)

Response:
{
"page": number,
"page_count": number
"workouts": [Workout],
}

Refer: ## 4. Data Models for Workout datatype

---

#### GET /v1/workouts/{id}

Get single workout details by id

Response:
{
"id": string,
"title": string,
"exercises": [Exercise],
"createdAt": datetime
}

Refer: ## 4. Data Models for Exercise datatype

---

#### POST /v1/workouts

Create workout

Body:
{
"title": string,
"exercises": [...]
}

---

#### PUT /v1/workouts/{id}

Update workout

---

### 3.3 ExerciseTemplates

#### GET /v1/exercise_templates

Paginated List of exercise templates

Response:
{
"page": number,
"page_count": number,
"exercise_templates": [Exercise_Template]

Refer: ## 4. Data Models for Exercise_Template datatype

#### GET /v1/exercise_templates/{exerciseTemplateId}

Get a single exercise template by id

Refer: ## 4. Data Models for Exercise_template datatype.

Can use this to filter out dumbbell exercises. parameter "equipment" is "dumbbell" if workout is a dumbbell workout.

---

## 4. Data Models

### Workout

{
"id": "string",
"title": "string",
"exercises": [Exercise],
"createdAt": "datetime"
}

### Exercise

{
"index": number,
"title": "string",
"exercise_template_id": "string",
"sets": [
{
"weight_kg": number,
"reps": number
}
]
}

### Exercise_Template

{
"id": "string",
"title": "string",
"type": "string",
"equipment": "string",
...
}

---

## 5. Pagination

Standard pagination:

?page=1&pageSize=10

Notes:

- Required for large datasets
- Some endpoints ignore unsupported filters

---

## 6. Rate Limits

- Not explicitly documented
- Best practice:
  - Avoid bulk requests
  - Use pagination
  - Cache results

---

## 8. Errors

Typical responses:

{
"error": "Unauthorized"
}

{
"error": "Invalid request"
}

---

## 9. Best Practices

- Store API key securely (env variable)
- Use pagination for all list endpoints
- Avoid relying on undocumented filters
- Normalize responses before processing
- Retry on transient failures

---

## 11. Capabilities Summary

| Feature           | Supported            |
| ----------------- | -------------------- |
| Read Workouts     | ✅                   |
| Create Workouts   | ✅                   |
| Update/Delete     | ✅                   |
| Exercise History  | ✅                   |
| Search/Filtering  | ⚠️ Limited           |
| Webhooks          | Available externally |
| Real-time updates | ❌                   |

---

## 12. Notes for Coding Agents

- Treat API as **eventually consistent**
- Prefer **ID-based access over search**
- Expect **partial filtering support**
- Design clients with:
  - retry logic
  - pagination abstraction
  - schema validation

## 13. Environment Variables

HEVY_API_KEY=your_api_key

---

## END
