import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import ConflictException, UnauthorizedException
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import Token, UserRegister

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = UserRepository(db)

    # --- Password-based auth ---

    def register(self, user_in: UserRegister) -> User:
        if self.repo.get_by_email(user_in.email):
            raise ConflictException("A user with this email already exists.")

        user = User(
            email=user_in.email,
            full_name=user_in.full_name,
            hashed_password=get_password_hash(user_in.password),
        )
        return self.repo.create(user)

    def authenticate(self, email: str, password: str) -> User:
        user = self.repo.get_by_email(email)
        if user is None or user.hashed_password is None:
            raise UnauthorizedException("Incorrect email or password.")
        if not verify_password(password, user.hashed_password):
            raise UnauthorizedException("Incorrect email or password.")
        if not user.is_active:
            raise UnauthorizedException("This account is inactive.")
        return user

    def issue_token(self, user: User) -> Token:
        access_token = create_access_token(subject=str(user.id))
        return Token(access_token=access_token)

    # --- Google OAuth ---

    def build_google_auth_url(self) -> str:
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "consent",
        }
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{GOOGLE_AUTH_URL}?{query}"

    def handle_google_callback(self, code: str) -> User:
        token_data = self._exchange_google_code(code)
        profile = self._fetch_google_profile(token_data["access_token"])

        google_sub = profile["sub"]
        email = profile["email"]

        user = self.repo.get_by_google_sub(google_sub)
        if user is not None:
            return user

        # Link to an existing password-based account with the same email,
        # otherwise create a brand-new Google-only user.
        user = self.repo.get_by_email(email)
        if user is not None:
            return self.repo.update(user, {"google_sub": google_sub})

        new_user = User(
            email=email,
            full_name=profile.get("name"),
            google_sub=google_sub,
        )
        return self.repo.create(new_user)

    def _exchange_google_code(self, code: str) -> dict:
        response = httpx.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def _fetch_google_profile(self, access_token: str) -> dict:
        response = httpx.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
