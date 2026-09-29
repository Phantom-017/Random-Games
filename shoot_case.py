import json
import hashlib
import random
from pathlib import Path


TAILLE_GRILLE = 5
NOMBRE_MANCHES = 10
NOMBRE_TIRS = 3
DOSSIER_SCORES = Path(__file__).with_name("scores_joueurs")


def normaliser_nom(nom):
    """Nettoie le pseudo sans tenir compte des majuscules pour son identite."""
    nom_nettoye = " ".join(nom.strip().split())
    return nom_nettoye or "Joueur"


def fichier_joueur(nom):
    """Retourne toujours le meme fichier pour un meme pseudo."""
    nom_normalise = normaliser_nom(nom)
    identifiant = hashlib.sha256(
        nom_normalise.casefold().encode("utf-8")
    ).hexdigest()[:16]
    return DOSSIER_SCORES / f"joueur_{identifiant}.json"


def normaliser_scores(scores):
    scores_normalises = []
    if not isinstance(scores, list):
        return scores_normalises

    for entree in scores:
        if not isinstance(entree, dict) or "score" not in entree:
            continue
        try:
            scores_normalises.append(
                {
                    "nom": normaliser_nom(entree.get("nom", "Joueur")),
                    "score": int(entree["score"]),
                }
            )
        except (TypeError, ValueError):
            continue

    return sorted(scores_normalises, key=lambda entree: entree["score"], reverse=True)[:3]


def charger_scores(nom):
    fichier_scores = fichier_joueur(nom)
    if not fichier_scores.exists():
        return []

    try:
        with fichier_scores.open("r", encoding="utf-8") as fichier:
            return normaliser_scores(json.load(fichier))
    except (json.JSONDecodeError, OSError):
        return []


def charger_scores_partages():
    scores = []
    if not DOSSIER_SCORES.exists():
        return scores

    for fichier_scores in DOSSIER_SCORES.glob("joueur_*.json"):
        try:
            with fichier_scores.open("r", encoding="utf-8") as fichier:
                scores.extend(normaliser_scores(json.load(fichier)))
        except (json.JSONDecodeError, OSError):
            continue

    return sorted(scores, key=lambda entree: entree["score"], reverse=True)[:3]


def sauvegarder_score(nom, score):
    nom = normaliser_nom(nom)
    scores = charger_scores(nom)
    scores.append({"nom": nom, "score": score})
    scores = normaliser_scores(scores)

    DOSSIER_SCORES.mkdir(exist_ok=True)
    with fichier_joueur(nom).open("w", encoding="utf-8") as fichier:
        json.dump(scores, fichier, indent=2, ensure_ascii=False)


def afficher_scores():
    scores = charger_scores_partages()
    print("\n=== MEILLEURS SCORES ===")

    if not scores:
        print("Aucun score enregistre pour le moment.")
    else:
        for position, entree in enumerate(scores, start=1):
            print(f"{position}. {entree['nom']} - {entree['score']} points")

    input("\nAppuie sur Entree pour revenir au menu.")


def afficher_grille(tirs_rates=None, cible=None):
    tirs_rates = tirs_rates or set()
    print("\n    " + "   ".join(str(colonne) for colonne in range(1, TAILLE_GRILLE + 1)))
    print("  +" + "---+" * TAILLE_GRILLE)

    for ligne in range(1, TAILLE_GRILLE + 1):
        cases = []
        for colonne in range(1, TAILLE_GRILLE + 1):
            position = (ligne, colonne)
            symbole = "X" if position == cible else "o" if position in tirs_rates else " "
            cases.append(f" {symbole} ")
        print(f"{ligne} |" + "|".join(cases) + "|")
        print("  +" + "---+" * TAILLE_GRILLE)


def demander_tir():
    while True:
        choix = input("Vise une case (ligne colonne), ou q pour quitter : ").strip().lower()
        if choix in {"q", "quit", "quitter"}:
            return None

        coordonnees = choix.replace(",", " ").split()
        if len(coordonnees) != 2:
            print("Entre deux nombres, par exemple : 2 4.")
            continue

        try:
            ligne, colonne = (int(valeur) for valeur in coordonnees)
        except ValueError:
            print("Les coordonnees doivent etre des nombres.")
            continue

        if 1 <= ligne <= TAILLE_GRILLE and 1 <= colonne <= TAILLE_GRILLE:
            return ligne, colonne

        print(f"Choisis une ligne et une colonne entre 1 et {TAILLE_GRILLE}.")


def jouer():
    nom = input("Entre ton pseudo : ").strip() or "Joueur"
    score = 0

    print("\n=== SHOOT CASE ===")
    print(f"Trouve la cible cachee en {NOMBRE_MANCHES} manches.")
    print(f"Tu as {NOMBRE_TIRS} tirs par manche. Un tir reussi rapporte jusqu'a 100 points.")

    for numero_manche in range(1, NOMBRE_MANCHES + 1):
        cible = (random.randint(1, TAILLE_GRILLE), random.randint(1, TAILLE_GRILLE))
        tirs_rates = set()
        touche = False

        print(f"\n--- Manche {numero_manche}/{NOMBRE_MANCHES} ---")
        for numero_tir in range(1, NOMBRE_TIRS + 1):
            afficher_grille(tirs_rates)
            print(f"Score : {score} | Tir {numero_tir}/{NOMBRE_TIRS}")
            tir = demander_tir()

            if tir is None:
                print("\nPartie interrompue.")
                sauvegarder_score(nom, score)
                return

            if tir == cible:
                points = 100 - (numero_tir - 1) * 25
                score += points
                print(f"Touche ! +{points} points.")
                afficher_grille(tirs_rates, cible)
                touche = True
                break

            tirs_rates.add(tir)
            print("Rate !")

        if not touche:
            print(f"La cible etait en ligne {cible[0]}, colonne {cible[1]}.")

    print(f"\nPartie terminee, {nom} ! Score final : {score} points.")
    sauvegarder_score(nom, score)
    print("Ton score a ete sauvegarde.")


def main_menu():
    while True:
        print("\n=== MENU PRINCIPAL ===")
        print("1 - Jouer au jeu de tir")
        print("2 - Afficher les scores")
        print("3 - Quitter")

        choix = input("> ").strip()
        if choix == "1":
            jouer()
        elif choix == "2":
            afficher_scores()
        elif choix == "3":
            print("\nA bientot !")
            break
        else:
            print("Choix invalide. Entre 1, 2 ou 3.")


if __name__ == "__main__":
    main_menu()
# Menu principal de tir acrade

def main_menu():
    while True:
        print("\n=== MENU PRINCIPAL ===")
        print("1 - Jouer au jeu de tir")
        print("2 - Afficher les scores")
        print("3 - Quitter")

        choix = input("> ").strip()
        if choix == "1":
            jouer()
        elif choix == "2":
            afficher_scores()
        elif choix == "3":
            print("\nA bientot !")
            break
        else:
            print("Choix invalide. Entre 1, 2 ou 3.\n")