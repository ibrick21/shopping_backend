class Payment:
    def __init__(self, balance):
        if balance < 0:
            raise ValueError("잔액은 0원 이상이어야 합니다.")

        self.balance = balance

    def pay(self, amount: int) -> bool:
        if amount <= 0:
            raise ValueError("결제 금액은 1원 이상이어야 합니다.")
        
        if amount <= self.balance:
            self.balance -= amount
            return True

        return False 

    def refund(self, amount: int) -> bool:
        if amount <= 0: 
            raise ValueError("결제 금액은 1원 이상이어야 합니다.")

        self.balance += amount
        return True