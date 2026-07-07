from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.pagination import PageParams, get_page_params
from app.core.response import page_response, success
from app.schemas.product import (
    BrandCreateIn,
    BrandOut,
    BrandUpdateIn,
    CategoryCreateIn,
    CategoryOut,
    CategoryUpdateIn,
    ProductCreateIn,
    ProductDetailOut,
    ProductListOut,
    ProductSkuCreateIn,
    ProductSkuOut,
    ProductSkuUpdateIn,
    ProductUpdateIn,
)
from app.services.product_service import ProductService

router = APIRouter()


def _product_list_item(product) -> dict:
    total_stock = sum(sku.stock for sku in product.skus if sku.deleted_at is None and sku.status == "active")
    locked_stock = sum(sku.locked_stock for sku in product.skus if sku.deleted_at is None and sku.status == "active")
    available_stock = max(total_stock - locked_stock, 0)
    return ProductListOut.model_validate(product).model_copy(
        update={
            "brand_name": product.brand.name if product.brand else None,
            "category_name": product.category.name if product.category else None,
            "total_stock": total_stock,
            "available_stock": available_stock,
            "has_stock": available_stock > 0,
        }
    ).model_dump()


@router.get("")
def list_products(
    keyword: str | None = Query(default=None, max_length=64),
    category_id: int | None = None,
    brand_id: int | None = None,
    min_price_cent: int | None = Query(default=None, ge=0),
    max_price_cent: int | None = Query(default=None, ge=0),
    sort: str = Query(default="latest", pattern="^(latest|price_asc|price_desc|sales_desc)$"),
    page: PageParams = Depends(get_page_params),
    db: Session = Depends(get_db),
):
    items, total = ProductService(db).list_products(
        page, keyword, category_id, brand_id, min_price_cent, max_price_cent, sort
    )
    return page_response([_product_list_item(item) for item in items], page.page, page.page_size, total)


@router.get("/categories")
def list_categories(db: Session = Depends(get_db)):
    items = ProductService(db).list_categories()
    return success([item.model_dump() for item in items])


@router.post("/categories")
def create_category(payload: CategoryCreateIn, db: Session = Depends(get_db)):
    category = ProductService(db).create_category(payload)
    return success(CategoryOut.model_validate(category).model_dump())


@router.patch("/categories/{category_id}")
def update_category(category_id: int, payload: CategoryUpdateIn, db: Session = Depends(get_db)):
    category = ProductService(db).update_category(category_id, payload)
    return success(CategoryOut.model_validate(category).model_dump())


@router.get("/brands")
def list_brands(db: Session = Depends(get_db)):
    items = ProductService(db).list_brands()
    return success([BrandOut.model_validate(item).model_dump() for item in items])


@router.post("/brands")
def create_brand(payload: BrandCreateIn, db: Session = Depends(get_db)):
    brand = ProductService(db).create_brand(payload)
    return success(BrandOut.model_validate(brand).model_dump())


@router.patch("/brands/{brand_id}")
def update_brand(brand_id: int, payload: BrandUpdateIn, db: Session = Depends(get_db)):
    brand = ProductService(db).update_brand(brand_id, payload)
    return success(BrandOut.model_validate(brand).model_dump())


@router.post("")
def create_product(payload: ProductCreateIn, db: Session = Depends(get_db)):
    product = ProductService(db).create_product(payload)
    return success(ProductDetailOut.model_validate(product).model_dump())


@router.get("/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = ProductService(db).get_product_detail(product_id)
    return success(ProductDetailOut.model_validate(product).model_dump())


@router.patch("/{product_id}")
def update_product(product_id: int, payload: ProductUpdateIn, db: Session = Depends(get_db)):
    product = ProductService(db).update_product(product_id, payload)
    return success(ProductDetailOut.model_validate(product).model_dump())


@router.post("/{product_id}/skus")
def create_sku(product_id: int, payload: ProductSkuCreateIn, db: Session = Depends(get_db)):
    sku = ProductService(db).create_sku(product_id, payload)
    return success(ProductSkuOut.model_validate(sku).model_dump())


@router.patch("/skus/{sku_id}")
def update_sku(sku_id: int, payload: ProductSkuUpdateIn, db: Session = Depends(get_db)):
    sku = ProductService(db).update_sku(sku_id, payload)
    return success(ProductSkuOut.model_validate(sku).model_dump())
