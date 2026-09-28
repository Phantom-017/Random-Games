import random


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


def tirer_defi():
	"""Retourne un exercice et un nombre aleatoires."""
	exercice = random.choice(EXERCICES)
	repetitions = random.randint(5, 25)
	return exercice, repetitions


def jouer():
	score = 0

	print("\n=== DEFIS POIDS DU CORPS ===")
	print("Appuie sur Entree quand le defi est termine.")
	print("Ecris q puis Entree pour quitter.\n")

	while True:
		exercice, repetitions = tirer_defi()
		print(f"Defi : {repetitions} {exercice} !")

		reponse = input("> ").strip().lower()
		if reponse in {"q", "quit", "quitter"}:
			break

		score += 1
		print(f"Bravo ! Defis termines : {score}\n")

	print(f"\nFin de la partie. Score final : {score} defi(s).")


if __name__ == "__main__":
	jouer()
