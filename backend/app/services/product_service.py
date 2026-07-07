from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import AppException, ErrorCode
from app.core.pagination import PageParams
from app.models.product import Brand, InventoryLog, Product, ProductCategory, ProductSku
from app.repositories.product_repo import ProductRepository
from app.schemas.product import (
    BrandCreateIn,
    BrandUpdateIn,
    CategoryCreateIn,
    CategoryTreeOut,
    CategoryUpdateIn,
    ProductCreateIn,
    ProductSkuCreateIn,
    ProductSkuUpdateIn,
    ProductUpdateIn,
)


class ProductService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ProductRepository(db)

    def list_categories(self, include_inactive: bool = False) -> list[CategoryTreeOut]:
        categories = self.repo.list_categories(include_inactive)
        nodes = {
            item.id: CategoryTreeOut.model_validate(item).model_copy(update={"children": []}) for item in categories
        }
        roots: list[CategoryTreeOut] = []
        for item in categories:
            node = nodes[item.id]
            if item.parent_id and item.parent_id in nodes:
                nodes[item.parent_id].children.append(node)
            else:
                roots.append(node)
        return roots

    def create_category(self, payload: CategoryCreateIn) -> ProductCategory:
        if payload.parent_id:
            self._get_active_category(payload.parent_id)
        category = ProductCategory(**payload.model_dump())
        try:
            return self.repo.create_category(category)
        except IntegrityError as exc:
            self.db.rollback()
            raise AppException(ErrorCode.conflict, "商品分类编码已存在", 409) from exc

    def update_category(self, category_id: int, payload: CategoryUpdateIn) -> ProductCategory:
        category = self._get_category(category_id)
        data = payload.model_dump(exclude_unset=True)
        if data.get("parent_id"):
            if data["parent_id"] == category_id:
                raise AppException(ErrorCode.validation_error, "父级分类不能是自己", 400)
            self._get_active_category(data["parent_id"])
        for field, value in data.items():
            setattr(category, field, value)
        try:
            return self.repo.save_category(category)
        except IntegrityError as exc:
            self.db.rollback()
            raise AppException(ErrorCode.conflict, "商品分类编码已存在", 409) from exc

    def list_brands(self, include_inactive: bool = False) -> list[Brand]:
        return self.repo.list_brands(include_inactive)

    def create_brand(self, payload: BrandCreateIn) -> Brand:
        brand = Brand(**payload.model_dump())
        try:
            return self.repo.create_brand(brand)
        except IntegrityError as exc:
            self.db.rollback()
            raise AppException(ErrorCode.conflict, "品牌名称已存在", 409) from exc

    def update_brand(self, brand_id: int, payload: BrandUpdateIn) -> Brand:
        brand = self._get_brand(brand_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(brand, field, value)
        try:
            return self.repo.save_brand(brand)
        except IntegrityError as exc:
            self.db.rollback()
            raise AppException(ErrorCode.conflict, "品牌名称已存在", 409) from exc

    def list_products(
        self,
        page: PageParams,
        keyword: str | None = None,
        category_id: int | None = None,
        brand_id: int | None = None,
        min_price_cent: int | None = None,
        max_price_cent: int | None = None,
        sort: str = "latest",
        include_inactive: bool = False,
    ) -> tuple[list[Product], int]:
        if sort not in {"latest", "price_asc", "price_desc", "sales_desc"}:
            raise AppException(ErrorCode.validation_error, "不支持的排序方式", 400)
        return self.repo.list_products(
            page, keyword, category_id, brand_id, min_price_cent, max_price_cent, sort, include_inactive
        )

    def get_product_detail(self, product_id: int, include_inactive: bool = False) -> Product:
        product = self.repo.get_product_detail(product_id, include_inactive)
        if product is None:
            raise AppException(ErrorCode.not_found, "商品不存在", 404)
        return product

    def create_product(self, payload: ProductCreateIn) -> Product:
        self._get_active_category(payload.category_id)
        if payload.brand_id:
            self._get_active_brand(payload.brand_id)
        data = payload.model_dump(exclude={"skus"})
        product = Product(**data)
        product.skus = [ProductSku(**sku.model_dump()) for sku in payload.skus]
        try:
            created = self.repo.create_product(product)
        except IntegrityError as exc:
            self.db.rollback()
            raise AppException(ErrorCode.conflict, "商品或 SKU 编码冲突", 409) from exc
        return self.get_product_detail(created.id, include_inactive=True)

    def update_product(self, product_id: int, payload: ProductUpdateIn) -> Product:
        product = self.get_product_detail(product_id, include_inactive=True)
        data = payload.model_dump(exclude_unset=True)
        if "category_id" in data and data["category_id"] is not None:
            self._get_active_category(data["category_id"])
        if "brand_id" in data and data["brand_id"] is not None:
            self._get_active_brand(data["brand_id"])
        for field, value in data.items():
            setattr(product, field, value)
        updated = self.repo.save_product(product)
        return self.get_product_detail(updated.id, include_inactive=True)

    def create_sku(self, product_id: int, payload: ProductSkuCreateIn) -> ProductSku:
        self.get_product_detail(product_id, include_inactive=True)
        sku = ProductSku(product_id=product_id, **payload.model_dump())
        inventory_log = InventoryLog(
            product_id=product_id,
            sku_id=0,
            change_type="init",
            change_quantity=payload.stock,
            stock_before=0,
            stock_after=payload.stock,
            related_type="product_sku",
            related_id=payload.sku_code,
            remark="初始化 SKU 库存",
        )
        try:
            return self.repo.create_sku(sku, inventory_log)
        except IntegrityError as exc:
            self.db.rollback()
            raise AppException(ErrorCode.conflict, "SKU 编码已存在", 409) from exc

    def update_sku(self, sku_id: int, payload: ProductSkuUpdateIn) -> ProductSku:
        sku = self.repo.get_sku(sku_id)
        if sku is None or sku.deleted_at is not None:
            raise AppException(ErrorCode.not_found, "SKU 不存在", 404)
        data = payload.model_dump(exclude_unset=True)
        inventory_log = None
        if "stock" in data and data["stock"] is not None and data["stock"] != sku.stock:
            inventory_log = InventoryLog(
                product_id=sku.product_id,
                sku_id=sku.id,
                change_type="adjust",
                change_quantity=data["stock"] - sku.stock,
                stock_before=sku.stock,
                stock_after=data["stock"],
                related_type="manual",
                related_id=str(sku.id),
                remark="手动调整 SKU 库存",
            )
        for field, value in data.items():
            setattr(sku, field, value)
        try:
            return self.repo.save_sku(sku, inventory_log)
        except IntegrityError as exc:
            self.db.rollback()
            raise AppException(ErrorCode.conflict, "SKU 编码已存在", 409) from exc

    def _get_category(self, category_id: int) -> ProductCategory:
        category = self.repo.get_category(category_id)
        if category is None or category.deleted_at is not None:
            raise AppException(ErrorCode.not_found, "商品分类不存在", 404)
        return category

    def _get_active_category(self, category_id: int) -> ProductCategory:
        category = self._get_category(category_id)
        if category.status != "active":
            raise AppException(ErrorCode.validation_error, "商品分类不可用", 400)
        return category

    def _get_brand(self, brand_id: int) -> Brand:
        brand = self.repo.get_brand(brand_id)
        if brand is None or brand.deleted_at is not None:
            raise AppException(ErrorCode.not_found, "品牌不存在", 404)
        return brand

    def _get_active_brand(self, brand_id: int) -> Brand:
        brand = self._get_brand(brand_id)
        if brand.status != "active":
            raise AppException(ErrorCode.validation_error, "品牌不可用", 400)
        return brand
