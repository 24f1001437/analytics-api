from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# --- CORS SETUP ---
# This tells your server: "It is okay if the exam website tries to talk to me."
# Without this, web browsers block the request for security reasons.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DATA BLUEPRINTS ---
# We tell FastAPI exactly what the incoming data looks like.
class Event(BaseModel):
    user: str
    amount: float
    ts: int

class Payload(BaseModel):
    events: List[Event]

# --- THE ENDPOINT ---
@app.post("/analytics")
def process_analytics(
    payload: Payload,
    x_api_key: Optional[str] = Header(None) # Look for the key in the headers
):
    # 1. THE BOUNCER (Authentication)
    expected_key = "ak_g2w0a728y91h7stz6883xvfd"
    if x_api_key != expected_key:
        # If the key is missing or wrong, kick them out with a 401 Unauthorized
        raise HTTPException(status_code=401, detail="Unauthorized")

    # 2. THE MATH (Aggregation)
    events = payload.events
    
    unique_users = set()
    revenue = 0.0
    user_positive_revenue = {}

    for event in events:
        # Add user to the set (sets automatically ignore duplicates)
        unique_users.add(event.user)
        
        # Only count positive amounts for revenue and top_user
        if event.amount > 0:
            revenue += event.amount
            
            # Keep a running total of positive revenue for each user
            if event.user not in user_positive_revenue:
                user_positive_revenue[event.user] = 0.0
            user_positive_revenue[event.user] += event.amount

    # Find the top user (the one with the most positive revenue)
    top_user = ""
    highest_amount = -1.0
    for user, amount in user_positive_revenue.items():
        if amount > highest_amount:
            highest_amount = amount
            top_user = user

    # 3. THE RESPONSE
    return {
        "email": "YOUR_ACTUAL_EMAIL@EXAMPLE.COM", # <-- CHANGE THIS TO YOUR EXAM EMAIL!
        "total_events": len(events),
        "unique_users": len(unique_users),
        "revenue": revenue,
        "top_user": top_user
    }