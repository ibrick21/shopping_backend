from order.database import Base, engine
from order.orm_models import OrderDB

Base.metadata.create_all(bind=engine)
