import csv
import os
from datetime import datetime
from pathlib import Path

from backend.app import csv_storage

NOTIFICATION_HEADERS = [
    "id", "user_id", "notification_type", "channel",
    "title", "message", "is_read", "order_id", "created_at",
]

PREFERENCE_HEADERS = [
    "id", "user_id", "notification_type", "enabled", "channel",
]


def get_notifications_csv_path() -> Path:
    return Path(os.environ.get("NOTIFICATIONS_CSV_PATH", "data/notifications.csv"))


def get_preferences_csv_path() -> Path:
    return Path(os.environ.get("NOTIFICATION_PREFS_CSV_PATH", "data/notification_preferences.csv"))


def _notif_row_to_dict(row: dict[str, str]) -> dict:
    order_id = row["order_id"]
    return {
        "id": int(row["id"]),
        "user_id": row["user_id"],
        "notification_type": row["notification_type"],
        "channel": row["channel"],
        "title": row["title"],
        "message": row["message"],
        "is_read": row["is_read"] == "True",
        "order_id": order_id if order_id and order_id != "None" and order_id.strip() else None,
        "created_at": row["created_at"],
    }


def _notif_to_row(d: dict) -> dict[str, str]:
    return {
        "id": str(d["id"]),
        "user_id": d["user_id"],
        "notification_type": d["notification_type"],
        "channel": d["channel"],
        "title": d["title"],
        "message": d["message"],
        "is_read": str(d["is_read"]),
        "order_id": str(d["order_id"]) if d["order_id"] is not None else "",
        "created_at": d["created_at"],
    }


def _pref_row_to_dict(row: dict[str, str]) -> dict:
    return {
        "id": int(row["id"]),
        "user_id": row["user_id"],
        "notification_type": row["notification_type"],
        "enabled": row["enabled"] == "True",
        "channel": row["channel"],
    }


def _pref_to_row(d: dict) -> dict[str, str]:
    return {
        "id": str(d["id"]),
        "user_id": d["user_id"],
        "notification_type": d["notification_type"],
        "enabled": str(d["enabled"]),
        "channel": d["channel"],
    }


def _load_notifications() -> list[dict]:
    path = get_notifications_csv_path()
    csv_storage.ensure_csv_file(path, NOTIFICATION_HEADERS)
    return [_notif_row_to_dict(r) for r in csv_storage.read_rows(path, NOTIFICATION_HEADERS)]


def _load_preferences() -> list[dict]:
    path = get_preferences_csv_path()
    csv_storage.ensure_csv_file(path, PREFERENCE_HEADERS)
    return [_pref_row_to_dict(r) for r in csv_storage.read_rows(path, PREFERENCE_HEADERS)]


def _save_notifications(notifications: list[dict]) -> None:
    path = get_notifications_csv_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=NOTIFICATION_HEADERS)
        writer.writeheader()
        for n in notifications:
            writer.writerow(_notif_to_row(n))


def _save_preferences(preferences: list[dict]) -> None:
    path = get_preferences_csv_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=PREFERENCE_HEADERS)
        writer.writeheader()
        for p in preferences:
            writer.writerow(_pref_to_row(p))


def create_notification(data: dict) -> dict:
    path = get_notifications_csv_path()
    rows = csv_storage.read_rows(path, NOTIFICATION_HEADERS)
    data["id"] = csv_storage.next_int_id(rows)
    data["is_read"] = False
    data["created_at"] = datetime.now().isoformat()
    csv_storage.append_row(path, NOTIFICATION_HEADERS, _notif_to_row(data))
    return data


def get_notifications_by_user(user_id: str) -> list[dict]:
    results = [n for n in _load_notifications() if n["user_id"] == user_id]
    return sorted(results, key=lambda x: x["created_at"], reverse=True)


def get_unread_count(user_id: str) -> int:
    return sum(1 for n in _load_notifications()
               if n["user_id"] == user_id and not n["is_read"])


def mark_as_read(notification_id: int) -> dict | None:
    notifications = _load_notifications()
    for n in notifications:
        if n["id"] == notification_id:
            n["is_read"] = True
            _save_notifications(notifications)
            return n
    return None


def get_preference(user_id: str, notification_type: str) -> dict | None:
    for p in _load_preferences():
        if p["user_id"] == user_id and p["notification_type"] == notification_type:
            return p
    return None


def get_preferences_by_user(user_id: str) -> list[dict]:
    return [p for p in _load_preferences() if p["user_id"] == user_id]


def upsert_preference(user_id: str, notification_type: str, enabled: bool, channel: str) -> dict:
    preferences = _load_preferences()
    for p in preferences:
        if p["user_id"] == user_id and p["notification_type"] == notification_type:
            p["enabled"] = enabled
            p["channel"] = channel
            _save_preferences(preferences)
            return p
    pref_path = get_preferences_csv_path()
    rows = csv_storage.read_rows(pref_path, PREFERENCE_HEADERS)
    pref = {
        "id": csv_storage.next_int_id(rows),
        "user_id": user_id,
        "notification_type": notification_type,
        "enabled": enabled,
        "channel": channel,
    }
    csv_storage.append_row(pref_path, PREFERENCE_HEADERS, _pref_to_row(pref))
    return pref


def clear() -> None:
    for path, headers in [
        (get_notifications_csv_path(), NOTIFICATION_HEADERS),
        (get_preferences_csv_path(), PREFERENCE_HEADERS),
    ]:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
