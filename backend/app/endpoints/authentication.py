import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.users.authentication import Tokens, authenticate_user, get_authenticated_user, get_user_tokens
from app.users.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix='',
    tags=['Authentication'],
)

@router.post("/login", response_model=Tokens)
async def __login_for_access_token__(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
    db: Annotated[Session, Depends(get_db)]
):
    user = authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials.")
    
    return get_user_tokens(user)

@router.get("/me", response_model=User)
def get_me(user: Annotated[User, Depends(get_authenticated_user)],):
    return user