from __future__ import annotations

import re
from pathlib import Path
from typing import Any


def _strip_comment(line: str) -> str:
    quote = None
    for index, char in enumerate(line):
        if char in "'\"":
            quote = None if quote == char else (char if quote is None else quote)
        elif char == "#" and quote is None:
            return line[:index]
    return line


def _scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return None
    if value.startswith("[") and value.endswith("]"):
        body = value[1:-1].strip()
        return [] if not body else [_scalar(item) for item in body.split(",")]
    if (value[0], value[-1]) in {("'", "'"), ('"', '"')}:
        return bytes(value[1:-1], "utf-8").decode("unicode_escape")
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if lowered in {"null", "~"}:
        return None
    if re.fullmatch(r"[-+]?\d+", value):
        return int(value)
    if re.fullmatch(r"[-+]?(?:\d+\.\d*|\d*\.\d+)", value):
        return float(value)
    return value


def load_yaml(path: str | Path) -> dict[str, Any]:
    """Load the conservative YAML subset used by Harness configuration files."""
    tokens: list[tuple[int, str]] = []
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        clean = _strip_comment(raw).rstrip()
        if clean.strip():
            tokens.append((len(clean) - len(clean.lstrip(" ")), clean.strip()))

    def parse_block(pos: int, indent: int) -> tuple[Any, int]:
        is_list = tokens[pos][1].startswith("- ")
        result: Any = [] if is_list else {}
        while pos < len(tokens):
            current_indent, text = tokens[pos]
            if current_indent < indent:
                break
            if current_indent > indent:
                raise ValueError(f"Unexpected indentation near: {text}")
            if is_list:
                if not text.startswith("- "):
                    break
                item_text = text[2:].strip()
                if ":" in item_text:
                    key, value = item_text.split(":", 1)
                    item = {key.strip(): _scalar(value)}
                    pos += 1
                    if pos < len(tokens) and tokens[pos][0] > indent:
                        extra, pos = parse_block(pos, tokens[pos][0])
                        if not isinstance(extra, dict):
                            raise ValueError(f"Expected mapping after: {item_text}")
                        item.update(extra)
                    result.append(item)
                else:
                    result.append(_scalar(item_text))
                    pos += 1
            else:
                if text.startswith("- ") or ":" not in text:
                    break
                key, value = text.split(":", 1)
                key = key.strip()
                pos += 1
                if value.strip():
                    result[key] = _scalar(value)
                elif pos < len(tokens) and tokens[pos][0] > indent:
                    result[key], pos = parse_block(pos, tokens[pos][0])
                else:
                    result[key] = {}
        return result, pos

    if not tokens:
        return {}
    parsed, end = parse_block(0, tokens[0][0])
    if end != len(tokens) or not isinstance(parsed, dict):
        raise ValueError(f"Could not parse all YAML from {path}")
    return parsed


def load_scenario(path: str | Path) -> dict[str, Any]:
    config = load_yaml(path)
    required = {"scale", "traffic", "course", "payload"}
    missing = required - config.keys()
    if missing:
        raise ValueError(f"scenario.yaml missing sections: {sorted(missing)}")
    return config


def load_schema_map(path: str | Path) -> dict[str, Any]:
    config = load_yaml(path)
    if "tables" not in config or "copy" not in config:
        raise ValueError("schema-map.yaml must contain tables and copy sections")
    return config

