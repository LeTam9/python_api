from email.policy import default
from fastapi import Depends, FastAPI, Response, status, HTTPException, APIRouter
from fastapi.security.oauth2 import  OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import database, schemas , models, utlis, oauth2

router = APIRouter(tags=['Authentication'])

@router.post('/login', response_model= schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(
        models.User.email == user_credentials.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid Credentials")

    if not utlis.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid Credentials")

    access_token = oauth2.create_access_token(data = {"user_id": user.id})    

    return {"access_token": access_token, "token_type": "bearer"}

