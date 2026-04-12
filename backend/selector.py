import os
import pandas as pd

POS_OPENER = "opener"
POS_MIDDLE = "middle order"
POS_LOWER  = "lower order"
POS_BOWLER = "bowler"

ROLE_WK         = "wicketkeeper"
ROLE_ALLROUNDER = "allrounder"
ROLE_BOWLER     = "bowler"
ROLE_BATTER     = "batter"

CSV_FILENAME = "merged_odi_stats.csv"

VENUES = {
    # INDIA
    "Wankhede Stadium, Mumbai":          {"pitch":"pace",     "country":"India",        "avg_score":310, "dew":True,  "desc":"High-scoring pace venue. Fast outfield, dew plays big role at night."},
    "Eden Gardens, Kolkata":             {"pitch":"spin",     "country":"India",        "avg_score":265, "dew":True,  "desc":"Spin-friendly, grips and turns from first innings. Slow outfield."},
    "Narendra Modi Stadium, Ahmedabad":  {"pitch":"pace",     "country":"India",        "avg_score":300, "dew":False, "desc":"Drop-in pitch with pace and bounce early. Dry conditions minimise dew."},
    "Chinnaswamy Stadium, Bengaluru":    {"pitch":"pace",     "country":"India",        "avg_score":330, "dew":True,  "desc":"Batters paradise. Small boundary, fast outfield produces huge totals."},
    "Chepauk, Chennai":                  {"pitch":"spin",     "country":"India",        "avg_score":255, "dew":False, "desc":"Classic spin deck — slow and low, generous turn from early on."},
    "Arun Jaitley Stadium, Delhi":       {"pitch":"pace",     "country":"India",        "avg_score":290, "dew":True,  "desc":"Pace-friendly first innings, flattens later. Dew heavy in night matches."},
    "Holkar Stadium, Indore":            {"pitch":"spin",     "country":"India",        "avg_score":275, "dew":False, "desc":"Dusty dry pitch, breaks up quickly, heavily favours spin from midpoint."},
    "Barsapara Stadium, Guwahati":       {"pitch":"balanced", "country":"India",        "avg_score":280, "dew":True,  "desc":"Fresh pitch with something for everyone — pace early, spin later."},
    "Rajiv Gandhi Stadium, Hyderabad":   {"pitch":"balanced", "country":"India",        "avg_score":285, "dew":True,  "desc":"Even contest early; spinners dominate second half. Dew aids chasers."},
    # AUSTRALIA
    "Melbourne Cricket Ground":          {"pitch":"pace",     "country":"Australia",    "avg_score":280, "dew":False, "desc":"Classic MCG bounce. Pacers exploit carry; one of quickest outfields."},
    "Sydney Cricket Ground":             {"pitch":"spin",     "country":"Australia",    "avg_score":265, "dew":False, "desc":"SCG spin-friendly surface suits off-spin and leg-spin alike."},
    "Adelaide Oval":                     {"pitch":"pace",     "country":"Australia",    "avg_score":290, "dew":False, "desc":"True even bounce with lateral pace movement. Day-night conditions."},
    "The Gabba, Brisbane":               {"pitch":"pace",     "country":"Australia",    "avg_score":285, "dew":False, "desc":"Pace fortress — steep bounce, lateral movement early."},
    "Optus Stadium, Perth":              {"pitch":"pace",     "country":"Australia",    "avg_score":290, "dew":False, "desc":"Modern Perth venue retaining traditional pace and bounce."},
    # ENGLAND
    "Lord's Cricket Ground, London":     {"pitch":"pace",     "country":"England",      "avg_score":260, "dew":False, "desc":"Iconic slope assists seam from Pavilion End. Overcast aids swing."},
    "The Oval, London":                  {"pitch":"pace",     "country":"England",      "avg_score":270, "dew":False, "desc":"Flat but seam-friendly. Vauxhall End offers movement throughout."},
    "Headingley, Leeds":                 {"pitch":"pace",     "country":"England",      "avg_score":255, "dew":False, "desc":"Green seamers paradise. Low bounce and lateral movement."},
    "Edgbaston, Birmingham":             {"pitch":"pace",     "country":"England",      "avg_score":265, "dew":False, "desc":"Bouncy surface. Pace and swing both play on cloudy days."},
    "Old Trafford, Manchester":          {"pitch":"balanced", "country":"England",      "avg_score":260, "dew":False, "desc":"Unpredictable Manchester pitch — bowler-friendly early then flattens."},
    "Trent Bridge, Nottingham":          {"pitch":"pace",     "country":"England",      "avg_score":275, "dew":False, "desc":"Free-scoring venue with fast outfield. Seam bowlers still find support."},
    # SOUTH AFRICA
    "Newlands, Cape Town":               {"pitch":"pace",     "country":"South Africa", "avg_score":265, "dew":False, "desc":"Genuine pace, bounce and swing. Sea breeze assists swing all day."},
    "SuperSport Park, Centurion":        {"pitch":"pace",     "country":"South Africa", "avg_score":290, "dew":False, "desc":"High-altitude hard pitches deliver steep bounce. One of fastest venues."},
    "Wanderers, Johannesburg":           {"pitch":"pace",     "country":"South Africa", "avg_score":295, "dew":False, "desc":"Thin air and hard surface produce extreme pace and bounce."},
    "Kingsmead, Durban":                 {"pitch":"balanced", "country":"South Africa", "avg_score":270, "dew":True,  "desc":"Coastal humidity assists swing early then flattens into batting track."},
    # PAKISTAN
    "Gaddafi Stadium, Lahore":           {"pitch":"spin",     "country":"Pakistan",     "avg_score":270, "dew":True,  "desc":"Dry dusty surface quickly assists spin. Spinners dominate middle overs."},
    "National Stadium, Karachi":         {"pitch":"spin",     "country":"Pakistan",     "avg_score":260, "dew":True,  "desc":"Slow low turner making stroke play difficult. Spinners dominate."},
    "Rawalpindi Cricket Stadium":        {"pitch":"pace",     "country":"Pakistan",     "avg_score":280, "dew":False, "desc":"Harder surface offering more pace and bounce than southern grounds."},
    "Multan Cricket Stadium":            {"pitch":"spin",     "country":"Pakistan",     "avg_score":255, "dew":False, "desc":"Extreme spinners paradise — dusty dry from ball one."},
    # BANGLADESH
    "Shere Bangla, Dhaka":               {"pitch":"spin",     "country":"Bangladesh",   "avg_score":250, "dew":True,  "desc":"Slow low surface heavily favouring spinners. Dew factor in day-night."},
    "Zahur Ahmed Stadium, Chittagong":   {"pitch":"spin",     "country":"Bangladesh",   "avg_score":245, "dew":True,  "desc":"Coastal spinners track — low and slow with high humidity."},
    # SRI LANKA
    "R.Premadasa Stadium, Colombo":      {"pitch":"spin",     "country":"Sri Lanka",    "avg_score":255, "dew":True,  "desc":"Hot humid conditions assist spin. Ball grips rough surface from early."},
    "Pallekele International Stadium":   {"pitch":"spin",     "country":"Sri Lanka",    "avg_score":260, "dew":False, "desc":"Scenic mountain venue. Turn and variable bounce makes footwork critical."},
    "Sinhalese Sports Club, Colombo":    {"pitch":"balanced", "country":"Sri Lanka",    "avg_score":265, "dew":True,  "desc":"Slightly more balanced — early pace followed by good spin assistance."},
    # NEW ZEALAND
    "Hagley Oval, Christchurch":         {"pitch":"pace",     "country":"New Zealand",  "avg_score":265, "dew":False, "desc":"Genuine seam movement. Overcast conditions frequently assist swing."},
    "Eden Park, Auckland":               {"pitch":"pace",     "country":"New Zealand",  "avg_score":250, "dew":False, "desc":"Tiny boundaries but two-paced surface. Short square boundaries help sloggers."},
    "Basin Reserve, Wellington":         {"pitch":"pace",     "country":"New Zealand",  "avg_score":245, "dew":False, "desc":"Windy City — notorious gusts affect ball flight significantly."},
    "Seddon Park, Hamilton":             {"pitch":"pace",     "country":"New Zealand",  "avg_score":270, "dew":False, "desc":"Lively surface with extra bounce. Home of NZ's biggest pace performances."},
}

COUNTRIES = [
    "India", "Australia", "England", "Pakistan",
    "Bangladesh", "South Africa", "Sri Lanka", "New Zealand"
]


def load_data() -> pd.DataFrame:
    base_path = os.path.dirname(os.path.abspath(__file__))
    possible_paths = [
        os.path.join(base_path, "data", CSV_FILENAME),
        os.path.join(base_path, "..", "data", CSV_FILENAME),
        os.path.join(os.getcwd(), "data", CSV_FILENAME),
        os.path.join(os.getcwd(), "backend", "data", CSV_FILENAME),
    ]
    for path in possible_paths:
        norm = os.path.normpath(path)
        if os.path.exists(norm):
            df = pd.read_csv(norm)
            df = df.rename(columns={
                "Player Name"     : "player_name",
                "Country"         : "country",
                "Role"            : "role",
                "Batting Position": "position",
                "Total Matches"   : "total_matches",
                "Innings Played"  : "innings_played",
                "Runs"            : "runs",
                "Bat Avg"         : "bat_avg",
                "Strike Rate"     : "bat_sr",
                "Runs Conceded"   : "runs_conceded",
                "Wickets"         : "wickets",
                "Bowling Avg"     : "bowl_avg",
                "Bowling SR"      : "bowl_sr",
            })
            df["country"]  = df["country"].astype(str).str.strip().str.lower()
            df["role"]     = df["role"].astype(str).str.strip().str.lower()
            df["position"] = df["position"].astype(str).str.strip().str.lower()

            for col in ["runs", "wickets", "bat_avg", "bat_sr",
                        "bowl_avg", "bowl_sr", "total_matches", "innings_played"]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

            print(f"[load_data] Loaded: {norm}")
            return df

    raise FileNotFoundError(
        f"{CSV_FILENAME} not found. Tried:\n" +
        "\n".join(os.path.normpath(p) for p in possible_paths)
    )


def get_stat(row: dict, keys: list):
    for k in keys:
        val = row.get(k, 0)
        try:
            fval = float(val)
            if pd.notna(fval) and fval != 0:
                return fval
        except (TypeError, ValueError):
            pass
    return 0.0


def _score_batter(row: dict, pitch: str, avg_score: int) -> float:
    runs = float(row.get("runs", 0))
    avg  = float(row.get("bat_avg", 0)) or 1.0
    sr   = float(row.get("bat_sr", 0)) or 70.0
    if pitch == "pace" or avg_score >= 290:
        return (runs * 0.5) + (sr * 2.5) + (avg * 1.5)
    elif pitch == "spin":
        return (runs * 0.5) + (avg * 3.0) + (sr * 1.0)
    return (runs * 0.5) + (avg * 2.0) + (sr * 2.0)


def _score_bowler(row: dict, pitch: str) -> float:
    wickets = float(row.get("wickets", 0))
    bowl_sr = float(row.get("bowl_sr", 0)) or 40.0
    bowl_avg= float(row.get("bowl_avg", 0)) or 30.0
    is_pace = bowl_sr < 35
    is_spin = bowl_sr >= 35
    base = wickets / (bowl_avg if bowl_avg > 0 else 30)
    if   pitch == "pace" and is_pace: base *= 1.35
    elif pitch == "spin" and is_spin: base *= 1.35
    elif pitch == "pace" and is_spin: base *= 0.80
    elif pitch == "spin" and is_pace: base *= 0.80
    return base


def select_team(country: str, venue: str = "", pitch: str = "pace"):
    try:
        df = load_data()

        if venue and venue in VENUES:
            pitch = VENUES[venue].get("pitch", pitch)
        pitch = pitch or "pace"

        v_info    = VENUES.get(venue, {})
        avg_score = v_info.get("avg_score", 275)
        dew       = v_info.get("dew", False)

        country_key = country.strip().lower()
        df = df[df["country"] == country_key].copy()

        print(f"[select_team] country='{country_key}' pitch='{pitch}' rows={len(df)}")
        if df.empty:
            return pd.DataFrame(), None, {}

        df["_bat_score"]  = df.apply(lambda r: _score_batter(r.to_dict(), pitch, avg_score), axis=1)
        df["_bowl_score"] = df.apply(lambda r: _score_bowler(r.to_dict(), pitch), axis=1)

        used: set = set()

        def pick(pool: pd.DataFrame, n: int) -> list:
            rows = []
            for _, r in pool.iterrows():
                if r["player_name"] in used:
                    continue
                used.add(r["player_name"])
                rows.append(r.to_dict())
                if len(rows) == n:
                    break
            return rows

        def remaining():
            return df[~df["player_name"].isin(used)].copy()

        # SLOT 1-2: Openers
        openers = pick(df[df["position"] == POS_OPENER].sort_values("_bat_score", ascending=False), 2)
        if len(openers) < 2:
            fb = remaining()
            fb = fb[fb["role"].isin([ROLE_BATTER, ROLE_ALLROUNDER])]
            openers += pick(fb.sort_values("_bat_score", ascending=False), 2 - len(openers))

        # SLOT 3-5: Middle order (batter + allrounder, no WK)
        middle = pick(
            df[(df["position"] == POS_MIDDLE) & (df["role"].isin([ROLE_BATTER, ROLE_ALLROUNDER]))]
              .sort_values("_bat_score", ascending=False), 3
        )
        if len(middle) < 3:
            fb = remaining()
            fb = fb[fb["role"].isin([ROLE_BATTER, ROLE_ALLROUNDER])]
            middle += pick(fb.sort_values("_bat_score", ascending=False), 3 - len(middle))

        # SLOT 6: Wicketkeeper
        wk = pick(df[df["role"] == ROLE_WK].sort_values("_bat_score", ascending=False), 1)
        if not wk:
            fb = remaining()
            wk = pick(fb[fb["role"] == ROLE_BATTER].sort_values("runs", ascending=False), 1)

        # SLOT 7-8: Lower order allrounders
        lower = pick(
            df[(df["position"] == POS_LOWER) & (df["role"] == ROLE_ALLROUNDER)]
              .sort_values(["_bowl_score", "_bat_score"], ascending=[False, False]), 2
        )
        if len(lower) < 2:
            lower += pick(df[df["position"] == POS_LOWER]
                          .sort_values(["_bowl_score", "_bat_score"], ascending=[False, False]),
                          2 - len(lower))
        if len(lower) < 2:
            fb = remaining()
            lower += pick(fb[fb["role"] == ROLE_ALLROUNDER]
                          .sort_values("_bowl_score", ascending=False), 2 - len(lower))
        if len(lower) < 2:
            lower += pick(remaining().sort_values("_bat_score", ascending=False), 2 - len(lower))

        # SLOT 9-11: Bowlers (pitch-split)
        pace_pool = df[(df["role"] == ROLE_BOWLER) & (df["bowl_sr"] > 0) & (df["bowl_sr"] < 35)].sort_values("_bowl_score", ascending=False)
        spin_pool = df[(df["role"] == ROLE_BOWLER) & (df["bowl_sr"] >= 35)].sort_values("_bowl_score", ascending=False)
        all_bowl  = df[df["role"] == ROLE_BOWLER].sort_values("_bowl_score", ascending=False)

        if pitch == "spin":
            bowlers  = pick(spin_pool, 2); bowlers += pick(pace_pool, 1)
        else:
            bowlers  = pick(pace_pool, 2); bowlers += pick(spin_pool, 1)
        if len(bowlers) < 3:
            bowlers += pick(all_bowl, 3 - len(bowlers))

        # Combine in strict slot order
        all_slots = openers + middle + wk + lower + bowlers

        # Fill to 11
        if len(all_slots) < 11:
            fb = remaining()
            all_slots += pick(fb[fb["role"] == ROLE_ALLROUNDER].sort_values("_bowl_score", ascending=False), 11 - len(all_slots))
        if len(all_slots) < 11:
            all_slots += pick(remaining().sort_values("_bat_score", ascending=False), 11 - len(all_slots))
        if len(all_slots) < 11:
            all_slots += pick(remaining().sort_values("wickets", ascending=False), 11 - len(all_slots))

        team = pd.DataFrame(all_slots)
        for c in ["_bat_score", "_bowl_score"]:
            if c in team.columns:
                team.drop(columns=[c], inplace=True)
        team = team.reset_index(drop=True)

        captain = team.sort_values(["runs", "wickets"], ascending=[False, False]).iloc[0]["player_name"]

        meta = {
            "pitch"     : pitch,
            "avg_score" : avg_score,
            "dew"       : dew,
            "venue_desc": v_info.get("desc", ""),
        }
        return team, captain, meta

    except FileNotFoundError as e:
        print(f"[FILE ERROR] {e}")
        return pd.DataFrame(), None, {}
    except Exception as e:
        import traceback; traceback.print_exc()
        return pd.DataFrame(), None, {}


def generate_insights(team: pd.DataFrame, venue: str = "",
                      pitch: str = "", meta: dict = None) -> dict:
    if meta is None:
        meta = {}
    empty = {k: [] for k in ["batting", "bowling", "team", "venue", "strategy"]}
    if team is None or team.empty:
        return empty
    try:
        avg_score  = meta.get("avg_score", 275)
        dew        = meta.get("dew", False)
        pitch      = meta.get("pitch", pitch) or "pace"
        venue_desc = meta.get("venue_desc", "")

        allrounders = team[team["role"] == ROLE_ALLROUNDER]
        bowlers_df  = team[team["role"] == ROLE_BOWLER]
        all_bowl    = pd.concat([bowlers_df, allrounders])

        # BATTING
        top_bat  = team.sort_values("runs", ascending=False).iloc[0]
        high_sr  = team.sort_values("bat_sr", ascending=False).iloc[0]
        openers  = team[team["position"] == POS_OPENER]
        qual_bat = team[team["bat_avg"] > 25]

        bat = [
            f"🏆 **{top_bat['player_name']}** leads batting with **{int(top_bat['runs'])} runs** "
            f"at avg **{round(top_bat['bat_avg'],2)}**, SR **{round(top_bat['bat_sr'],2)}**.",
            f"💥 **{high_sr['player_name']}** is the impact player with SR **{round(high_sr['bat_sr'],2)}** — "
            f"a game-changer in the final overs.",
            f"📊 **{len(qual_bat)} players** average above 25, giving excellent batting depth.",
        ]
        if not openers.empty:
            op_names = " & ".join(openers["player_name"].tolist())
            op_sr    = round(openers["bat_sr"].mean(), 2)
            bat.append(f"⚡ Openers **{op_names}** avg SR of **{op_sr}** — "
                       + ("ideal for exploiting powerplay on pace surface." if pitch=="pace"
                          else "key to negotiating new ball before spinners dominate."))

        # BOWLING
        top_wkt = team.sort_values("wickets", ascending=False).iloc[0]
        pace_b  = all_bowl[all_bowl["bowl_sr"] < 35]
        spin_b  = all_bowl[all_bowl["bowl_sr"] >= 35]

        bowl = [
            f"🎯 **{top_wkt['player_name']}** leads bowling with **{int(top_wkt['wickets'])} wickets** "
            f"at avg **{round(top_wkt['bowl_avg'],2)}**, SR **{round(top_wkt['bowl_sr'],2)}**.",
            f"⚖️ Attack balance: **{len(pace_b)} pace / {len(spin_b)} spin** — "
            + (f"optimised for pace conditions." if pitch=="pace" else
               f"optimised for spin conditions." if pitch=="spin" else "well balanced."),
        ]

        # TEAM
        wk_row = team[team["role"] == ROLE_WK]
        team_i = []
        if not allrounders.empty:
            ar_names = ", ".join(allrounders["player_name"].tolist())
            team_i.append(
                f"🔁 All-rounders **{ar_names}** contribute "
                f"**{int(allrounders['runs'].sum())} runs** and **{int(allrounders['wickets'].sum())} wickets**."
            )
        if not wk_row.empty:
            w = wk_row.iloc[0]
            team_i.append(
                f"🧤 Wicketkeeper **{w['player_name']}** averages **{round(w['bat_avg'],2)}** "
                f"at SR **{round(w['bat_sr'],2)}**."
            )
        team_i.append(
            f"💪 **{len(team[team['wickets']>20])} players** in the XI have taken 20+ ODI wickets."
        )

        # VENUE
        ven = []
        if venue:   ven.append(f"🏟️ **{venue}**")
        if venue_desc: ven.append(f"📋 {venue_desc}")
        if avg_score:
            chase_par = avg_score + (15 if dew else 0)
            ven.append(f"📈 Avg 1st innings: **{avg_score}**. "
                       + (f"Dew expected — chasing **{chase_par}+** is viable." if dew
                          else f"Posting **{avg_score-10}+** is a defendable total."))
        if dew:
            ven.append("💧 **Dew factor** significant — consider **bowling first** if toss is won.")
        ven.append({"pace": "🏃 Pace-friendly — pacers will find seam and swing early.",
                    "spin": "🌀 Spin-friendly — ball grips and turns from early on.",
                    "balanced": "⚖️ Balanced — early seam gives way to spin in middle overs."
                    }.get(pitch, ""))

        # STRATEGY
        strat = [
            f"🎯 **Powerplay**: " + ("Target top-order wickets with new-ball pacers overs 1-10."
                                      if pitch in ("pace","balanced")
                                      else "Contain in PP — spinners tighten from over 6."),
            f"🔄 **Middle overs (11-40)**: " + ("Build partnerships, capitalise on batting PP."
                                                  if pitch == "pace"
                                                  else "Rotate strike; target spinners with sweep and slog-sweep."),
            f"💣 **Death overs (41-50)**: Aim for "
            + (f"90+ in last 10 overs on this high-scoring ground." if avg_score >= 290
               else "70-80 in last 10 overs is par on this slower ground."),
            "💧 **Toss**: Bowl first — dew will assist the batting side later." if dew
            else "🌤️ **Toss**: Bat first — put a total on the board and let the pitch deteriorate.",
        ]

        return {"batting": bat, "bowling": bowl, "team": team_i, "venue": ven, "strategy": strat}

    except Exception as e:
        import traceback; traceback.print_exc()
        return {k: [f"Error: {e}"] for k in ["batting","bowling","team","venue","strategy"]}