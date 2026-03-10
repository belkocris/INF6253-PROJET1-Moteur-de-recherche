import time
from collections import defaultdict
from bs4 import BeautifulSoup


#========================================================================
# Cette fonction est globale
# Elle ouvre et parcours un fichier du dossier pages_html
# Si on exécution le fichier courant ajouter le chemin "../"
#========================================================================
def load_file(file_name):
    fichier = open("pages_html/"+file_name, "r", encoding="UTF-8")
    url = fichier.read()
    soup = BeautifulSoup(url, "html.parser")
    return soup


#========================================================================
# Cette fonction retourne l\'équipe qui est première
# au classement général, ainsi que le temps d\'execution
# de la requête. Elle prend en paramètre le fichier
# classement.html
#========================================================================
def extract_r1(file_name):

    # Lecture et parcours du fichier html
    soup = load_file(file_name)

    # On ne considère pas l\'entête du tableau
    r1 = soup.find('table').find_all('tr')[1]
    r1_team_name = r1.find_all('td')[1].text

    # Construction du résultat
    result_text = (
        f"Équipe première au classement : <strong>{r1_team_name}</strong><br>"
    )

    return result_text



#========================================================================
# Cette fonction retourne le nombre total de matchs joués
# durant toute la saison sportive, ainsi que le temps d\'exécution
# de la requête. Elle prend 2 paramètres : le fichier statistique.html
# r2_Or_r3 correspond à la question 2 ou 3. Si vous répondez à la
# Q2 initialisez r2_Or_r3 = 1. Si c'est la Q3 initialisez
# r2_Or_r3 = 2
#========================================================================
def extract_r2(file_name, r2_Or_r3):

    # Lecture et parcours du fichier html
    soup = load_file(file_name)
    r2 = soup.find_all('div')[1]

    # --------------------------------------------------
    # r2_Or_r3 = 1 → nombre de matchs joués
    # r2_Or_r3 = 2 → nombre total de buts
    # ---------------------------------------------------
    if r2_Or_r3 == 1:
        valeur = r2.find_all('p')[0].text.strip()
        titre = "Nombre total de matchs joués cette saison"
    elif r2_Or_r3 == 2:
        valeur = r2.find_all('p')[1].text.strip()
        titre = "Nombre total de buts marqués cette saison"
    else:
        return "Paramètre r2_Or_r3 invalide"

    # Construction du résultat HTML lisible
    result_text = (
        f"<h4>{titre}</h4>" 
        f"<strong>{valeur}</strong><br><br>"
    )

    return result_text



#===========================================================================
# Cette fonction retourne le nom de l\'équipe qui a marqué le plus
# de buts cette saison. Et temps d\'exécution de la requête.
# Elle prend en paramètre le fichier statistique.html
#============================================================================
def extract_r4(file_name):

    # Lecture et parcours du fichier html
    soup = load_file(file_name)
    r4 = soup.find_all('div')[2]

    # Extraction des données
    r4_team_name = r4.find_all('p')[0].text.strip()
    r4_team_goals = r4.find_all('p')[1].text.strip()

    # Construction du résultat HTML lisible
    result_text = (
        "<h4>Équipe ayant marqué le plus de buts</h4>" 
        f"<strong>{r4_team_name}</strong><br>" 
        f"<strong>{r4_team_goals}</strong>"
    )

    return result_text



#==============================================================================
# Cette fonction retourne les équipes qui ont marqué plus de 70 buts
# cette saison et le temps d\'exécution de la requête. Elle prend en
# paramètre le fichier classement.html
#==============================================================================
def extract_r5(file_name):

    # Lecture et parcours du fichier html
    soup = load_file(file_name)
    rows = soup.find('table').find_all('tr')[2:]

    equipes_plus_70 = []

    # Recherche des équipes ayant marqué ≥ 70 buts
    for row in rows:
        cols = row.find_all('td')
        if not cols :
            continue

        equipe = cols[1].get_text(strip=True)
        bp = int(cols[7].get_text(strip=True))

        if bp >= 70:
            equipes_plus_70.append((equipe, bp))

        # Si aucune équipe trouvée
        if not equipes_plus_70:
            return (
                "<h4>Équipes ayant marqué plus de 70 buts</h4>" 
                "Aucune équipe n'a atteint ce total.<br><br>"
            )

        # Construction du résultat HTML
        result_text = "<h4>Équipes ayant marqué plus de 70 buts</h4>"
        for equipe, buts in equipes_plus_70:
            result_text += f"{equipe} : <strong>{buts}</strong> buts<br>"

    return result_text




#==================================================================================
# Cette fonction retourne les matchs qui ont eu lieu en novembre 2008
# Ainsi que le temps d\'exécution de la requête. Elle prend en
# paramètre le fichier calendrier.html
#==================================================================================
def extract_r6(file_name):
    # Initialisation du tableay d\'affichage du résultat
    rslt = []

    # Lecture et parcours du fichier html
    soup = load_file(file_name)

    # On ne considère pas la première ligne
    r6 = soup.find('table').find_all('tr')[1:]

    matchs_novembre = []
    # --------------------------------------------------------------------------------
    # Parcours du dataset r6 et identification des matchs qui ont
    # eu lieu en nov 2008
    # --------------------------------------------------------------------------------
    for row in r6:
        cols = row.find_all('td')
        if len(cols) < 4:
            continue

        # Extraction du champ date
        date = cols[0].get_text(strip=True)

        # Vérifier si la date est en novembre 2008
        if date.endswith("/2008") and date[3:5] == "11":
            # Equipe à domicile
            domicile = cols[1].get_text(strip=True)

            # Score du match
            score = cols[2].get_text(strip=True)

            # Equipe à l\'extérieur
            exterieur = cols[3].get_text(strip=True)

            #Construction du dataset resultat
            matchs_novembre.append((date, domicile, score, exterieur))

    # Si aucun match trouvé
    if not matchs_novembre:
        return (
            "<h4>Matchs joués en novembre 2008</h4>" 
            "Aucun match trouvé.<br><br>"
        )

    # Construction du résultat HTML
    result_text = "<h4>Matchs joués en novembre 2008</h4>"
    for date, dom, score, ext in matchs_novembre:
        result_text += f"{date} : <strong>{dom}</strong> {score} <strong>{ext}</strong><br>"

    return result_text



#=====================================================================================
# Cette fonction retourne le nombre de victoires à domicile pour Manchester
# United et le temps d\'exécution de la requête. Elle prend en paramètre
# le fichier calendrier.html
#======================================================================================
def extract_r7(file_name):
    # Initialisation du tableay d\'affichage du résultat
    rslt = []

    # Lecture et parcours du fichier html
    soup = load_file(file_name)

    # on ne compte pas l\'entête
    rows = soup.find('table').find_all('tr')[1:]

    victoires = []

    #-------------------------------------------------------------------
    # Parcours du dataset r7 et extraction des données de la page html
    #--------------------------------------------------------------------
    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 4:
            continue

        #---------------------------------------------------------------
        # Extraction des données de date, equipe à domicile
        # score et équipe à l\'extérieur
        #---------------------------------------------------------------
        date = cols[0].get_text(strip=True)
        domicile = cols[1].get_text(strip=True)
        score = cols[2].get_text(strip=True)
        exterieur = cols[3].get_text(strip=True)

        #---------------------------------------------------------------
        # construction du résultat si MU joue à domiicile
        #---------------------------------------------------------------
        if domicile == "Manchester United":
            buts_domicile, buts_exterieur = score.split("-")
            buts_domicile = int(buts_domicile.strip())
            buts_exterieur = int(buts_exterieur.strip())

            if buts_domicile > buts_exterieur:
                victoires.append((date, domicile, score, exterieur))

    # Si aucune victoire trouvée
    if not victoires:
        return (
            "<h4>Victoires à domicile de Manchester United</h4>" 
            "Aucune victoire trouvée.<br><br>"
        )

    # Construction du résultat HTML
    result_text = "<h4>Victoires à domicile de Manchester United</h4>"

    for date, dom, score, ext in victoires:
        result_text += f"{date} : <strong>{dom}</strong> {score} <strong>{ext}</strong><br>"

    result_text += (
        f"<br><strong>Total :</strong> {len(victoires)} victoires<br>"
    )

    return result_text




#=====================================================================================
# Cette fonction retourne le classement des équipes par rapport nombre de victoires
# à l'extérieur et le temps d\'exécution de la requête. Elle prend en paramètre
# le fichier calendrier.html
#======================================================================================
def extract_r8(file_name):

    # Initialisation du compteur
    start_time = time.time()

    # Lecture et parcours du fichier html
    soup = load_file(file_name)

    # on ne compte pas l\'entête
    rows = soup.find('table').find_all('tr')[1:]

    victoires_ext = defaultdict(int)

    # --------------------------------------------------------------------
    # Parcours du dataset r8 et extraction des données de la page html
    # --------------------------------------------------------------------
    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 4:
            continue

        # ---------------------------------------------------------------
        # Extraction des données équipe à domicile
        # score et équipe à l\'extérieur
        # ---------------------------------------------------------------
        domicile = cols[1].get_text(strip=True)
        score = cols[2].get_text(strip=True)
        exterieur = cols[3].get_text(strip=True)

        buts_domicile, buts_exterieur = score.split("-")
        buts_domicile = int(buts_domicile.strip())
        buts_exterieur = int(buts_exterieur.strip())

        # Victoire à l\'extérieur
        if buts_exterieur > buts_domicile:
            victoires_ext[exterieur] += 1

    # Classement décroissant
    classement = sorted(victoires_ext.items(), key=lambda x: x[1], reverse=True)

    # Si aucune victoire trouvée
    if not classement:
        return (
            "<h4>Classement des équipes par victoires à l’extérieur</h4>" 
            "Aucune équipe n'a gagné à l'extérieur.<br><br>"
        )

    # Construction du résultat HTML
    html = "<ol>"
    for team, wins in classement:
        html += f"<li>{team} — {wins} victoires</li>"
    html += "</ol>"

    #for equip, nb in classement:
    #    result_text += f"{equip} : <strong>{nb}</strong> victoires<br>"

    return  f"""
    <h2>R8 — Classement des équipes par victoires à l’extérieur</h2>
    {html}
    """




#=====================================================================================
# Cette fonction retourne la moyenne de buts marqués à l\'extérieur par les
# équipes du top 6 et le temps d\'exécution de la requête. Elle prend en paramètre
# le fichier calendrier.html
#======================================================================================
def extract_r9(file_name):
    # Initialisation du tableay d\'affichage du résultat
    rslt = {}

    # Initialisation du compteur
    start_time = time.time()

    # Lecture et parcours du fichier html
    soup = load_file(file_name)

    # on ne compte pas l\'entête
    rows = soup.find('table').find_all('tr')[1:]

    # Top 6 défini
    top6 = {"Manchester United", "Liverpool", "Chelsea", "Arsenal", "Everton", "Aston Villa"}

    total_buts = 0
    total_matchs = 0

    #-------------------------------------------------------------
    # Parcours du dataset r8 pour exraire les buts marqués à
    # l\extérieur
    #--------------------------------------------------------------
    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 4:
            continue

        #domicile = cols[1].get_text(strip=True)
        exterieur = cols[3].get_text(strip=True)
        score = cols[2].get_text(strip=True)

        if exterieur in top6:
            buts_domicile, buts_exterieur = score.split("-")
            buts_exterieur = int(buts_exterieur.strip())
            total_buts += buts_exterieur
            total_matchs += 1

    #Calcul de la moyenne
    moyenne = total_buts / total_matchs if total_matchs > 0 else 0
    moyenne = round(moyenne, 2)

    html_top6 = "<ul>"
    for t in top6:
        html_top6 += f"<li>{t}</li>"
    html_top6 += "</ul>"

    # Construction du résultat HTML
    result_text = (
            "<h2>R9 - Moyenne de buts marqués à l’extérieur par le du Top 6</h2>" 
            "<h3>Équipes du Top 6</h3>"
            f"{html_top6}"
            f"Total de buts marqués à l’extérieur : <strong>{total_buts}</strong><br>" 
            f"Nombre total de matchs à l’extérieur : <strong>{total_matchs}</strong><br>" 
            f"<p>Moyenne de buts marqués à l’extérieur : <strong>{moyenne}</strong></p>"
        )

    return result_text



#=====================================================================================
# Cette fonction retourne le classement des équipes par rapport nombre de victoires
# à l'extérieur et le temps d\'exécution de la requête. Elle prend en paramètre
# les fichiers classement.html et calendrier.html
#======================================================================================
def extract_r10(file_name1, file_name2):
    # Initialisation du tableay d\'affichage du résultat
    rslt = {}

    # Initialisation du compteur
    start_time = time.time()

    # Retourne la position de l\'équipe à une position dans le classement
    def get_team_by_position(pos):
        # Charger le fichier
        soup = load_file(file_name1)

        # ignorer l'en-tête
        rows = soup.find("table").find_all("tr")[1:]

        row = rows[pos - 1] # pos=1 → index 0
        team = row.find_all("td")[1].get_text(strip=True)
        return team

    # Transforme '2 - 1' en (2,1)
    def parse_score(score):
        home, away = score.split("-")
        return int(home.strip()), int(away.strip())

    # Retourne toutes les confrontations entre team1 et team2
    def get_confrontations(team1, team2):
        soup = load_file(file_name2)
        rows = soup.find("table").find_all("tr")[1:]
        matches = []

        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 4:
                continue

            date = cols[0].get_text(strip=True)
            home = cols[1].get_text(strip=True)
            score = cols[2].get_text(strip=True)
            away = cols[3].get_text(strip=True)

            if {home, away} == {team1, team2}:
                home_goals, away_goals = parse_score(score)

                if home_goals > away_goals:
                    result = f"Victoire : {home}"
                elif away_goals > home_goals:
                    result = f"Victoire: {away}"
                else:
                    result = "Match nul"

                matches.append((date, home, score, away, result))

        return matches

    # ---------------------------------------------------------
    # Programme principal
    # ---------------------------------------------------------
    team1 = get_team_by_position(1) # Manchester United
    team2 = get_team_by_position(3) # Chelsea
    confrontations = get_confrontations(team1, team2)

    # Si aucune confrontation trouvée
    if not confrontations:
        return (
            f"<h4>Confrontations historiques entre {team1} et {team2}</h4>" 
            "Aucune confrontation trouvée.<br><br>"
        )

    # Construction du résultat HTML
    result_text = f"<h2>R10 - Confrontations entre {team1} et {team2}</h2>"

    for date, home, score, away, result in confrontations:
        result_text += (
            f"{date} : <strong>{home}</strong> {score} <strong>{away}</strong>" 
            f" → {result}<br>"
        )

    return result_text

#==============================================================================================#
#                       TEST DES FONCTIONS ET EXÉCUTION CONSOLE                                #
#==============================================================================================#
#print(extract_r1("classement.html"))
#print(extract_r2("statistiques.html", 1))
#print(extract_r4("statistiques.html"))
#print(extract_r5("classement.html"))
#print(extract_r6("calendrier.html"))
#print(extract_r7("calendrier.html"))
#print(extract_r8("calendrier.html"))
#print(extract_r9("calendrier.html"))
#print(extract_r10("classement.html","calendrier.html"))