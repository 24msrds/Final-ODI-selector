from fastapi import FastAPI, HTTPException
from backend.selector import select_team

app = FastAPI(title="ODI AI Selector")

@app.get("/")
def home():
    return {"message": "ODI AI Selector Running ✅"}

@app.get("/best-xi")
def best_xi(country: str):
    try:
        team, captain = select_team(country)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if team is None or team.empty:
        raise HTTPException(status_code=404, detail=f"No data for: {country}")

    return {
        "country": country,
        "captain": captain,
        "team": team.to_dict(orient="records"),
    }