logged_in_users: set[int] = set()


def login_session(user_id: int) -> None:
    logged_in_users.add(user_id)


def logout_session(user_id: int) -> None:
    logged_in_users.discard(user_id)


def is_logged_in(user_id: int) -> bool:
    return user_id in logged_in_users


def clear_sessions() -> None:
    logged_in_users.clear()
