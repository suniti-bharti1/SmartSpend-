
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import Category
from schemas.categories import CategoryCreate, CategoryResponse

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


@router.get("/", response_model=list[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()


@router.post("/", response_model=CategoryResponse)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db)
):
    new_category = Category(
        category_name=category.category_name,
        category_type=category.category_type
    )

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category
