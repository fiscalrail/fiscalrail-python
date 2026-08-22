from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from urllib.request import urlopen

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = "https://docs.fiscalrail.com/openapi.yml"
GENERATED = ROOT / "src/fiscalrail/_generated"
METHODS = ("get", "post", "put", "patch", "delete")
BASE_CLASS_MAP = {
    name: "fiscalrail._model.ResponseModel"
    for name in (
        "Account",
        "ApiKey",
        "BalanceTransaction",
        "Customer",
        "Event",
        "EventDestination",
        "Invoice",
        "InvoiceAmendment",
        "InvoicePdf",
        "InvoiceSeries",
        "PaymentInstruction",
        "TaxId",
        "TaxRegime",
    )
}
TYPE_OVERRIDES = {
    "Money": "decimal.Decimal",
    "Decimal": "decimal.Decimal",
    "DecimalInput": "fiscalrail._types.DecimalInput",
}
PARAM_TYPE_OVERRIDES = {
    **TYPE_OVERRIDES,
    "InvoiceLineCreate.taxes": "fiscalrail._types.TaxReferenceList",
}


def generate_models(schema: Path, destination: Path, model_type: str) -> None:
    command = [
        "datamodel-codegen",
        "--input",
        str(schema),
        "--input-file-type",
        "openapi",
        "--output",
        str(destination),
        "--output-model-type",
        model_type,
        "--target-python-version",
        "3.11",
        "--use-standard-collections",
        "--use-union-operator",
        "--use-standard-primitive-types",
        "--use-title-as-name",
        "--output-date-class",
        "date",
        "--output-datetime-class",
        "datetime",
        "--formatters",
        "builtin",
        "--disable-timestamp",
        "--custom-file-header",
        '"""Generated from FiscalRail\'s OpenAPI contract. Do not edit by hand."""',
        "--no-allow-remote-refs",
    ]
    if model_type == "dataclasses.dataclass":
        command.extend(
            [
                "--dataclass-arguments",
                json.dumps({"frozen": True, "slots": True, "kw_only": True}),
                "--base-class",
                "fiscalrail._model.FiscalRailModel",
                "--base-class-map",
                json.dumps(BASE_CLASS_MAP, sort_keys=True),
                "--type-overrides",
                json.dumps(TYPE_OVERRIDES, sort_keys=True),
            ]
        )
    else:
        command.extend(
            [
                "--use-total-false-for-typed-dict",
                "--type-overrides",
                json.dumps(PARAM_TYPE_OVERRIDES, sort_keys=True),
            ]
        )
    subprocess.run(command, check=True)


def ref_name(value: Any) -> str | None:
    if isinstance(value, dict) and isinstance(value.get("$ref"), str):
        return value["$ref"].rsplit("/", 1)[-1]
    return None


def resolve(document: dict[str, Any], value: Any) -> Any:
    if not isinstance(value, dict) or "$ref" not in value:
        return value
    node: Any = document
    for part in value["$ref"].removeprefix("#/").split("/"):
        node = node[part]
    return node


def generate_operations(document: dict[str, Any], destination: Path) -> None:
    operations: list[dict[str, Any]] = []
    seen: set[str] = set()
    for path, path_item in document["paths"].items():
        for method in METHODS:
            operation = path_item.get(method)
            if operation is None:
                continue
            operation_id = operation.get("operationId")
            if not operation_id or operation_id in seen:
                endpoint = f"{method.upper()} {path}"
                raise ValueError(f"Missing or duplicate operationId for {endpoint}")
            seen.add(operation_id)
            request_schema = (
                operation.get("requestBody", {})
                .get("content", {})
                .get("application/json", {})
                .get("schema")
            )
            statuses = tuple(
                int(status)
                for status in operation["responses"]
                if str(status).startswith("2")
            )
            response_model = None
            for status, response in operation["responses"].items():
                if not str(status).startswith("2"):
                    continue
                resolved = resolve(document, response)
                content = resolved.get("content", {}).get("application/json", {})
                response_model = ref_name(content.get("schema"))
                if response_model:
                    break
            operations.append(
                {
                    "operation_id": operation_id,
                    "method": method.upper(),
                    "path": path,
                    "tag": operation.get("tags", [None])[0],
                    "request_model": ref_name(request_schema),
                    "response_model": response_model,
                    "success_statuses": statuses,
                }
            )

    lines = [
        '"""Generated from FiscalRail\'s OpenAPI contract. Do not edit by hand."""',
        "",
        "from dataclasses import dataclass",
        "from typing import Final",
        "",
        f"CONTRACT_VERSION: Final = {document['info']['version']!r}",
        "",
        "",
        "@dataclass(frozen=True, slots=True)",
        "class Operation:",
        "    method: str",
        "    path: str",
        "    tag: str | None",
        "    request_model: str | None",
        "    response_model: str | None",
        "    success_statuses: tuple[int, ...]",
        "",
        "",
        "OPERATIONS: Final[dict[str, Operation]] = {",
    ]
    for operation in operations:
        lines.extend(
            [
                f"    {operation['operation_id']!r}: Operation(",
                f"        method={operation['method']!r},",
                f"        path={operation['path']!r},",
                f"        tag={operation['tag']!r},",
                f"        request_model={operation['request_model']!r},",
                f"        response_model={operation['response_model']!r},",
                f"        success_statuses={operation['success_statuses']!r},",
                "    ),",
            ]
        )
    lines.append("}")
    destination.write_text("\n".join(lines) + "\n")


def generate(schema: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    document = yaml.safe_load(schema.read_text())
    generate_models(schema, destination / "models.py", "dataclasses.dataclass")
    generate_models(schema, destination / "params.py", "typing.TypedDict")
    generate_operations(document, destination / "operations.py")
    generated_files = (
        str(destination / name) for name in ("models.py", "params.py", "operations.py")
    )
    subprocess.run(
        ["ruff", "format", *generated_files],
        check=True,
    )


def check(schema: Path) -> None:
    with tempfile.TemporaryDirectory() as directory:
        candidate = Path(directory)
        generate(schema, candidate)
        changed = [
            name
            for name in ("models.py", "params.py", "operations.py")
            if not (GENERATED / name).exists()
            or (GENERATED / name).read_bytes() != (candidate / name).read_bytes()
        ]
    if changed:
        raise SystemExit(f"Generated contract is stale: {', '.join(changed)}")


@contextmanager
def schema_path(source: str) -> Iterator[Path]:
    parsed = urlparse(source)
    if parsed.scheme:
        if parsed.scheme != "https":
            raise ValueError("Remote OpenAPI schemas must use HTTPS")
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "openapi.yml"
            with urlopen(source) as response:  # noqa: S310
                destination.write_bytes(response.read())
            yield destination
        return

    yield Path(source).resolve()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--schema",
        default=DEFAULT_SCHEMA,
        help="OpenAPI file or HTTPS URL (defaults to FiscalRail's published contract)",
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    with schema_path(args.schema) as schema:
        if args.check:
            check(schema)
        else:
            generate(schema, GENERATED)


if __name__ == "__main__":
    main()
