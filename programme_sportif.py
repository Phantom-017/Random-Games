import json
import hashlib
import random
import select
import sys
import time
from pathlib import Path


TEMPS_IMPARTI = 60
DOSSIER_SCORES = Path(__file__).with_name("scores_joueurs")
PLAGE_REPETITIONS = {
	"Facile": (15, 25),
	"Moyen": (30, 40),
	"Difficile": (45, 55),
}
PLAGE_SECONDES = {
	"Facile": (10, 20),
	"Moyen": (20, 30),
	"Difficile": (30, 45),
}


EXERCICES = [
	"pompes",
	"squats",
	"fentes (par jambe)",
	"abdominaux",
	"burpees",
	"mountain climbers (par jambe)",
	"jumping jacks",
	"gainage (secondes)",
	"pompes diamants",
	"pompes avec les mains larges",
	"pompes pike",
	"dips sur une chaise",
	"fentes laterales (par jambe)",
	"ponts fessiers",
	"elevations de mollets",
	"levees de jambes",
	"touche-epaules en planche",
	"superman",
	"montees de genoux",
	"chaise contre un mur (secondes)",
	"bear crawl (par pas)",
]
EXERCICES_EN_SECONDES = {
	"gainage (secondes)",
	"chaise contre un mur (secondes)",
}


def tirer_defi(difficulte):
	"""Retourne un exercice et une quantite adaptee a son unite."""
	exercice = random.choice(EXERCICES)
	if exercice in EXERCICES_EN_SECONDES:
		minimum, maximum = PLAGE_SECONDES[difficulte]
	else:
		minimum, maximum = PLAGE_REPETITIONS[difficulte]
	return exercice, random.randint(minimum, maximum)


def scores_vides():
	return {exercice: [] for exercice in EXERCICES}


def normaliser_scores(scores):
	"""Convertit les scores lus en format nom + temps."""
	scores_normalises = scores_vides()
	for exercice in EXERCICES:
		entrees = []
		for entree in scores.get(exercice, []) if isinstance(scores, dict) else []:
			if isinstance(entree, dict) and "temps" in entree:
				try:
					entrees.append(
						{
							"nom": entree.get("nom", "Ancien joueur"),
							"temps": float(entree["temps"]),
						}
					)
				except (TypeError, ValueError):
					continue
			elif isinstance(entree, (int, float)):
				entrees.append({"nom": "Ancien joueur", "temps": float(entree)})

		scores_normalises[exercice] = sorted(
			entrees, key=lambda entree: entree["temps"]
		)[:3]

	return scores_normalises


def fichier_joueur(nom):
	"""Retourne un fichier stable sans mettre le pseudo dans le chemin."""
	identifiant = hashlib.sha256(nom.strip().casefold().encode("utf-8")).hexdigest()[:16]
	return DOSSIER_SCORES / f"joueur_{identifiant}.json"


def charger_scores(nom):
	"""Charge uniquement les scores du joueur courant."""
	fichier_scores = fichier_joueur(nom)
	if not fichier_scores.exists():
		return scores_vides()

	try:
		with fichier_scores.open("r", encoding="utf-8") as fichier:
			return normaliser_scores(json.load(fichier))
	except (OSError, json.JSONDecodeError):
		return scores_vides()


def charger_scores_partages():
	"""Assemble les scores de tous les joueurs pour l'affichage uniquement."""
	scores_partages = scores_vides()
	if not DOSSIER_SCORES.exists():
		return scores_partages

	for fichier_scores in DOSSIER_SCORES.glob("joueur_*.json"):
		try:
			with fichier_scores.open("r", encoding="utf-8") as fichier:
				scores_joueur = normaliser_scores(json.load(fichier))
		except (OSError, json.JSONDecodeError):
			continue

		for exercice in EXERCICES:
			scores_partages[exercice].extend(scores_joueur[exercice])

	for exercice in EXERCICES:
		scores_partages[exercice] = sorted(
			scores_partages[exercice], key=lambda entree: entree["temps"]
		)[:3]
	return scores_partages


def sauvegarder_temps(scores, exercice, temps, nom):
	"""Ajoute un temps et conserve seulement les trois meilleurs."""
	scores[exercice].append({"nom": nom, "temps": round(temps, 2)})
	scores[exercice] = sorted(scores[exercice], key=lambda entree: entree["temps"])[:3]

	DOSSIER_SCORES.mkdir(exist_ok=True)
	with fichier_joueur(nom).open("w", encoding="utf-8") as fichier:
		json.dump(scores, fichier, indent=2, ensure_ascii=False)


def attendre_entree(temps_imparti):
	"""Attend Entree, ou renvoie None si le temps imparti est depasse."""
	debut = time.perf_counter()
	while True:
		temps = time.perf_counter() - debut
		restant = temps_imparti - temps
		if restant <= 0:
			print(
				f"\rChrono : {temps_imparti:.1f} s | Temps restant : 0.0 s",
				end="\n",
				flush=True,
			)
			return None

		print(
			f"\rChrono : {temps:04.1f} s | Temps restant : {restant:04.1f} s",
			end="",
			flush=True,
		)
		lecture, _, _ = select.select([sys.stdin], [], [], min(0.1, restant))
		if lecture:
			reponse = sys.stdin.readline().strip().lower()
			temps = min(time.perf_counter() - debut, temps_imparti)
			print("\r" + " " * 55 + "\r", end="", flush=True)
			return reponse, temps


def afficher_top3(scores, exercice):
	top3 = scores[exercice]
	if top3:
		classement = " | ".join(
			f"{entree['nom']} : {entree['temps']:.2f} s" for entree in top3
		)
		print(f"Top 3 pour {exercice} : {classement}")


def afficher_scores():
	"""Affiche les trois meilleurs temps de chaque exercice."""
	scores = charger_scores_partages()
	print("\n=== TOP 3 DES SCORES ===")
	aucun_score = True
	for exercice in EXERCICES:
		if scores[exercice]:
			aucun_score = False
			print(f"\n{exercice} :")
			for position, entree in enumerate(scores[exercice], start=1):
				print(f"{position}. {entree['nom']} - {entree['temps']:.2f} s")

	if aucun_score:
		print("Aucun score enregistre pour le moment.")
	input("\nAppuie sur Entree pour revenir au menu.")


def choisir_difficulte():
	"""Demande le niveau et retourne son nom et son nombre de defis."""
	while True:
		print("Choisis une difficulte :")
		print("1 - Facile : 1 defi")
		print("2 - Moyen : 2 defis")
		print("3 - Difficile : 3 a 5 defis")
		print("4 - Afficher les scores")
		print("5 - Quitter")

		choix = input("> ").strip()
		if choix == "1":
			return "Facile", 1
		if choix == "2":
			return "Moyen", 2
		if choix == "3":
			return "Difficile", random.randint(3, 5)
		if choix == "4":
			afficher_scores()
			continue
		if choix == "5":
			return None

		print("Choix invalide. Entre 1, 2, 3, 4 ou 5.\n")


def jouer():
	score = 0
	choix_difficulte = choisir_difficulte()
	if choix_difficulte is None:
		print("\nA bientot !")
		return

	nom_difficulte, nombre_defis = choix_difficulte
	nom_joueur = input("Entre ton nom ou ton pseudo : ").strip() or "Anonyme"
	scores = charger_scores(nom_joueur)

	print("\n=== DEFIS POIDS DU CORPS ===")
	print(f"Difficulte : {nom_difficulte} ({nombre_defis} defi(s))")
	print(f"Appuie sur Entree quand le defi est termine ({TEMPS_IMPARTI} secondes max).")
	print("Ecris q puis Entree pour quitter.\n")

	for numero_defi in range(1, nombre_defis + 1):
		exercice, quantite = tirer_defi(nom_difficulte)
		unite = "secondes" if exercice in EXERCICES_EN_SECONDES else "repetitions"
		print(f"Defi {numero_defi}/{nombre_defis} : {quantite} {unite} de {exercice} !")

		resultat = attendre_entree(TEMPS_IMPARTI)
		if resultat is None:
			sauvegarder_temps(scores, exercice, TEMPS_IMPARTI, nom_joueur)
			print(f"Temps ecoule ! Temps enregistre : {TEMPS_IMPARTI:.2f} s")
			afficher_top3(charger_scores_partages(), exercice)
			print()
			continue

		reponse, temps = resultat
		if reponse in {"q", "quit", "quitter"}:
			break

		sauvegarder_temps(scores, exercice, temps, nom_joueur)
		score += 1
		print(f"Bravo ! Temps realise : {temps:.2f} s. Defis termines : {score}")
		afficher_top3(charger_scores_partages(), exercice)
		print()

	print(f"\nFin de la partie. Score final : {score} defi(s) reussi(s).")


if __name__ == "__main__":
	jouer()
