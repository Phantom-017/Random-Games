import random

GAGES = {
    1: [
        "Faire 5 pompes.",
        "Chanter le refrain d'une chanson.",
        "Faire rire quelqu'un en 30 secondes.",
    ],
    2: [
        "Faire 10 pompes.",
        "Imiter une personne du groupe pendant 30 secondes.",
        "Danser sans musique pendant 30 secondes.",
    ],
    3: [
        "Faire 20 squats.",
        "Parler avec une voix choisie par le groupe pendant 2 minutes.",
        "Faire une declaration dramatique a un objet.",
    ],
    4: [
        "Faire 15 burpees.",
        "Laisser le groupe choisir ta photo de profil pendant 10 minutes.",
        "Improviser une publicite pour un objet du groupe.",
    ],
    5: [
        "Faire 30 squats.",
        "Raconter une anecdote genante.",
        "Faire une danse choregraphiee par le groupe.",
    ],
    6: [
        "Faire 25 burpees.",
        "Faire un discours de 2 minutes sur un sujet choisi par le groupe.",
        "Realiser deux gages choisis par le groupe.",
    ],
}


def choisir_difficulte(nombre_tickets):
    return min(nombre_tickets, 6)


kill_ticket = random.randint(1, 6)
nombre_tickets = 0

while True:
    random_number = random.randint(1, 6)
    input("Appuyez sur Entrée pour tirer...")
    nombre_tickets += 1
    print("Vous avez tiré le numéro :", random_number)
    if random_number == kill_ticket:
        print("FAAAAAAHHHHH ! T mor !")
        difficulte = choisir_difficulte(nombre_tickets)
        gage = random.choice(GAGES[difficulte])
        print(f"Gage de difficulte {difficulte} : {gage}")
        break
