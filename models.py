from sqlalchemy import Column, Integer, String, DateTime
from database import Base

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    coin = Column(String)
    direction = Column(String)
    minutes = Column(Integer)

    start_price = Column(String)
    end_price = Column(String, nullable=True)

    end_time = Column(DateTime)

    status = Column(String)  # pending / win / loss