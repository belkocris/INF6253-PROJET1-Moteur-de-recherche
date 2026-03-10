from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import time

#import backend_non_enrichi as old
#import backend_rdfa as rdfa

# --- Import des deux backends ---
from sources.extract import (extract_r1, extract_r2, extract_r4, extract_r5, extract_r6, extract_r7,
                             extract_r8, extract_r9, extract_r10)
from sources.extract_enrichi import (extract_R1, extract_R2, extract_R3, extract_R4, extract_R5, extract_R6,
                            extract_R7, extract_R8, extract_R9, extract_R10)
from sources.extract_sparql import execute_r_query


# ton ancien backend utilisait extract_r2 pour R2 et R3
OLD_FUNCTIONS = {
    "R1": extract_r1,
    "R2": extract_r2,
    "R3": extract_r2,
    "R4": extract_r4,
    "R5": extract_r5,
    "R6": extract_r6,
    "R7": extract_r7,
    "R8": extract_r8,
    "R9": extract_r9,
    "R10": extract_r10
}

# Backend RDFa
RDFA_FUNCTIONS = {
    "R1": extract_R1,
    "R2": extract_R2,
    "R3": extract_R3,
    "R4": extract_R4,
    "R5": extract_R5,
    "R6": extract_R6,
    "R7": extract_R7,
    "R8": extract_R8,
    "R9": extract_R9,
    "R10": extract_R10
}

# Backend SparQL
SPARQL_FUNCTIONS = {
    "R1": lambda: execute_r_query("R1"),
    "R2": lambda: execute_r_query("R2"),
    "R3": lambda: execute_r_query("R3"),
    "R4": lambda: execute_r_query("R4"),
    "R5": lambda: execute_r_query("R5"),
    "R6": lambda: execute_r_query("R6"),
    "R7": lambda: execute_r7_sparql(),
    "R8": lambda: execute_r_query("R8"),
    "R9": lambda: execute_r_query("R9"),
    "R10": lambda: execute_r_query("R10")
}

def sparql_json_to_html_table(data):
    head = data.get("head", {}).get("vars", [])
    rows = data.get("results", {}).get("bindings", [])

    if not rows:
        return "<p>Aucun résultat.</p>"

    # On laisse le CSS gérer les couleurs, arrondis, hover, etc.
    html = "<table class='sparql-table compact'>"


    # En-tête
    html += "<tr>"
    for col in head:
        html += f"<th data-col='{col}'>{col}</th>"
    html += "</tr>"

    # Lignes
    for row in rows:
        html += "<tr>"
        for col in head:
            value = row.get(col, {}).get("value", "")
            html += f"<td>{value}</td>"
        html += "</tr>"

    html += "</table>"
    return html


def execute_r7_sparql():
    # 1) Exécuter la liste des matchs
    results_r7 = execute_r_query("R7")

    # 2) Exécuter le total
    results_r7bis = execute_r_query("R7bis")

    # Sécurité : si pas de résultats
    if "results" not in results_r7 or "results" not in results_r7bis:
        return {
            "head": {"vars": ["error"]},
            "results": {"bindings": [
                {"error": {"value": "Erreur SPARQL dans R7 ou R7bis."}}
            ]}
        }

    # 3) On renvoie un JSON combiné
    return {
        "matches": results_r7,
        "count": results_r7bis
    }


def execute_r10_sparql():
    # 1) Exécuter R10a
    results_r10a = execute_r_query("R10a")

    # Vérification de sécurité
    if "results" not in results_r10a:
        return {"head": {"vars": ["error"]},
                "results": {"bindings": [{"error": {"value": "Erreur SPARQL dans R10a"}}]}}

    ranking = results_r10a["results"]["bindings"]

    if len(ranking) < 3:
        return {"head": {"vars": ["error"]},
                "results": {"bindings": [{"error": {"value": "Pas assez d'équipes pour déterminer un 1er et un 3e."}}]}}

    # 2) Extraire le 1er et le 3e
    team1 = ranking[0]["teamName"]["value"]
    team3 = ranking[2]["teamName"]["value"]

    # 3) Construire la requête R10b
    query_r10b = f'''
    PREFIX schema: <http://schema.org/>

    SELECT ?date ?homeName ?awayName ?score
    WHERE {{
      ?event a schema:SportsEvent ;
             schema:homeTeam ?home ;
             schema:awayTeam ?away ;
             schema:score ?score ;
             schema:startDate ?date .

      ?home schema:name ?homeName .
      ?away schema:name ?awayName .

      FILTER(
        (?homeName = "{team1}" && ?awayName = "{team3}") ||
        (?homeName = "{team3}" && ?awayName = "{team1}")
      )
    }}
    ORDER BY ?date
    '''

    # 4) Exécuter R10b
    results_r10b = execute_r_query(query_r10b, raw_query=True)

    return results_r10b


app = Flask(__name__)
CORS(app)
FUSEKI_URL = "http://localhost:3030/#/dataset/premierLeague/query"

@app.route("/")
def home():
    return render_template("search.html")

@app.route("/search", methods=["POST"])
def search():
    data = request.get_json()
    query = data.get("query", "").strip()
    engine = data.get("engine", "RDFa")

    start = time.time()

    # Normalisation : on extrait le numéro R1, R2, etc.
    mapping_index = {
        "Quelle équipe est première au classement ?": "R1",
        "Combien de matchs ont été joués cette saison ?": "R2",
        "Quel est le nombre total de buts marqués cette saison ?": "R3",
        "Quelle équipe a marqué le plus de buts ?": "R4",
        "Quelles équipes ont marqué plus de 70 buts cette saison ?": "R5",
        "Quels matchs ont eu lieu en novembre 2008 ?": "R6",
        "Combien de victoires à domicile pour Manchester United ?": "R7",
        "Classement des équipes par victoires à l’extérieur": "R8",
        "Moyenne de buts marqués à l’extérieur par le Top 6": "R9",
        "Confrontations historiques entre le 1er et le 3e": "R10",
    }

    if query not in mapping_index:
        return jsonify({"result": "<p>Requête inconnue.</p>", "time": 0, "diff": ""})

    R = mapping_index[query]

    # Sélection du moteur

    if engine == "OLD":
        func = OLD_FUNCTIONS[R]

        # Détermination automatique des fichiers nécessaires
        if R in ["R1", "R5"]:
            result_html = func("classement.html")
        elif R in ["R2"]:
            result_html = func("statistiques.html", 1)
        elif R in ["R3"]:
            result_html = func("statistiques.html", 2)
        elif R in ["R4"]:
            result_html = func("statistiques.html")
        elif R in ["R6", "R7", "R8", "R9"]:
            result_html = func("calendrier.html")
        else:  # R10
            result_html = func("classement.html", "calendrier.html")

    elif engine == "RDFa":

        func = RDFA_FUNCTIONS[R]

        result_html = func("pages_html_enrichies/classement_enrichi.html") if R in ["R1", "R4", "R5"] else \
            func("pages_html_enrichies/statistiques_enrichi.html") if R in ["R2", "R3"] else \
                func("pages_html_enrichies/calendrier_enrichi.html") if R in ["R6", "R7", "R8"] else \
                    func("pages_html_enrichies/classement_enrichi.html", "pages_html_enrichies/calendrier_enrichi.html")

    else:

        func = SPARQL_FUNCTIONS[R]

        # Exécute execute_r_query("R1"....."R10")
        result_json = func()

        # Cas spécial R7 (2 résultats)
        if R == "R7":
            table_html = sparql_json_to_html_table(result_json["matches"])
            total = result_json["count"]["results"]["bindings"][0][".1"]["value"]

            result_html = f""" 
                <h3>Victoires à domicile de Manchester United</h3> 
                {table_html} 
                <p><strong>Total :</strong> {total}</p> 
            """
        else:
            # On convertit le JSON SPARQL en HTML lisible
            result_html = sparql_json_to_html_table(result_json)


        #result_html = sparql_json_to_html_table(result_json)

    # Résumé des différences
    #diff_html = """

    #"""

    end = time.time()

    return jsonify({
        "result": result_html,
        "time": int((end - start) * 1000)
    })


if __name__ == "__main__":
    app.run(debug=True)
