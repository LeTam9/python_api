import models, schemas, utlis
from fastapi import Body, Depends, FastAPI, Response, status, HTTPException, APIRouter
from sqlalchemy.orm import Session
from database import engine, get_db


router = APIRouter(
    prefix="/users",
    tags=['Users']
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(use: schemas.UserCreate, db: Session = Depends(get_db)):
    hashed_password =  utlis.hash(use.password)
    use.password = hashed_password
    new_user = models.User(**use.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get('/{id}', response_model=schemas.UserOut)
def get_user(id: int,db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {id} does not exist")

    return user    