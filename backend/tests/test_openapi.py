"""The emitted contract: version, operation count, tags, and no default ids.

These assertions are read against `openapi.json` **on disk**, not against a schema
generated in the test, because the file is what the frontend generates its client from.
A test that regenerated the schema would pass while the committed file was stale.
"""

import json
import re
from pathlib import Path

import pytest

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "openapi.json"

#: The twelve operations the backend serves. Named here so that a route added or removed
#: without thought fails against a list somebody wrote, rather than against a count.
EXPECTED_OPERATIONS = {
    "listSymbols",
    "listQuotes",
    "listCandles",
    "getPortfolio",
    "getMovers",
    "listMacroDrivers",
    "listScenarios",
    "getActiveScenario",
    "activateScenario",
    "deactivateScenario",
    "getPortfolioImpact",
    "getSymbolImpact",
}

#: FastAPI's default operation id: `<name>_<path>_<method>`. The shape the generator
#: would otherwise turn into a TypeScript method name.
DEFAULT_ID = re.compile(r"^[a-z_]+_[a-z_]*_(get|post|put|delete|patch)$")


def report(capsys, message: str) -> None:
    with capsys.disabled():
        print(f"\n    {message}")


@pytest.fixture(scope="module")
def schema() -> dict:
    assert SCHEMA_PATH.exists(), (
        f"{SCHEMA_PATH.name} is not on disk; run scripts/emit_openapi.py"
    )
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def operations(schema: dict) -> dict[str, dict]:
    return {
        operation["operationId"]: operation
        for path in schema["paths"].values()
        for operation in path.values()
    }


def test_the_schema_version_is_pinned(schema) -> None:
    """3.0.2 unconditionally — the generator may reject 3.1."""
    assert schema["openapi"] == "3.0.2"


def test_all_twelve_operations_are_present(schema, capsys) -> None:
    found = set(operations(schema))
    assert found == EXPECTED_OPERATIONS, (
        f"missing {sorted(EXPECTED_OPERATIONS - found)}, "
        f"unexpected {sorted(found - EXPECTED_OPERATIONS)}"
    )
    report(capsys, f"{len(found)} operations: {sorted(found)}")


def test_every_operation_carries_at_least_one_tag(schema) -> None:
    for name, operation in operations(schema).items():
        assert operation.get("tags"), f"{name} carries no tag"


def test_no_operation_id_matches_the_fastapi_default_form(schema, capsys) -> None:
    """`get_quotes_quotes_get` and its kind would reach the client as method names."""
    offenders = [name for name in operations(schema) if DEFAULT_ID.match(name)]
    assert not offenders, f"default-form ids: {offenders}"
    report(capsys, "no operation id matches <name>_<path>_<method>")


def test_every_operation_declares_a_response_model(schema) -> None:
    """A route without one emits an untyped body and the client loses its types."""
    for name, operation in operations(schema).items():
        content = operation["responses"]["200"]["content"]["application/json"]
        assert "schema" in content, f"{name} has no response schema"
