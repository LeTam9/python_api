from typing import List, Optional
import models, schemas, utlis,oauth2
from fastapi import Body, Depends, FastAPI, Response, status, HTTPException, APIRouter
from sqlalchemy.orm import Session
from database import engine, get_db

router = APIRouter(
     prefix="/posts",
     tags=['Posts']
)

my_posts = [{"title": "title of post 1", "content":"content of post 1", "id":1},{"title":"favorite foods", "content":"i love pizza", "id":2}]


def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p

def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p['id'] == id:
            return i

@router.get("/", response_model=List[schemas.Post])
def get_posts(db: Session = Depends(get_db),current_user: int = Depends(oauth2.get_current_user),
 limit: int = 10, skip: int = 0, search: Optional[str] = ""):

    # cursor.execute("""SELECT * FROM posts """)
    # posts =  cursor.fetchall()

    posts =  db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    results = db.query(models.Post).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)

    return posts


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES(%s,%s,%s) RETURNING * """,(post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()
    new_post = models.Post(owner_id =current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/{id}", response_model=schemas.Post)
def get_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("""SELECT * from posts WHERE id = %s """, (str(id)))
    # test_post =  cursor.fetchone()
    post = db.query(models.Post).filter(models.Post.id == id).first()

    post = find_post(id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail=f"post with id:{id} was not found")

    return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    # cursor.execute(""" DELETE FROM posts WHERE id = %s returning * """, (str(id)))
    # delete_post =  cursor.fetchone()
    # conn.commit()
    post =  db.query(models.Post).filter(models.Post.id == id)

    if post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id:{id} does not exits")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code =status.HTTP_403_FORBIDDEN, detail="NOT authorized to perform request")

    post.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.Post)
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db),  current_user: int = Depends(oauth2.get_current_user)):

    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s 
    # RETURNING * """,
    #                 (post.title, post.content, post.published))

    # update_post =  cursor.fetchone()
    # conn.commit()
   
    post_query = db.query(models.Post).filter(models.Post.id == id)

    posts = post_query.first()

    if posts == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id:{id} does not exits")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code =status.HTTP_403_FORBIDDEN, detail="NOT authorized to perform request")

    post_query.update(post.dict(), synchronize_session=False)

    db.commit()

    return post_query.first()
