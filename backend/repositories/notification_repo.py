from datetime import datetime

notifications = []
preferences = []
_next_id = 0
_pref_next_id = 0


def _get_next_id():
    global _next_id
    _next_id += 1
    return _next_id


def _get_pref_next_id():
    global _pref_next_id
    _pref_next_id += 1
    return _pref_next_id


def create_notification(data):
    data["id"] = _get_next_id()
    data["is_read"] = False
    data["created_at"] = datetime.now().isoformat()
    notifications.append(data)
    return data


def get_notifications_by_user(user_id):
    results = [n for n in notifications if n["user_id"] == user_id]
    return sorted(results, key=lambda x: x["created_at"], reverse=True)


def get_unread_count(user_id):
    return sum(1 for n in notifications
               if n["user_id"] == user_id and not n["is_read"])


def mark_as_read(notification_id):
    for n in notifications:
        if n["id"] == notification_id:
            n["is_read"] = True
            return n
    return None


def get_preference(user_id, notification_type):
    for p in preferences:
        if p["user_id"] == user_id and p["notification_type"] == notification_type:
            return p
    return None


def get_preferences_by_user(user_id):
    return [p for p in preferences if p["user_id"] == user_id]


def upsert_preference(user_id, notification_type, enabled, channel):
    for p in preferences:
        if p["user_id"] == user_id and p["notification_type"] == notification_type:
            p["enabled"] = enabled
            p["channel"] = channel
            return p
    pref = {
        "id": _get_pref_next_id(),
        "user_id": user_id,
        "notification_type": notification_type,
        "enabled": enabled,
        "channel": channel,
    }
    preferences.append(pref)
    return pref


def clear():
    global _next_id, _pref_next_id
    notifications.clear()
    preferences.clear()
    _next_id = 0
    _pref_next_id = 0
