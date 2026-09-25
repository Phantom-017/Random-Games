import random

kill_ticket = random.randint(1, 6)

while True:
    random_number = random.randint(1, 6)
    input("Appuyez sur Entrée pour tirer...")
    print("Vous avez tiré le numéro :", random_number)
    if random_number == kill_ticket:
        print("FAAAAAAHHHHH ! T mor !")
        break
