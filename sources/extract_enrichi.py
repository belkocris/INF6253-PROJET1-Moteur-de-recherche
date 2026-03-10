from bs4 import BeautifulSoup
from pathlib import Path


# ============================================================
#  UTILITAIRES
# ============================================================

def load_html(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def get_soup_from_file(path: str) -> BeautifulSoup:
    html = load_html(path)
    return BeautifulSoup(html, "html.parser")


# ============================================================
#  PARSING CLASSEMENT
# ============================================================

def parse_classement(path: str):
    soup = get_soup_from_file(path)
    teams = []

    for row in soup.find_all(attrs={"typeof": "SportsTeam"}):

        def get_int(prop):
            cell = row.find(attrs={"property": prop})
            if not cell:
                return None
            txt = cell.get_text(strip=True).replace("+", "")
            try:
                return int(txt)
            except:
                return None

        name_cell = row.find(attrs={"property": "name"})
        if name_cell:
            link = name_cell.find("a")
            if link:
                name = link.get_text(strip=True)
                url = link.get("href")
            else:
                name = name_cell.get_text(strip=True)
                url = None
        else:
            name = None
            url = None

        teams.append({
            "position": get_int("position"),
            "name": name,
            "url": url,
            "points": get_int("points"),
            "gamesPlayed": get_int("gamesPlayed"),
            "wins": get_int("wins"),
            "draws": get_int("draws"),
            "losses": get_int("losses"),
            "goalsScored": get_int("goalsScored"),
            "goalsConceded": get_int("goalsConceded"),
            "goalDifference": get_int("goalDifference"),
        })

    return teams


# ============================================================
#  PARSING CALENDRIER
# ============================================================

def parse_calendrier(path: str):
    soup = get_soup_from_file(path)
    matches = []

    for row in soup.find_all(attrs={"typeof": "SportsEvent"}):
        date = row.find(attrs={"property": "startDate"}).get_text(strip=True)
        home = row.find(attrs={"property": "homeTeam"}).get_text(strip=True)
        away = row.find(attrs={"property": "awayTeam"}).get_text(strip=True)
        score = row.find(attrs={"property": "score"}).get_text(strip=True)

        hg, ag = None, None
        if "-" in score:
            parts = score.split("-")
            try:
                hg = int(parts[0].strip())
                ag = int(parts[1].strip())
            except:
                pass

        matches.append({
            "date": date,
            "homeTeam": home,
            "awayTeam": away,
            "score": score,
            "homeGoals": hg,
            "awayGoals": ag,
        })

    return matches


# ============================================================
#  PARSING STATISTIQUES
# ============================================================

def parse_statistiques(path: str):
    soup = get_soup_from_file(path)
    stats = {}

    boxes = soup.find_all("div", attrs={"typeof": "SportsOrganization"})

    for box in boxes:
        title = box.find("h3").get_text(strip=True)

        if "générales" in title.lower():
            games = int(box.find(attrs={"property": "numberOfGames"}).get_text(strip=True))
            ps = box.find_all("p")
            total_goals = int(ps[1].get_text(strip=True).split(":")[1])
            avg = float(ps[2].get_text(strip=True).split(":")[1])
            stats["general"] = {
                "numberOfGames": games,
                "totalGoals": total_goals,
                "goalsPerGame": avg
            }

    return stats


# ============================================================
#  R1 : Équipe première au classement
# ============================================================

def extract_R1(classement_path: str):
    teams = parse_classement(classement_path)
    first = min(teams, key=lambda t: t["position"])

    return f"""
    <h2>R1 — Équipe première au classement</h2>
    <p><strong>{first['name']}</strong> est première avec <strong>{first['points']} points</strong>.</p>
    """


# ============================================================
#  R2 : Nombre total de matchs joués
# ============================================================

def extract_R2(statistiques_path: str):
    stats = parse_statistiques(statistiques_path)
    n = stats["general"]["numberOfGames"]

    return f"""
    <h2>R2 — Nombre total de matchs joués</h2>
    <p>Il y a eu <strong>{n}</strong> matchs joués cette saison.</p>
    """


# ============================================================
#  R3 : Nombre total de buts marqués
# ============================================================

def extract_R3(statistiques_path: str):
    stats = parse_statistiques(statistiques_path)
    total = stats["general"]["totalGoals"]

    return f"""
    <h2>R3 — Nombre total de buts marqués</h2>
    <p>Un total de <strong>{total}</strong> buts ont été marqués cette saison.</p>
    """


# ============================================================
#  R4 : Équipe ayant marqué le plus de buts
# ============================================================

def extract_R4(classement_path: str):
    teams = parse_classement(classement_path)
    best = max(teams, key=lambda t: t["goalsScored"])

    return f"""
    <h2>R4 — Meilleure attaque</h2>
    <p>L'équipe ayant marqué le plus de buts est <strong>{best['name']}</strong> avec 
    <strong>{best['goalsScored']} buts</strong>.</p>
    """


# ============================================================
#  R5 : Équipes ayant marqué plus de 70 buts
# ============================================================

def extract_R5(classement_path: str):
    teams = parse_classement(classement_path)
    filtered = [t for t in teams if t["goalsScored"] > 70]

    html = "<ul>"
    for t in filtered:
        html += f"<li>{t['name']} — {t['goalsScored']} buts</li>"
    html += "</ul>"

    return f"""
    <h2>R5 — Équipes ayant marqué plus de 70 buts</h2>
    {html}
    """


# ============================================================
#  R6 : Matchs de novembre 2008 + liste complète
# ============================================================

def extract_R6(calendrier_path: str):
    matches = parse_calendrier(calendrier_path)
    nov = [m for m in matches if m["date"].split("/")[1] == "11" and m["date"].split("/")[2] == "2008"]

    html = "<ul>"
    for m in nov:
        html += f"<li>{m['date']} — {m['homeTeam']} {m['score']} {m['awayTeam']}</li>"
    html += "</ul>"

    return f"""
    <h2>R6 — Matchs de novembre 2008</h2>
    <p>Nombre de matchs : <strong>{len(nov)}</strong></p>
    {html}
    """


# ============================================================
#  R7 : Victoires à domicile de Manchester United + liste
# ============================================================

def extract_R7(calendrier_path: str):
    matches = parse_calendrier(calendrier_path)
    wins = [
        m for m in matches
        if m["homeTeam"] == "Manchester United" and m["homeGoals"] > m["awayGoals"]
    ]

    html = "<ul>"
    for m in wins:
        html += f"<li>{m['date']} — {m['homeTeam']} {m['score']} {m['awayTeam']}</li>"
    html += "</ul>"

    return f"""
    <h2>R7 — Victoires à domicile de Manchester United</h2>
    <p>Total : <strong>{len(wins)}</strong> victoires</p>
    {html}
    """


# ============================================================
#  R8 : Classement des équipes par victoires à l’extérieur
# ============================================================

def extract_R8(calendrier_path: str):
    matches = parse_calendrier(calendrier_path)
    away_wins = {}

    for m in matches:
        if m["awayGoals"] > m["homeGoals"]:
            away_wins[m["awayTeam"]] = away_wins.get(m["awayTeam"], 0) + 1

    ranking = sorted(away_wins.items(), key=lambda x: x[1], reverse=True)

    html = "<ol>"
    for team, wins in ranking:
        html += f"<li>{team} — {wins} victoires</li>"
    html += "</ol>"

    return f"""
    <h2>R8 — Classement des équipes par victoires à l’extérieur</h2>
    {html}
    """


# ============================================================
#  R9 : Top 6 + moyenne buts marqués à l’extérieur
# ============================================================

def extract_R9(classement_path: str, calendrier_path: str):
    teams = parse_classement(classement_path)
    top6 = [t["name"] for t in sorted(teams, key=lambda t: t["position"])[:6]]

    matches = parse_calendrier(calendrier_path)

    total_goals = 0
    total_matches = 0

    for m in matches:
        if m["awayTeam"] in top6:
            total_goals += m["awayGoals"]
            total_matches += 1

    avg = total_goals / total_matches if total_matches else 0

    html_top6 = "<ul>"
    for t in top6:
        html_top6 += f"<li>{t}</li>"
    html_top6 += "</ul>"

    return f"""
    <h2>R9 — Moyenne de buts marqués à l’extérieur par le Top 6</h2>
    <h3>Équipes du Top 6</h3>
    {html_top6}
    Total de buts marqués à l’extérieur : <strong>{total_goals}</strong><br> 
    Nombre total de matchs à l’extérieur : <strong>{total_matches}</strong><br>
    <p>Moyenne de buts marqués à l’extérieur : <strong>{avg:.2f}</strong></p>
    """


# ============================================================
#  R10 : Confrontations entre 1er et 3e
# ============================================================

def extract_R10(classement_path: str, calendrier_path: str):
    teams = parse_classement(classement_path)
    sorted_teams = sorted(teams, key=lambda t: t["position"])

    first = sorted_teams[0]["name"]
    third = sorted_teams[2]["name"]

    matches = parse_calendrier(calendrier_path)

    confrontations = [
        m for m in matches
        if {m["homeTeam"], m["awayTeam"]} == {first, third}
    ]

    html = "<ul>"
    for m in confrontations:
        html += f"<li>{m['date']} — <strong>{m['homeTeam']}</strong> {m['score']} <strong>{m['awayTeam']}</strong></li>"
    html += "</ul>"

    return f"""
    <h2>R10 — Confrontations entre {first} et {third}</h2>
    {html}
    """

#===================================================================================================================
#           TEST DES FICHIERS ENRICHIS AVEC RDFa ET RÉSULTATS DES REQUÊTES DE R1-R10
#===================================================================================================================


#print(extract_R1("../pages_html_enrichies/classement_enrichi.html"))
#print(extract_R2("../pages_html_enrichies/statistiques_enrichi.html"))
#print(extract_R3("../pages_html_enrichies/statistiques_enrichi.html"))
#print(extract_R4("../pages_html_enrichies/classement_enrichi.html"))
#print(extract_R5("../pages_html_enrichies/classement_enrichi.html"))
#print(extract_R6("../pages_html_enrichies/calendrier_enrichi.html"))
#print(extract_R7("../pages_html_enrichies/calendrier_enrichi.html"))
#print(extract_R8("../pages_html_enrichies/calendrier_enrichi.html"))
#print(extract_R9("../pages_html_enrichies/classement_enrichi.html", "../pages_html_enrichies/calendrier_enrichi.html"))
#print(extract_R10("../pages_html_enrichies/classement_enrichi.html", "../pages_html_enrichies/calendrier_enrichi.html"))