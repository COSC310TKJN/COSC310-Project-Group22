import pytest

from backend.app import database


class FakeSession:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


def test_get_db_yields_session_and_closes_it(monkeypatch):
    fake_session = FakeSession()
    monkeypatch.setattr(database, "SessionLocal", lambda: fake_session)

    db_generator = database.get_db()

    assert next(db_generator) is fake_session

    with pytest.raises(StopIteration):
        next(db_generator)

    assert fake_session.closed is True
