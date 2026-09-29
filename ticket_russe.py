import random

GAGES = {
    1: [
        "Faire 5 pompes.",
        "Chanter le refrain d'une chanson.",
        "Faire rire quelqu'un en 30 secondes.",
        "Imiter un animal pendant 20 secondes.",
        "Tenir une pose de statue pendant 30 secondes.",
        "Faire 10 flexions du cou.",
        "Dire le mot 'bonjour' comme un robot pendant 15 secondes.",
    ],
    2: [
        "Faire 10 pompes.",
        "Imiter une personne du groupe pendant 30 secondes.",
        "Danser sans musique pendant 30 secondes.",
        "Raconter une blague sans rire.",
        "Faire 15 fentes.",
        "Parler avec une voix de pirate pendant 1 minute.",
        "Faire un défi de mimique avec quelqu'un du groupe.",
    ],
    3: [
        "Faire 20 squats.",
        "Parler avec une voix choisie par le groupe pendant 2 minutes.",
        "Faire une declaration dramatique a un objet.",
        "Manger une gorgée de quelque chose sans grimacer.",
        "Courir sur place pendant 30 secondes en chantant.",
        "Faire 5 pompes avec les pieds sur une chaise.",
        "Raconter une anecdote embarrassante en riant.",
    ],
    4: [
        "Faire 15 burpees.",
        "Laisser le groupe choisir ta photo de profil pendant 10 minutes.",
        "Improviser une publicite pour un objet du groupe.",
        "Faire un discours de 1 minute sur un sujet absurde.",
        "Essayer de faire un tour de danse imposé par le groupe.",
        "Reproduire une scène de film en mode comédie.",
        "Faire 20 sauts de kangourou.",
    ],
    5: [
        "Faire 30 squats.",
        "Raconter une anecdote genante.",
        "Faire une danse choregraphiee par le groupe.",
        "Jouer une petite scène avec un autre joueur sans parler.",
        "Tenir une conversation normale en lisant sur un mur.",
        "Faire 25 jumping jacks sans s'arrêter.",
        "Imiter un personnage célèbre pendant 1 minute.",
    ],
    6: [
        "Faire 25 burpees.",
        "Faire un discours de 2 minutes sur un sujet choisi par le groupe.",
        "Realiser deux gages choisis par le groupe.",
        "Participer a un mini-jeu inventé par le groupe pendant 2 minutes.",
        "Faire une performance de 1 minute avec une consigne bizarre.",
        "Répéter un geste ridicule pendant 1 minute sans rire.",
        "Faire 30 squats puis 10 pompes sans pause.",
    ],
}


def choisir_difficulte(nombre_tickets):
    return min(nombre_tickets, 6)


kill_ticket = random.randint(1, 6)
nombre_tickets = 0

if __name__ == "__main__":
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
