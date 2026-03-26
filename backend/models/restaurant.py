from dataclasses import dataclass


class Restaurant:
    id: int
    name: str
    cuisine_type: str
    address: str | None = None
