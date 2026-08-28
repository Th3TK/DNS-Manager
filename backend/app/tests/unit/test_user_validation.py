import pytest
from app.management.users.validation import validate_username
from fastapi import HTTPException


@pytest.mark.parametrize(
    "username",
    [
        "abc",
        "user123",
        "123",
        "user_name",
        "user-name",
        "user@name",
        "user.name",
        "user+name",
        "user:name",
        "user$name",
        "user_123@example.com",
        "a-b_c@d.e+f:g$h",
    ],
)
def test_validate_username_valid(username: str):
    validate_username(username)


@pytest.mark.parametrize(
    "username",
    [
        "Auser",
        "User",
        "USER",
        "user name",
        "user/name",
        "user\\name",
        "user#name",
        "user%name",
        "user&name",
        "user*name",
        "user!name",
        "user?name",
    ],
)
def test_validate_username_invalid_pattern(username: str):
    with pytest.raises(HTTPException):
        validate_username(username)


@pytest.mark.parametrize(
    "username",
    [
        "system",
        "automatic",
        "deleted",
    ],
)
def test_validate_username_reserved(username: str):
    with pytest.raises(HTTPException):
        validate_username(username)


@pytest.mark.parametrize(
    "username",
    [
        "watcher",
        "watcher1",
        "watcher_user",
        "watcher-user",
        "watcher@domain",
        "watcher.example",
    ],
)
def test_validate_username_watcher_prefix(username: str):
    with pytest.raises(HTTPException):
        validate_username(username)


@pytest.mark.parametrize(
    "username",
    [
        "mywatcher",
        "user-watcher",
        "user_watcher",
        "thewatcher",
        "xwatcher",
    ],
)
def test_validate_username_watcher_not_prefix(username: str):
    validate_username(username)
