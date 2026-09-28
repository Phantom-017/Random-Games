import json
import random
import select
import sys
import time
from pathlib import Path


TEMPS_IMPARTI = 30
FICHIER_SCORES = Path(__file__).with_name("scores_sportifs.json")
PLAGE_REPETITIONS = {
	"Facile": (15, 25),
	"Moyen": (30, 40),
	"Difficile": (45, 55),
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


def tirer_defi(difficulte):
	"""Retourne un exercice et un nombre de repetitions aleatoires."""
	exercice = random.choice(EXERCICES)
	minimum, maximum = PLAGE_REPETITIONS[difficulte]
	repetitions = random.randint(minimum, maximum)
	return exercice, repetitions


def charger_scores():
	"""Charge les scores existants ou cree un tableau vide par exercice."""
	if not FICHIER_SCORES.exists():
		return {exercice: [] for exercice in EXERCICES}

	try:
		with FICHIER_SCORES.open("r", encoding="utf-8") as fichier:
			scores = json.load(fichier)
	except (OSError, json.JSONDecodeError):
		return {exercice: [] for exercice in EXERCICES}

	return {
		exercice: sorted(scores.get(exercice, []))[:3]
		for exercice in EXERCICES
	}


def sauvegarder_temps(scores, exercice, temps):
	"""Ajoute un temps et conserve seulement les trois meilleurs."""
	scores[exercice].append(round(temps, 2))
	scores[exercice] = sorted(scores[exercice])[:3]

	with FICHIER_SCORES.open("w", encoding="utf-8") as fichier:
		json.dump(scores, fichier, indent=2, ensure_ascii=False)


def attendre_entree(temps_imparti):
	"""Attend Entree, ou renvoie None si le temps imparti est depasse."""
	debut = time.perf_counter()
	while True:
		temps = time.perf_counter() - debut
		restant = temps_imparti - temps
		if restant <= 0:
			print("\rChrono : 30.0 s | Temps restant : 0.0 s", end="\n", flush=True)
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
		classement = " | ".join(f"{temps:.2f} s" for temps in top3)
		print(f"Top 3 pour {exercice} : {classement}")


def choisir_difficulte():
	"""Demande le niveau et retourne son nom et son nombre de defis."""
	while True:
		print("Choisis une difficulte :")
		print("1 - Facile : 1 defi")
		print("2 - Moyen : 2 defis")
		print("3 - Difficile : 3 a 5 defis")

		choix = input("> ").strip()
		if choix == "1":
			return "Facile", 1
		if choix == "2":
			return "Moyen", 2
		if choix == "3":
			return "Difficile", random.randint(3, 5)

		print("Choix invalide. Entre 1, 2 ou 3.\n")


def jouer():
	score = 0
	scores = charger_scores()
	nom_difficulte, nombre_defis = choisir_difficulte()

	print("\n=== DEFIS POIDS DU CORPS ===")
	print(f"Difficulte : {nom_difficulte} ({nombre_defis} defi(s))")
	print(f"Appuie sur Entree quand le defi est termine ({TEMPS_IMPARTI} secondes max).")
	print("Ecris q puis Entree pour quitter.\n")

	for numero_defi in range(1, nombre_defis + 1):
		exercice, repetitions = tirer_defi(nom_difficulte)
		print(f"Defi {numero_defi}/{nombre_defis} : {repetitions} {exercice} !")

		resultat = attendre_entree(TEMPS_IMPARTI)
		if resultat is None:
			sauvegarder_temps(scores, exercice, TEMPS_IMPARTI)
			print(f"Temps ecoule ! Temps enregistre : {TEMPS_IMPARTI:.2f} s")
			afficher_top3(scores, exercice)
			print()
			continue

		reponse, temps = resultat
		if reponse in {"q", "quit", "quitter"}:
			break

		sauvegarder_temps(scores, exercice, temps)
		score += 1
		print(f"Bravo ! Temps realise : {temps:.2f} s. Defis termines : {score}")
		afficher_top3(scores, exercice)
		print()

	print(f"\nFin de la partie. Score final : {score} defi(s) reussi(s).")


if __name__ == "__main__":
	jouer()
