from __future__ import annotations

import csv
from pathlib import Path


def ensure_csv_file(path: Path, headers: list[str]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.stat().st_size == 0:
        with path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=headers)
            writer.writeheader()
    return path


def read_rows(path: Path, headers: list[str]) -> list[dict[str, str]]:
    ensure_csv_file(path, headers)
    with path.open(newline="", encoding="utf-8") as csv_file:
        return list(csv.DictReader(csv_file))


def append_row(path: Path, headers: list[str], row: dict[str, str]) -> None:
    ensure_csv_file(path, headers)
    with path.open("a", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writerow(row)


def next_int_id(rows: list[dict[str, str]], id_field: str = "id") -> int:
    return max((int(row[id_field]) for row in rows), default=0) + 1
