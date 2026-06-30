from fastapi import FastAPI
from database import SessionLocal, engine
from models import Base, Prediction
from worker import check_predictions
from datetime import datetime, timedelta
import requests
import threading
import uvicorn

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Start background worker
threading.Thread(target=check_predictions, daemon=True).start()


@app.post("/predict")
def create_prediction(coin: str, direction: str, minutes: int):

    db = SessionLocal()

    try:
       response = requests.get(
    f"https://api.binance.com/api/v3/ticker/price?symbol={coin.upper()}"
).json()

if "price" not in response:
    return {
        "error": "Invalid coin symbol or Binance API returned an error.",
        "response": response
    }

start_price = float(response["price"])
        end_time = datetime.utcnow() + timedelta(minutes=minutes)

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

        return {
            "message": "Prediction saved",
            "id": prediction.id
        }

    finally:
        db.close()


@app.get("/results")
def get_results():
    db = SessionLocal()

    try:
        predictions = db.query(Prediction).all()

        return [
            {
                "id": p.id,
                "coin": p.coin,
                "direction": p.direction,
                "start_price": p.start_price,
                "end_price": p.end_price,
                "status": p.status,
                "minutes": p.minutes
            }
            for p in predictions
        ]

    finally:
        db.close()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
