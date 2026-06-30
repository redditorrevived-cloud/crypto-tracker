from fastapi import FastAPI
from database import SessionLocal, engine
from models import Base, Prediction
from datetime import datetime, timedelta
import requests
import uvicorn

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI()


@app.post("/predict")
def create_prediction(coin: str, direction: str, minutes: int):

    db = SessionLocal()

    try:
        # Get current price from Binance
        start_price = float(requests.get(
            f"https://api.binance.com/api/v3/ticker/price?symbol={coin}"
        ).json()["price"])

        # Calculate end time
        end_time = datetime.utcnow() + timedelta(minutes=minutes)

        # Save prediction
        prediction = Prediction(
            coin=coin,
            direction=direction,
            minutes=minutes,
            start_price=start_price,
            end_time=end_time,
            status="pending"
        )

        db.add(prediction)
        db.commit()
        db.refresh(prediction)

        return {"message": "Prediction saved", "id": prediction.id}

    finally:
        db.close()


# For local testing only (Render ignores this)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)