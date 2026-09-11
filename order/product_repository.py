from sqlalchemy.orm import Session
from .orm_models import ProductDB
from .models import Product


class ProductRepository:
    def __init__(self, session: Session):
        self.session = session

    def _product_db_to_product(self,product_db: ProductDB) -> Product: 
        product = Product(
            name = product_db.name,
            price = product_db.price,
            stock = product_db.stock,
            product_id = product_db.product_id
     )

        return product


    def find_product(self, product_id: int) -> Product | None:
        product_db = self.session.get(ProductDB, product_id)

        if product_db is None:
            return None

        return self._product_db_to_product(product_db)

    def add_product(self, product: Product):
        product_db = ProductDB(
            name = product.name,
            price = product.price,
            stock = product.stock
        )

        self.session.add(product_db)
        self.session.commit()

        product.product_id = product_db.product_id

        return product

    def decrease_stock(self, product_id: int, quantity: int):
        product_db = self.session.get(ProductDB, product_id)

        product_db.stock -= quantity

        self.session.commit()

        
    def increase_stock(self, product_id: int, quantity: int):
        product_db = self.session.get(ProductDB, product_id)

        product_db.stock += quantity
        
        self.session.commit()