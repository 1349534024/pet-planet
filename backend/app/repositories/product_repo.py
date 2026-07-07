from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.pagination import PageParams
from app.models.product import Brand, InventoryLog, Product, ProductCategory, ProductSku


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_categories(self, include_inactive: bool = False) -> list[ProductCategory]:
        stmt = select(ProductCategory).where(ProductCategory.deleted_at.is_(None))
        if not include_inactive:
            stmt = stmt.where(ProductCategory.status == "active")
        return list(self.db.scalars(stmt.order_by(ProductCategory.sort_order.asc(), ProductCategory.id.asc())))

    def get_category(self, category_id: int) -> ProductCategory | None:
        return self.db.get(ProductCategory, category_id)

    def get_category_by_code(self, code: str) -> ProductCategory | None:
        return self.db.scalar(
            select(ProductCategory).where(ProductCategory.code == code, ProductCategory.deleted_at.is_(None))
        )

    def create_category(self, category: ProductCategory) -> ProductCategory:
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def save_category(self, category: ProductCategory) -> ProductCategory:
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def list_brands(self, include_inactive: bool = False) -> list[Brand]:
        stmt = select(Brand).where(Brand.deleted_at.is_(None))
        if not include_inactive:
            stmt = stmt.where(Brand.status == "active")
        return list(self.db.scalars(stmt.order_by(Brand.id.desc())))

    def get_brand(self, brand_id: int) -> Brand | None:
        return self.db.get(Brand, brand_id)

    def create_brand(self, brand: Brand) -> Brand:
        self.db.add(brand)
        self.db.commit()
        self.db.refresh(brand)
        return brand

    def save_brand(self, brand: Brand) -> Brand:
        self.db.add(brand)
        self.db.commit()
        self.db.refresh(brand)
        return brand

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
        stmt = (
            select(Product)
            .options(selectinload(Product.category), selectinload(Product.brand), selectinload(Product.skus))
            .where(Product.deleted_at.is_(None))
        )
        stmt = self._apply_product_filters(
            stmt, keyword, category_id, brand_id, min_price_cent, max_price_cent, include_inactive
        )
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        stmt = self._apply_sort(stmt, sort)
        items = list(self.db.scalars(stmt.offset(page.offset).limit(page.page_size)))
        return items, total

    def get_product_detail(self, product_id: int, include_inactive: bool = False) -> Product | None:
        stmt = (
            select(Product)
            .options(selectinload(Product.category), selectinload(Product.brand), selectinload(Product.skus))
            .where(Product.id == product_id, Product.deleted_at.is_(None))
        )
        if not include_inactive:
            stmt = stmt.where(Product.status == "on_sale")
        return self.db.scalar(stmt)

    def create_product(self, product: Product) -> Product:
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def save_product(self, product: Product) -> Product:
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def get_sku(self, sku_id: int) -> ProductSku | None:
        return self.db.get(ProductSku, sku_id)

    def create_sku(self, sku: ProductSku, inventory_log: InventoryLog | None = None) -> ProductSku:
        self.db.add(sku)
        self.db.flush()
        if inventory_log:
            inventory_log.sku_id = sku.id
            self.db.add(inventory_log)
        self.db.commit()
        self.db.refresh(sku)
        return sku

    def save_sku(self, sku: ProductSku, inventory_log: InventoryLog | None = None) -> ProductSku:
        self.db.add(sku)
        if inventory_log:
            self.db.add(inventory_log)
        self.db.commit()
        self.db.refresh(sku)
        return sku

    def _apply_product_filters(
        self,
        stmt: Select[tuple[Product]],
        keyword: str | None,
        category_id: int | None,
        brand_id: int | None,
        min_price_cent: int | None,
        max_price_cent: int | None,
        include_inactive: bool,
    ) -> Select[tuple[Product]]:
        if not include_inactive:
            stmt = stmt.where(Product.status == "on_sale")
        if keyword:
            like_keyword = f"%{keyword}%"
            stmt = stmt.where(or_(Product.title.like(like_keyword), Product.subtitle.like(like_keyword)))
        if category_id:
            stmt = stmt.where(Product.category_id == category_id)
        if brand_id:
            stmt = stmt.where(Product.brand_id == brand_id)
        if min_price_cent is not None:
            stmt = stmt.where(Product.price_cent >= min_price_cent)
        if max_price_cent is not None:
            stmt = stmt.where(Product.price_cent <= max_price_cent)
        return stmt

    def _apply_sort(self, stmt: Select[tuple[Product]], sort: str) -> Select[tuple[Product]]:
        if sort == "price_asc":
            return stmt.order_by(Product.price_cent.asc(), Product.id.desc())
        if sort == "price_desc":
            return stmt.order_by(Product.price_cent.desc(), Product.id.desc())
        if sort == "sales_desc":
            return stmt.order_by(Product.sales_count.desc(), Product.id.desc())
        return stmt.order_by(Product.id.desc())
