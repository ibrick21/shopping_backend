from .models import Product


class ProductService:
    def __init__(self, product_repository):
        self.product_repository = product_repository

    def create_product(self, name: str, price: int, stock: int) -> Product:
        product = Product(
            name = name,
            price = price,
            stock = stock 
    )

        self.product_repository.add_product(product)

        return product
    
   