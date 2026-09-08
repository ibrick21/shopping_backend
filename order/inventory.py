class Inventory:
    def __init__(self):
        self.stocks = {}

    def add_stock(self, product: str, quantity: int):
        if quantity <= 0:
            raise ValueError("재고 수량은 1개 이상이어야 합니다.")

        if product in self.stocks:
            self.stocks[product] += quantity
        else:
            self.stocks[product] = quantity

    def decrease_stock(self,product: str, quantity: int):
        if product in self.stocks:
            if self.stocks[product] < quantity:
                raise ValueError("재고가 부족합니다.")
            
            self.stocks[product] -= quantity
        else:
            raise ValueError("등록되지 않은 상품입니다.")

