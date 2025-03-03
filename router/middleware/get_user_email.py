from fastapi import Cookie, HTTPException

from ..utils.security import verify_token


def get_current_user(access_token: str = Cookie()):
    print(f"Cookie form client {access_token}")
    if not access_token:
        raise HTTPException(status_code=401, detail="Access token missing")
    payload = verify_token(access_token)
    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    return email
