import time
import random

# temps objectif en secondes
target_time = random.randint(1, 19)
print(f"Arrêter le chrono à {target_time} secondes.")

# temps maximal en secondes
max_time = 20
print(f"Temps maximal : {max_time} secondes.")

player_1_time = 0
player_2_time = 0

# En deux tours (1 tour par joueur)
for i in range(2):

    # Démarrer le chrono
    input(f"Tour {i + 1} : Appuyez sur Entrée pour démarrer le chrono...")
    start_time = time.time()
    
    # Attente de l'utilisateur pour arrêter le chrono
    input("Appuyez sur Entrée pour arrêter le chrono...")
    elapsed_time = time.time() - start_time
    
    if i == 0:
        player_1_time = elapsed_time
    else:
        player_2_time = elapsed_time

    print(f"Temps écoulé : {elapsed_time:.2f} secondes.")
    
    if elapsed_time > max_time:
        print("Vous avez dépassé le temps maximal !")
        break

# Calcul du tour le plus proche de l'objectif
if player_1_time and player_2_time:
    player_1_diff = abs(player_1_time - target_time)
    player_2_diff = abs(player_2_time - target_time)

    if player_1_diff < player_2_diff:
        print("Le joueur 1 est le plus proche de l'objectif !")
    elif player_2_diff < player_1_diff:
        print("Le joueur 2 est le plus proche de l'objectif !")
    else:
        print("Égalité ! Les deux joueurs sont à la même distance de l'objectif.")