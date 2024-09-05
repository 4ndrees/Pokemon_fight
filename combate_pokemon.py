import random
from pokeload import get_all_pokemons


# Recibir la información del jugador
def get_player_profile(pokemon_list):
    profile = {
        "player_name": input("¿Cual es tu nombre? "),
        "pokemon_inventory": [random.choice(pokemon_list) for a in range(3)],
        "combats": 0,
        "pokeballs": 0,
        "health_potion": 0
    }

    return profile


# Comprobar si queda algún pokemon con vida en tu inventario
def any_player_pokemon_lives(player_profile):
    return sum([pokemon["current_health"] for pokemon in player_profile["pokemon_inventory"]]) > 0


# Recibir la información del pokemon consultado
def get_pokemon_info(pokemon):
    return "{} | levl {} | hp {}/{}".format(pokemon["name"],
                                            pokemon["level"],
                                            pokemon["current_health"],
                                            pokemon["base_health"])


# Elegir un nuevo pokemon con el que combatir
def choose_pokemon(player_profile):
    chosen = None
    while not chosen:
        print("Elige con que pokemon lucharás")
        for index in range(len(player_profile["pokemon_inventory"])):
            print("{} - {}".format(index, get_pokemon_info(player_profile["pokemon_inventory"][index])))
        try:
            pokemon = None
            while not pokemon:
                pokemon = player_profile["pokemon_inventory"][int(input("¿Cual eliges?"))]
                if pokemon["current_health"] <= 0:
                    pokemon = None
            return pokemon
        except (ValueError, IndexError):
            print("Opcion invalida")


def weaknesses(attack_type, damage, pokemon_types):
    # Definir las debilidades de cada tipo en un diccionario
    type_weaknesses = {
        "Acero": ["Lucha", "Fuego", "Tierra"],
        "Agua": ["Planta", "Eléctrico"],
        "Bicho": ["Volador", "Fuego", "Roca"],
        "Dragón": ["Hada", "Hielo", "Dragón"],
        "Eléctrico": ["Tierra"],
        "Fantasma": ["Fantasma", "Siniestro"],
        "Fuego": ["Tierra", "Agua", "Roca"],
        "Hada": ["Acero", "Veneno"],
        "Hielo": ["Lucha", "Acero", "Roca", "Fuego"],
        "Lucha": ["Psíquico", "Volador", "Hada"],
        "Normal": ["Lucha"],
        "Planta": ["Volador", "Bicho", "Veneno", "Hielo", "Fuego"],
        "Psíquico": ["Bicho", "Fantasma", "Siniestro"],
        "Roca": ["Lucha", "Tierra", "Acero", "Agua", "Planta"],
        "Siniestro": ["Lucha", "Hada", "Bicho"],
        "Tierra": ["Agua", "Planta", "Hielo"],
        "Veneno": ["Tierra", "Psíquico"],
        "Volador": ["Roca", "Hielo", "Eléctrico"]
    }

    # Inicializamos el multiplicador de daño en 1 (sin cambios)
    multiplier = 1

    # Recorrer cada tipo de Pokémon en la lista
    for pokemon_type in pokemon_types:
        # Verificar si el ataque es efectivo contra el tipo del Pokémon (x1.5)
        if attack_type in type_weaknesses.get(pokemon_type, []):
            multiplier *= 1.5

        # Verificar si el ataque es débil frente al tipo del Pokémon (x0.5)
        elif pokemon_type in type_weaknesses.get(attack_type, []):
            multiplier *= 0.5

    # Aplicar el multiplicador total al daño
    return damage * multiplier


def get_attack_info(pokemon_attack):
    return "{} | typ {} | dmg {}".format(pokemon_attack["name"],
                                         pokemon_attack["type"],
                                         pokemon_attack["damage"])


def choose_attack(pokemon):
    chosen = None
    while not chosen:
        print("Elige el ataque a realizar:")
        for index in range(len(pokemon["attacks"])):
            try:
                min_level = int(pokemon["attacks"][index]["min_level"])
                if min_level <= pokemon["level"]:
                    print("{} - {}".format(index, get_attack_info(pokemon["attacks"][index])))
            except (ValueError, IndexError):
                print("Error al obtener el nivel mínimo")
        try:
            return pokemon["attacks"][int(input("¿Cual eliges?"))]
        except (ValueError, IndexError):
            print("Opcion invalida")


# Atacar al pokemon enemigo
def player_attack(player_pokemon, enemy_pokemon):

    attack = choose_attack(player_pokemon)
    attack_damage = weaknesses(attack["type"], attack["damage"], enemy_pokemon["type"])
    enemy_pokemon["current_health"] -= attack_damage
    print("{} ha realizado {}".format(player_pokemon["name"], attack["name"]))
    print("{} ha recibido {} puntos de daño".format(enemy_pokemon["name"], attack_damage))
    print("Ps de {} reducidos a {}".format(enemy_pokemon["name"], enemy_pokemon["current_health"]))


# Recibir un ataque del pokemon enemigo
def enemy_attack(enemy_pokemon, player_pokemon):

    attack = None
    while not attack:
        index = random.randint(0, len(enemy_pokemon["attacks"])-1)
        try:
            min_level = int(enemy_pokemon["attacks"][index]["min_level"])
            if min_level <= enemy_pokemon["level"]:
                attack = enemy_pokemon["attacks"][index]
        except (ValueError, IndexError):
            print("Error al obtener el nivel mínimo")

    attack_damage = weaknesses(attack["type"], attack["damage"], player_pokemon["type"])
    player_pokemon["current_health"] -= attack_damage

    print("{} ha realizado {}".format(enemy_pokemon["name"], attack["name"]))
    print("{} ha recibido {} puntos de daño".format(player_pokemon["name"], attack_damage))
    print("Ps de {} reducidos a {}".format(player_pokemon["name"], player_pokemon["current_health"]))


# Añadir experiencia a "current_exp" de tu pokemon y subir de nivel en caso de tener los puntos necesarios
def assign_experience(attack_history):
    for pokemon in attack_history:
        points = random.randint(1, 5)
        pokemon["current_exp"] += points

        while pokemon["current_exp"] > 20:
            pokemon["current_exp"] -= 20
            pokemon["level"] += 1
            print("Tu pokemon ha subido al nivel".format(get_pokemon_info(pokemon)))


# Si el usuario tiene cura en el inventario, el pokemon se cura 50 puntos de vida o hasta llegar a base_helth
# Si el usuario no tiene cura no se cura
def cure_pokemon(player_profile, player_pokemon):
    if player_profile["health_potion"] > 0:
        if player_pokemon["base_health"] <= player_pokemon["current_health"] + 50:
            print("{} ha recuperado 50 ps".format(player_pokemon["name"]))
            player_pokemon["current_health"] += 50
        else:
            print("{} ha recuperado {} ps".format(player_pokemon["name"], player_pokemon["base_health"] -
                                                  player_pokemon["current_health"]))
            player_pokemon["current_health"] += player_pokemon["base_health"]
    else:
        print("No tienes pociones de curación en tu inventario")


# probabilidad de capturarlo relativa a la vida
# si no hay pokeballs no se puede capturar
# si se captura se añade tal cual al inventario
def capture_with_pokeball(player_profile, enemy_pokemon):
    if player_profile["pokeballs"] > 0:
        if random.randint(1, enemy_pokemon["base_health"]) > enemy_pokemon["current_health"]:
            player_profile["pokemon_inventory"].append(enemy_pokemon)
            print("Pokemon enemigo capturado")
            return True
        else:
            print("{} se ha escapado".format(enemy_pokemon["name"]))
            return False
    else:
        print("No tienes pokeballs en tu inventario")


# controlador del combate pokemon
# Opciones: atacar (A), capturar pokemon enemigo (P), curar a tu pokemon (V), elegir otro pokemon (C)
def fight(player_profile, enemy_pokemon):
    print("--- NUEVO COMBATE ---")

    enemy_pokemon_captured = False
    attack_history = []
    player_pokemon = choose_pokemon(player_profile)
    print("Contrincantes: {} vs {}".format(get_pokemon_info(player_pokemon),
                                           get_pokemon_info(enemy_pokemon)))

    while any_player_pokemon_lives(player_profile) and enemy_pokemon["current_health"] > 0:
        action = None
        while action not in ["A", "P", "V", "C"]:
            action = input("¿Que deseas hacer? [A]tacar, [P]okeball ({}), Pocion de [V]ida ({}), [C]ambiar".format(
                player_profile["pokeballs"], player_profile["health_potion"]))

        if action == "A":
            player_attack(player_pokemon, enemy_pokemon)
            attack_history.append(player_pokemon)
        elif action == "V":
            cure_pokemon(player_profile, player_pokemon)
        elif action == "P":
            capture_with_pokeball(player_profile, enemy_pokemon)
        elif action == "C":
            player_pokemon = choose_pokemon(player_profile)
            print("Has elegido a {}".format(get_pokemon_info(player_pokemon)))

        enemy_attack(enemy_pokemon, player_pokemon)

        if player_pokemon["current_health"] <= 0 and any_player_pokemon_lives(player_profile):
            player_pokemon = choose_pokemon(player_profile)
            print("Has elegido a {}".format(get_pokemon_info(player_pokemon)))

    if enemy_pokemon["current_health"] <= 0 or enemy_pokemon_captured:
        print("Has ganado!!")
        assign_experience(attack_history)

    print("--- FIN DEL COMBATE ---")

    input("presiona enter para continuar")


def get_item_lotery(player_profile):
    rand = random.randint(1, 2)
    if rand == 1:
        player_profile["pokeballs"] += 1
    else:
        player_profile["health_potion"] += 1


def main():
    pokemon_list = get_all_pokemons()
    player_profile = get_player_profile(pokemon_list)

    while any_player_pokemon_lives(player_profile):
        enemy_pokemon = random.choice(pokemon_list)
        fight(player_profile, enemy_pokemon)
        get_item_lotery(player_profile)

    print("Has perdido en el combate nº{}".format(player_profile["combats"]))


if __name__ == "__main__":
    main()
