from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.user import Token, UserRead, UserRegister
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=201)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    service = AuthService(db)
    user = service.register(user_in)
    return user


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Standard OAuth2 password flow — accepts form data (username, password).
    `username` is the user's email. This shape is what makes the
    interactive /docs "Authorize" button work out of the box.
    """
    service = AuthService(db)
    user = service.authenticate(email=form_data.username, password=form_data.password)
    return service.issue_token(user)


@router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/google/login")
def google_login(db: Session = Depends(get_db)):
    """
    Redirects the browser to Google's consent screen. Requires
    GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET to be set in .env.
    """
    service = AuthService(db)
    return RedirectResponse(service.build_google_auth_url())


@router.get("/google/callback", response_model=Token)
def google_callback(code: str, db: Session = Depends(get_db)):
    """
    Google redirects here with a `code` query param after the user
    approves consent. We exchange it for a Google access token, fetch
    the profile, find-or-create the local user, and issue our own JWT.
    """
    service = AuthService(db)
    user = service.handle_google_callback(code)
    return service.issue_token(user)
