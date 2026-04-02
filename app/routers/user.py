from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status

from app.models.user import UserCreate, UserResponse
from app.storage.user import get_user_db, user_id_counter

router = APIRouter()


@router.post(
    "/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def create_user(user_data: UserCreate, db: dict = Depends(get_user_db)):
    global user_id_counter
    user_id_counter += 1

    new_user = {
        "id": user_id_counter,
        "email": user_data.email,
        "name": user_data.name,
        # 실제로는 해싱 알고리즘 사용
        "hashed_password": f"hashed_{user_data.password}",
        "is_admin": False,
        "created_at": datetime.now(),
    }

    db[user_id_counter] = new_user
    return new_user


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: dict = Depends(get_user_db)):
    if user_id not in db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"{user_id} is not found"
        )

    return db[user_id]


@router.get("/users", response_model=list[UserResponse])
async def list_users(skip: int = 0, limit: int = 10, db: dict = Depends(get_user_db)):
    users = list(db.values())
    return users[skip : skip + limit]


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: dict = Depends(get_user_db)):
    if user_id not in db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"{user_id} is not found"
        )

    del db[user_id]
