# Standardised API Error Responses — Design

- **Date:** 2026-10-04
- **Task:** 19 — Standardise API error response format across all Patient Service endpoints
- **Status:** Design approved; pending written-spec review
- **Baseline:** `staging` @ `b7a62ec`; unit suite 461 passed / 0 failed. All counts and line numbers below were taken from the code at this commit.

## 1. Goal

Every Patient Service endpoint returns errors in one shape, with correct and consistent HTTP status codes, and never exposes internal exception text or request data in an error response.

Success criteria:

1. Every error response (all routers, used or not) has the shape in §3.
2. Status codes follow the table in §3; duplicates are `409`, schema failures `422`.
3. No `500` response body contains exception text; no validation response echoes the request body.
4. The WebFE needs no changes: `detail` remains a human-readable string.
5. A guard test fails CI if leaks, swallowed errors or `400`-duplicates are reintroduced.

Out of scope: Activity/User services (they can adopt `errors.py` later), the `require_auth` query-parameter bypass (team decision pending), removing unused endpoints, `ref_user_crud.py` and `messaging/`.

## 2. Current state (verified in code)

| Finding | Evidence |
|---|---|
| 334 `HTTPException(...)` constructions; each picks its own status and message | 161 in `routers/`, 149 in `crud/`, 14 in `services/` + `auth/` |
| Only two global handlers; validation returns `400` and echoes the request body | `app/main.py:229-236` (`{"detail": exc.errors(), "body": exc.body}`) |
| Exception text returned to clients | 38 sites — §8.B |
| Catch-alls that convert real `404`/`409` into `500`/`400` | 4 sites — §8.C (e.g. an empty dementia stage list returns `500` "404: No dementia stage list entries found.") |
| Duplicates returned as `400` | 26 sites — §8.D |
| `detail` is a string everywhere except validation errors (list) | `main.py:233` |
| 10 `except HTTPException: raise` pass-throughs rely on the exception type | `routers/`, `crud/` |

Consumers of error responses:

| Consumer | Reads | Impact |
|---|---|---|
| WebFE | `error.response.data.detail` as a string (42 reads); Patient screens branch only on `404` (allergy, dementia, guardian, mobility) | None — `detail` stays a string; `404` behaviour unchanged. Validation-list parsing exists only in User/Activity modals. |
| `PEAR_reconciliation_service` → `/integrity/*` | `raise_for_status()` + logs text | None |
| k8s CronJob → `/cronjobs/highlight-cleanup/run` | curl exit code | None |
| Activity Service `services/patient_service.py:24,40` → `GET /patients/{id}`, `GET /allocation/patient/{id}` | Re-raises with `detail=response.json()` (nests our whole body) | Not broken (nesting already exists); notify Activity owner |
| Messaging consumers / outbox processor | Not HTTP; consumers treat `ValueError` as permanent | None — `ref_user_crud.py`, `messaging/` untouched |

## 3. Error format

```json
{ "detail": "Patient medication not found", "code": "NOT_FOUND", "status": 404 }
```

Validation errors add `errors`:

```json
{ "detail": "Request validation failed", "code": "VALIDATION_ERROR", "status": 422,
  "errors": [ { "field": "body.Dosage", "message": "Field required" } ] }
```

Rules:

1. `detail` is always a string (non-string details are converted with `str()`).
2. Any `5xx` other than `503` returns `"detail": "An unexpected error occurred"`; the original detail and traceback are logged. `503` keeps its (leak-free) message.
3. Validation responses contain field paths and messages only — never input values or the request body.
4. `exc.headers` are preserved (e.g. `WWW-Authenticate`).
5. Unless a raise supplies its own `code`, it is derived from the status:

| Status | `code` |
|---|---|
| 400 | `BAD_REQUEST` |
| 401 | `UNAUTHORIZED` |
| 403 | `FORBIDDEN` |
| 404 | `NOT_FOUND` |
| 405 | `METHOD_NOT_ALLOWED` |
| 409 | `CONFLICT` |
| 422 | `VALIDATION_ERROR` |
| 500 | `INTERNAL_ERROR` |
| 503 | `SERVICE_UNAVAILABLE` |
| other | `ERROR` |

## 4. Components

`app/errors.py` (new):

- `AppError(fastapi.HTTPException)` — `__init__(status_code, detail, code=None, headers=None)`. Subclasses FastAPI's `HTTPException` so the 10 existing `except HTTPException: raise` pass-throughs keep working.
- `BadRequestError` (400), `NotFoundError` (404), `ConflictError` (409), `ForbiddenError` (403), `ServiceUnavailableError` (503).
- `register_error_handlers(app)` registering:
  - `starlette.exceptions.HTTPException` → covers every existing `raise HTTPException(...)`, `AppError`, and Starlette's own unknown-route `404` / wrong-method `405`;
  - `RequestValidationError` → `422` + `errors`;
  - `SQLAlchemyError` → generic `500`, logged;
  - `Exception` → generic `500`, logged with traceback.

`app/main.py`: remove the two existing handlers; call `register_error_handlers(app)`.

Existing raise sites are **not** rewritten unless listed in §8: the handler normalises their shape.

## 5. Changes by site

- **B. Exception text in `detail` (38).**
  - `crud/` sites of the form `except Exception: db.rollback(); raise HTTPException(500, str(e) / f"...{e}")` → keep the rollback, then bare `raise` (the catch-all handler logs and returns the generic `500`). Includes the Cloudinary upload failure (`patient_crud.py:34`).
  - `routers/integrity_router.py` (6) → fixed messages without exception text, plus a log line.
  - `crud/patient_vital_crud.py:138, 239` (`400` from our own `ValueError` range checks, e.g. "Temperature must be between …") → intentional user-facing messages; rewritten as `BadRequestError(str(e))` and allow-listed in the guard test. The two `500` sites in the same file follow the general rule.
  - `routers/patient_assigned_dementia_list_router.py:46` → pass `HTTPException` through, re-raise anything else; remove the stray `print`.
- **C. Swallowing catch-alls (4).** Add `except HTTPException: raise` before `except Exception`.
- **D. Duplicates (26).** `HTTPException(400, ...)` → `ConflictError(...)`; messages unchanged.
- **Validation.** `400` → `422` via the new handler.
- **Unchanged.** The 9 generic `500`s in `outbox_router.py` / `services/user_service.py` (no exception text; masked by rule 2 anyway); empty-collection `404` behaviour (WebFE depends on it); `ref_user_crud.py`; `messaging/`.

## 6. Testing

- `tests/unit/test_errors.py` — minimal FastAPI app + `register_error_handlers` (does not import `app.main`, which creates tables and starts the outbox/consumers on import). Covers: plain `HTTPException` shape; each `AppError` subclass status/code; custom `code` override; `500` with explicit detail masked; unhandled `Exception` and `SQLAlchemyError` masked and logged; `422` with `errors` and no body echo; header preservation; unknown route `404`; wrong method `405`; non-string `detail` coerced.
- `tests/unit/test_error_conventions.py` — AST guard over `app/` that fails on: an `HTTPException`/`AppError` whose `detail` references the caught exception (allow-list: the two vital `ValueError` sites); a duplicate/"already exists" message raised with `400`; a `try` raising `HTTPException` in its body with `except Exception` and no prior `except HTTPException`.
- `tests/integration` — real app: unknown patient id returns `404` in the new shape (proves `main.py` wiring).
- Existing tests: assertions that change must map to a site in §8 (`400`→`409`; `HTTPException(500)` → original exception at CRUD level). Any other failure is a defect in this change.
- Unit tests need `SERVICE_NAME=PATIENT`, `DB_*` and `RABBITMQ_*` env vars set (dummy values suffice).

## 7. Rollout

One PR to `staging` (draft), commits each green:

1. `errors.py` + `register_error_handlers` + `main.py` wiring + `test_errors.py`
2. §8.B exception-text sites
3. §8.C swallowing catch-alls
4. §8.D conflicts → `409`
5. Validation `422` + guard test

Staging verification after deploy: add a duplicate dementia stage → message shown, response `409`; open a patient with no allergies → `404` handling unchanged.

Notify the Activity owner about the nested error body in `services/patient_service.py:24,40`.

## 8. Site inventory (generated from code at `b7a62ec`)

### B. Exception text in `detail` (38)

| File | Line | Status |
|---|---|---|
| `app/crud/patient_crud.py` | 34 | 500 |
| `app/crud/patient_crud.py` | 543 | 500 |
| `app/crud/patient_crud.py` | 687 | 500 |
| `app/crud/patient_crud.py` | 813 | 500 |
| `app/crud/patient_dementia_stage_list_crud.py` | 20 | 500 |
| `app/crud/patient_highlight_crud.py` | 357 | 500 |
| `app/crud/patient_medication_crud.py` | 362 | 500 |
| `app/crud/patient_medication_crud.py` | 579 | 500 |
| `app/crud/patient_medication_crud.py` | 740 | 500 |
| `app/crud/patient_mobility_list_crud.py` | 26 | 500 |
| `app/crud/patient_mobility_mapping_crud.py` | 137 | 500 |
| `app/crud/patient_personal_preference_crud.py` | 256 | 500 |
| `app/crud/patient_personal_preference_crud.py` | 398 | 500 |
| `app/crud/patient_personal_preference_crud.py` | 477 | 500 |
| `app/crud/patient_personal_preference_list_crud.py` | 141 | 500 |
| `app/crud/patient_personal_preference_list_crud.py` | 238 | 500 |
| `app/crud/patient_personal_preference_list_crud.py` | 292 | 500 |
| `app/crud/patient_prescription_crud.py` | 159 | 500 |
| `app/crud/patient_prescription_crud.py` | 275 | 500 |
| `app/crud/patient_prescription_crud.py` | 392 | 500 |
| `app/crud/patient_prescription_list_crud.py` | 89 | 500 |
| `app/crud/patient_problem_crud.py` | 185 | 500 |
| `app/crud/patient_problem_crud.py` | 320 | 500 |
| `app/crud/patient_problem_crud.py` | 403 | 500 |
| `app/crud/patient_problem_list_crud.py` | 92 | 500 |
| `app/crud/patient_problem_list_crud.py` | 166 | 500 |
| `app/crud/patient_problem_list_crud.py` | 215 | 500 |
| `app/crud/patient_vital_crud.py` | 138 | 400 |
| `app/crud/patient_vital_crud.py` | 141 | 500 |
| `app/crud/patient_vital_crud.py` | 239 | 400 |
| `app/crud/patient_vital_crud.py` | 245 | 500 |
| `app/routers/integrity_router.py` | 63 | 500 |
| `app/routers/integrity_router.py` | 116 | 500 |
| `app/routers/integrity_router.py` | 166 | 500 |
| `app/routers/integrity_router.py` | 215 | 500 |
| `app/routers/integrity_router.py` | 264 | 500 |
| `app/routers/integrity_router.py` | 290 | 503 |
| `app/routers/patient_assigned_dementia_list_router.py` | 46 | 400 |

### C. Catch-alls that swallow `HTTPException` (4)

| File | Line (`try`) | |
|---|---|---|
| `app/crud/patient_crud.py` | 557 |  |
| `app/crud/patient_dementia_stage_list_crud.py` | 12 |  |
| `app/crud/patient_mobility_list_crud.py` | 20 |  |
| `app/routers/patient_assigned_dementia_list_router.py` | 41 |  |

### D. Duplicate / conflict raised as `400`, becomes `409` (26)

| File | Line | Current status |
|---|---|---|
| `app/crud/patient_allergy_mapping_crud.py` | 304 | 400 |
| `app/crud/patient_assigned_dementia_mapping_crud.py` | 179 | 400 |
| `app/crud/patient_dementia_stage_list_crud.py` | 51 | 400 |
| `app/crud/patient_dementia_stage_list_crud.py` | 116 | 400 |
| `app/crud/patient_guardian_crud.py` | 59 | 400 |
| `app/crud/patient_guardian_crud.py` | 122 | 400 |
| `app/crud/patient_highlight_type_crud.py` | 99 | 400 |
| `app/crud/patient_highlight_type_crud.py` | 164 | 400 |
| `app/crud/patient_list_language_crud.py` | 33 | 400 |
| `app/crud/patient_list_language_crud.py` | 78 | 400 |
| `app/crud/patient_medical_diagnosis_list_crud.py` | 49 | 400 |
| `app/crud/patient_medical_diagnosis_list_crud.py` | 118 | 400 |
| `app/crud/patient_medication_crud.py` | 407 | 400 |
| `app/crud/patient_personal_preference_crud.py` | 327 | 400 |
| `app/crud/patient_personal_preference_list_crud.py` | 97 | 400 |
| `app/crud/patient_personal_preference_list_crud.py` | 191 | 400 |
| `app/crud/patient_photo_list_album_crud.py` | 41 | 400 |
| `app/crud/patient_photo_list_album_crud.py` | 106 | 400 |
| `app/crud/patient_prescription_crud.py` | 80 | 400 |
| `app/crud/patient_prescription_crud.py` | 195 | 400 |
| `app/crud/patient_prescription_list_crud.py` | 49 | 400 |
| `app/crud/patient_prescription_list_crud.py` | 125 | 400 |
| `app/crud/patient_problem_crud.py` | 229 | 400 |
| `app/crud/patient_problem_list_crud.py` | 52 | 400 |
| `app/crud/patient_problem_list_crud.py` | 125 | 400 |
| `app/routers/patient_guardian_router.py` | 96 | 400 |
