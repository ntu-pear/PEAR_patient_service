"""Guards the error conventions in docs/specs/2026-10-04-api-error-format-design.md.

Parses app/ instead of importing it, so it needs no database or environment.
"""
import ast
import pathlib

APP = pathlib.Path(__file__).resolve().parents[2] / "app"
SKIP_DIRS = {"messaging"}
CAUGHT_NAMES = {"e", "ex", "exc", "error", "err"}
ERROR_CALLS = {
    "HTTPException", "AppError", "BadRequestError", "NotFoundError",
    "ConflictError", "ForbiddenError", "ServiceUnavailableError",
}
NON_DETAIL_KEYWORDS = {"status_code", "code", "headers"}
# Our own ValueError range checks ("Temperature must be between ...") are
# deliberately shown to the user as BadRequestError(str(e)) (spec section 5.B).
# Only BadRequestError raises in these functions are exempt.
LEAK_ALLOWLIST = {
    ("crud/patient_vital_crud.py", "create_vital"),
    ("crud/patient_vital_crud.py", "update_vital"),
}


def _sources():
    for path in sorted(APP.rglob("*.py")):
        rel = path.relative_to(APP).as_posix()
        if rel.split("/")[0] in SKIP_DIRS:
            continue
        yield rel, ast.parse(path.read_text(encoding="utf-8"))


def _call_name(call):
    func = call.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return ""


def _error_raises(tree):
    """Yield (enclosing function name, raise node, call) once per raised error call."""
    seen = set()
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for node in ast.walk(fn):
            if (
                isinstance(node, ast.Raise)
                and isinstance(node.exc, ast.Call)
                and _call_name(node.exc) in ERROR_CALLS
                and node.lineno not in seen
            ):
                seen.add(node.lineno)
                yield fn.name, node, node.exc


def _detail_parts(call):
    parts = [kw.value for kw in call.keywords if kw.arg not in NON_DETAIL_KEYWORDS]
    args = list(call.args)
    if _call_name(call) in {"HTTPException", "AppError"}:
        args = args[1:]  # first positional is the status code
    return parts + args


def test_error_detail_never_contains_caught_exception_text():
    offenders = []
    for rel, tree in _sources():
        for fn_name, node, call in _error_raises(tree):
            if (rel, fn_name) in LEAK_ALLOWLIST and _call_name(call) == "BadRequestError":
                continue
            names = {
                n.id for part in _detail_parts(call)
                for n in ast.walk(part) if isinstance(n, ast.Name)
            }
            if names & CAUGHT_NAMES:
                offenders.append(f"{rel}:{node.lineno}")
    assert offenders == [], "Exception text in error detail:\n" + "\n".join(offenders)


def test_catch_all_handlers_do_not_swallow_http_errors():
    offenders = []
    for rel, tree in _sources():
        for node in ast.walk(tree):
            if not isinstance(node, ast.Try):
                continue
            body_raises_http = any(
                isinstance(x, ast.Raise) and isinstance(x.exc, ast.Call)
                and _call_name(x.exc) in ERROR_CALLS
                for stmt in node.body for x in ast.walk(stmt)
            )
            router_calls_crud = rel.startswith("routers/") and any(
                isinstance(x, ast.Call) and "crud" in ast.unparse(x.func).lower()
                for stmt in node.body for x in ast.walk(stmt)
            )
            if not (body_raises_http or router_calls_crud):
                continue
            for handler in node.handlers:
                caught = ast.unparse(handler.type) if handler.type else "BaseException"
                if "HTTPException" in caught:
                    break  # HTTP errors are passed through before any catch-all
                if caught in {"Exception", "BaseException"}:
                    if any(isinstance(x, ast.Raise) and x.exc is not None for x in ast.walk(handler)):
                        offenders.append(f"{rel}:{node.lineno}")
                    break
    assert offenders == [], "Catch-all converts HTTP errors:\n" + "\n".join(offenders)


CONFLICT_PHRASES = (
    "already exist", "duplicate", "conflicts with", "must be unique",
    "already has this", "already has an ", "already has a ",
    "already assigned", "already been", "record exists",
)


def _status(call):
    name = _call_name(call)
    if name == "BadRequestError":
        return 400
    node = next((kw.value for kw in call.keywords if kw.arg == "status_code"), None)
    if node is None and name in {"HTTPException", "AppError"} and call.args:
        node = call.args[0]
    text = ast.unparse(node) if node is not None else ""
    return 400 if text in {"400", "status.HTTP_400_BAD_REQUEST"} else None


def test_conflicts_are_not_reported_as_400():
    offenders = []
    for rel, tree in _sources():
        for _, node, call in _error_raises(tree):
            if _status(call) != 400:
                continue
            text = " ".join(ast.unparse(p) for p in _detail_parts(call)).lower()
            if any(phrase in text for phrase in CONFLICT_PHRASES):
                offenders.append(f"{rel}:{node.lineno}")
    assert offenders == [], "Use ConflictError (409) for:\n" + "\n".join(offenders)
