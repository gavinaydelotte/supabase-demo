import os

from fastapi import FastAPI
from supabase import create_client

app = FastAPI()
supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SECRET_KEY"])


@app.get("/analyze/{symbol}")
async def analyze_stock(symbol: str):
    # 1. Fetch the data from Supabase
    response = (
        supabase.table("stock_records")
        .select("*")
        .eq("ticker", symbol.upper())
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    if not response.data:
        return {"error": "No data found in database. Run ingest.py first."}

    record = response.data[0]
    initial_p = record["initial_price"]
    final_p = record["final_price"]

    # 2. TASK: Determine the Signal
    # Logic: If final > initial, signal is "Bullish". Otherwise "Bearish".
    signal = "Bullish" if final_p > initial_p else "Bearish"

    return {
        "ticker": symbol.upper(),
        "analysis": {
            "start_price": initial_p,
            "current_price": final_p,
            "signal": signal,
            "source": "Internal Database",
        },
    }


@app.get("/history/{symbol}")
async def stock_history(symbol: str):
    response = (
        supabase.table("stock_records")
        .select("*")
        .eq("ticker", symbol.upper())
        .order("created_at", desc=False)
        .execute()
    )

    return response.data
