from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def list_users():
    return [{"id": 1, "name": "张三"}]


@router.get("/{user_id}")
def get_user(user_id: int):
    return {"id": user_id}


@router.post("/")
def create_user():
    return {"message": "创建用户"}