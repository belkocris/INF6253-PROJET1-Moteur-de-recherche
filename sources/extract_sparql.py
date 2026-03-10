import requests

# ---------------------------------------------------------
# Configuration Fuseki
# ---------------------------------------------------------

FUSEKI_URL = "http://localhost:3030/premierLeague/sparql"

def run_sparql(query: str):
    """Envoie une requête SPARQL à Fuseki et renvoie le JSON."""
    response = requests.post(
        FUSEKI_URL,
        data={"query": query},
        headers={"Accept": "application/sparql-results+json"}
    )
    response.raise_for_status()
    return response.json()

# ---------------------------------------------------------
# Requêtes SPARQL R1 à R10
# ---------------------------------------------------------

R_QUERIES = {

    # R1 — Équipe première au classement
    "R1": """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX schema: <http://schema.org/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?teamName ?points WHERE {
  ?team a schema:SportsTeam ;
        schema:name ?teamName ;
        schema:position ?pos ;
        schema:points ?points .
}
ORDER BY ASC(xsd:integer(?pos))
LIMIT 1
""",

    # R2 — Nombre total de matchs
    "R2": """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX schema: <http://schema.org/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT (COUNT(?match) AS ?nbMatchs) WHERE {
  ?match a schema:SportsEvent .
}
""",

    # R3 — Liste des équipes + points
    "R3": """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX schema: <http://schema.org/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT (SUM(?homeGoals) + SUM(?awayGoals) AS ?totalGoals)
WHERE {
  ?event a schema:SportsEvent ;
         schema:score ?score .

  # Extraire les buts à domicile et à l'extérieur
  BIND(STRBEFORE(?score, " - ") AS ?homeStr)
  BIND(STRAFTER(?score, " - ") AS ?awayStr)

  # Convertir en entiers
  BIND(xsd:integer(?homeStr) AS ?homeGoals)
  BIND(xsd:integer(?awayStr) AS ?awayGoals)
}
""",

    # R4 — Classement complet
    "R4": """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX schema: <http://schema.org/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?name ?maxGoalsScored
WHERE {
  ?pdt schema:goalsScored ?goalsScored .
  ?pdt schema:name ?name

  {
    SELECT (MAX(xsd:integer(?goalsScored)) AS ?maxGoalsScored)
    WHERE {
      ?y schema:goalsScored ?goalsScored .
    }
  }
  FILTER(xsd:integer(?goalsScored) = ?maxGoalsScored)
}
""",

    # R5 — Matchs d’une équipe donnée (ex: Arsenal)
    "R5": """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX schema: <http://schema.org/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?name ?goalsScored
    WHERE {
    ?pdt schema:goalsScored ?goalsScored .
    ?pdt schema:name ?name
    FILTER(xsd:integer(?goalsScored) > 70)
}
""",

    # R6 — Matchs joués en novembre 2008
    "R6": """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX schema: <http://schema.org/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?date ?homeName ?awayName ?score WHERE {
  ?match a schema:SportsEvent ;
         schema:homeTeam ?home ;
         schema:awayTeam ?away ;
         schema:score ?score .

  OPTIONAL { ?match schema:startDate ?date }

  ?home schema:name ?homeName .
  ?away schema:name ?awayName .

  FILTER(BOUND(?date))
  FILTER(CONTAINS(STR(?date), "/11/2008"))
}
ORDER BY ?date
""",

    # R7 — Moyenne des buts marqués (si disponible)
    "R7": """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX schema: <http://schema.org/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?date ?homeName ?awayName ?score
WHERE {
  ?event a schema:SportsEvent ;
         schema:homeTeam ?home ;
         schema:awayTeam ?away ;
         schema:score ?score ;
         schema:startDate ?date .

  ?home schema:name ?homeName .
  ?away schema:name ?awayName .

  # On ne garde que les matchs où MU est à domicile
  FILTER(?homeName = "Manchester United")

  # Extraction des buts
  BIND(STRBEFORE(?score, " - ") AS ?homeStr)
  BIND(STRAFTER(?score, " - ") AS ?awayStr)

  BIND(xsd:integer(?homeStr) AS ?homeGoals)
  BIND(xsd:integer(?awayStr) AS ?awayGoals)

  # Victoire à domicile
  FILTER(?homeGoals > ?awayGoals)
}
ORDER BY ?date
""",

# R7 — Moyenne des buts marqués (si disponible)
    "R7bis": """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX schema: <http://schema.org/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT COUNT(?event)
WHERE {
  ?event a schema:SportsEvent ;
         schema:homeTeam ?home ;
         schema:awayTeam ?away ;
         schema:score ?score ;
         schema:startDate ?date .

  ?home schema:name ?homeName .
  ?away schema:name ?awayName .

  FILTER(?homeName = "Manchester United")

  BIND(STRBEFORE(?score, " - ") AS ?homeStr)
  BIND(STRAFTER(?score, " - ") AS ?awayStr)

  BIND(xsd:integer(?homeStr) AS ?homeGoals)
  BIND(xsd:integer(?awayStr) AS ?awayGoals)

  FILTER(?homeGoals > ?awayGoals)
}
""",

    # R8 — Matchs gagnés à domicile
    "R8": """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX schema: <http://schema.org/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?teamName COUNT(?event)
WHERE {
  ?event a schema:SportsEvent ;
         schema:homeTeam ?home ;
         schema:awayTeam ?away ;
         schema:score ?score .

  ?away schema:name ?teamName .

  # Extraction des buts
  BIND(STRBEFORE(?score, " - ") AS ?homeStr)
  BIND(STRAFTER(?score, " - ") AS ?awayStr)

  BIND(xsd:integer(?homeStr) AS ?homeGoals)
  BIND(xsd:integer(?awayStr) AS ?awayGoals)

  # Victoire à l'extérieur
  FILTER(?awayGoals > ?homeGoals)
}
GROUP BY ?teamName
ORDER BY DESC(COUNT(?event))
""",

    # R9 — Matchs gagnés à l’extérieur
    "R9": """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX schema: <http://schema.org/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT (xsd:decimal(ROUND(AVG(xsd:decimal(?awayGoals)) * 100) / 100) AS ?avg)
WHERE {
  ?event a schema:SportsEvent ;
         schema:awayTeam ?awayTeam ;
         schema:score ?score .
  ?standing a schema:SportsTeam ;
            schema:position ?pos ;
            schema:name ?name0 .
  ?awayTeam schema:name ?awayTeamName .

  FILTER(xsd:integer(?pos) <= 6 && ?awayTeamName = ?name0)

  BIND(xsd:integer(STRAFTER(str(?score), " - ")) AS ?awayGoals)
}
""",

    # R10 — Matchs nuls
    "R10": """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX schema: <http://schema.org/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT DISTINCT ?date ?homeName ?awayName ?score ?resultat
WHERE {
  ?event a schema:SportsEvent ;
         schema:startDate ?date ;
         schema:homeTeam ?homeTeamEvent ;
         schema:awayTeam ?awayTeamEvent ;
         schema:score ?score .
 
  ?homeTeamEvent schema:name ?homeName .
  ?awayTeamEvent schema:name ?awayName .
 
  ?homeTeam a schema:SportsTeam ;
            schema:name ?homeName ;
            schema:position ?homePos .
 
  ?awayTeam a schema:SportsTeam ;
            schema:name ?awayName ;
            schema:position ?awayPos .
 
  FILTER (
      (xsd:integer(?homePos) = 1 && xsd:integer(?awayPos) = 3)
   || (xsd:integer(?homePos) = 3 && xsd:integer(?awayPos) = 1)
  )

  BIND(xsd:integer(STRBEFORE(str(?score), " - ")) AS ?homeGoals)
  BIND(xsd:integer(STRAFTER(str(?score), " - ")) AS ?awayGoals)

  BIND(
    IF(?homeGoals > ?awayGoals, "Victoire : " + ?homeName,
      IF(?homeGoals < ?awayGoals, "Victoire : " + ?awayName,
        "Match nul"
      )
    ) AS ?resultat
  )
}
ORDER BY ?date
"""
}

# ---------------------------------------------------------
# Fonction principale appelée par ton app.py
# ---------------------------------------------------------

def execute_r_query(key_or_query, raw_query=False):
    if raw_query:
        query = key_or_query
    else:
        query = R_QUERIES[key_or_query]

    return run_sparql(query)
