import time
import requests
from datetime import datetime
from database import SessionLocal
from models import Prediction

def check_predictions():
    print("Worker started...")

    while True:
        db = SessionLocal()

        try:
            predictions = db.query(Prediction).filter(Prediction.status == "pending").all()

            for p in predictions:

                if p.end_time and datetime.utcnow() >= p.end_time:

                    try:
                        response = requests.get(
                            f"https://api.binance.com/api/v3/ticker/price?symbol={p.coin}"
                        ).json()

                        end_price = float(response["price"])
                        start_price = float(p.start_price)

                        p.end_price = str(end_price)

                        if (p.direction.lower() == "up" and end_price > start_price) or \
                           (p.direction.lower() == "down" and end_price < start_price):
                            p.status = "win"
                        else:
                            p.status = "loss"

                        db.commit()

                    except Exception as e:
                        print("Error checking prediction:", e)

        except Exception as e:
            print("Worker loop error:", e)

        finally:
            db.close()

        time.sleep(15)