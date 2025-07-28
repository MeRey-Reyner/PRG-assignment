# Name: S10270880E
# Class: PRG1
# Date: July 2025
# Description:
# This program implements the "Sundrop Caves" strategy role-playing game.
# The objective is to explore a mine to collect minerals, sell them, and reach 100 GP to retire.

from random import randint
import os
import json

# --- Global Constants ---
TURNS_PER_DAY = 20
WIN_GP = 2000
MAP_FILE = "level1.txt"
SAVE_FILE = "savegame.json"
SCORES_FILE = "topscores.txt"

minerals = ['copper', 'silver', 'gold', 'platinum', 'obsidian']
mineral_names = {'C': 'copper', 'S': 'silver', 'G': 'gold', 'P': 'platinum', 'O': 'obsidian', 'D': 'door_down', 'U': 'door_up'}
mineral_symbols = {'copper': 'C', 'silver': 'S', 'gold': 'G', 'platinum': 'P', 'obsidian': 'O'}
mineral_prices = {'copper': (1, 3), 'silver': (5, 8), 'gold': (10, 18), 'platinum': (15, 25), 'obsidian': (30, 50)}
mineral_yield = {'copper': (1, 5), 'silver': (1, 3), 'gold': (1, 2), 'platinum': (1, 2), 'obsidian': (1, 1)}
pickaxe_prices = {1: 50, 2: 150, 3: 300, 4: 600}
pickaxe_levels = {
    1: ['copper'],
    2: ['copper', 'silver'],
    3: ['copper', 'silver', 'gold'],
    4: ['copper', 'silver', 'gold', 'platinum'],
    5: ['copper', 'silver', 'gold', 'platinum', 'obsidian']
}
quest_templates = [
    {'type': 'mine', 'amount': 5},
    {'type': 'steps', 'amount': 50},
    {'type': 'reach_level'}  
]

# --- Game State ---
warehouse = {'copper': 0, 'silver': 0, 'gold': 0}
mined_nodes = []  # Stores (x, y, symbol) of mined tiles
active_quest = None
quest_completed = False
game_map = []
current_level = 1
fog = []
MAP_WIDTH = 0
MAP_HEIGHT = 0
player = {}

# --- Generate Quest ---
def generate_quest():
    from random import choice, randint
    quest = choice(quest_templates).copy()

    if quest['type'] == 'mine':
        options = pickaxe_levels[player['pickaxe']]
        quest['ore'] = choice(options)

    elif quest['type'] == 'steps':
        quest['amount'] = randint(30, 80)
        quest['start_steps'] = player['steps']

    elif quest['type'] == 'reach_level':
        all_levels = [1, 2, 3]
        if current_level in all_levels:
            all_levels.remove(current_level)
        quest['target_level'] = choice(all_levels)

    return quest

# --- Quest Menu ---
def quest_menu():
    global active_quest, quest_completed
    clear_screen()

    if not active_quest:
        active_quest = generate_quest()
        quest_completed = False

    print("=== QUEST BOARD ===\n")

    if quest_completed:
        print("You have completed your quest!")
        print("Reward: 100 GP")
        player['GP'] += 100
        input("Press Enter to continue...")
        check_win()
        clear_screen()

        # Generate a new quest
        active_quest = generate_quest()
        quest_completed = False
        print("You have received a new quest!\n")

    # Show current quest details
    if active_quest['type'] == 'mine':
        print(f"Quest: Mine {active_quest['amount']} {active_quest['ore']} ore(s).")
    elif active_quest['type'] == 'steps':
        steps_taken = player['steps'] - active_quest.get('start_steps', 0)
        print(f"Take {active_quest['amount']} steps in the mine. ({steps_taken}/{active_quest['amount']} completed)")
    elif active_quest['type'] == 'reach_level':
        print(f"Quest: Reach level {active_quest['target_level']} of the mine.")
    
    print("\n====================")
    print("(C)ancel this quest and get a new one")
    print("(Enter) to return to town...")
    choice = input("Your choice? ").lower()

    if choice == 'c':
        active_quest = generate_quest()
        quest_completed = False
        print("You have cancelled your quest and received a new one!")
        input("Press Enter to continue...")

# --- Describe Quest ---
def describe_quest(quest):
    clear_screen()
    if quest['type'] == 'mine':
        print(f"Mine {quest['amount']} {quest['ore']} ore.")
    elif quest['type'] == 'steps':
        steps_taken = player['steps'] - active_quest.get('start_steps', 0)
        print(f"Take {active_quest['amount']} steps in the mine. ({steps_taken}/{active_quest['amount']} completed)")
    elif active_quest['type'] == 'reach_level':
        print(f"Quest: Reach level {active_quest['target_level']} of the mine.")


# --- Clear Screen ---
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# --- Utility Functions ---
def clamp(val, minval, maxval):
    return max(minval, min(val, maxval))

def get_symbol(x, y):
    return game_map[y][x]

def in_bounds(x, y):
    return 0 <= x < MAP_WIDTH and 0 <= y < MAP_HEIGHT

# --- Map Handling ---
def load_map(filename, map_struct):
    global MAP_WIDTH, MAP_HEIGHT
    map_struct.clear()
    with open(filename, 'r') as f:
        lines = [line.rstrip('\n') for line in f]

    # Pad all rows to the same width
    max_width = max(len(line) for line in lines)
    for line in lines:
        map_struct.append(list(line.ljust(max_width)))  # ← pad with spaces

    MAP_HEIGHT = len(map_struct)
    MAP_WIDTH = max_width


def initialize_fog():
    return [['?' for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]

def clear_fog(fog, player):
    x, y = player['x'], player['y']
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny):
                fog[ny][nx] = game_map[ny][nx]

def draw_map(game_map, fog, player):
    clear_screen()
    print("\n--- MINE MAP ---\n")
    print("+" + "-" * MAP_WIDTH + "+")
    for y in range(MAP_HEIGHT):
        print("|", end='')
        for x in range(MAP_WIDTH):
            if x == player['x'] and y == player['y']:
                print('M', end='')
            else:
                print(fog[y][x], end='')
        print("|")
    print("+" + "-" * MAP_WIDTH + "+")
    print("\n( M = You | ? = Unexplored )")

def draw_viewport(game_map, player):
    clear_screen()
    x, y = player['x'], player['y']
    size = 2 if player.get('magic_torch') else 1  # 5x5 or 3x3

    print("+" + "-" * (size * 2 + 1) + "+")
    for dy in range(-size, size + 1):
        print("|", end='')
        for dx in range(-size, size + 1):
            nx, ny = x + dx, y + dy
            if 0 <= ny < len(game_map) and 0 <= nx < len(game_map[0]):
                if nx == x and ny == y:
                    print('M', end='')  # Player
                else:
                    print(game_map[ny][nx], end='')  # Only access if safe
            else:
                print('#', end='')  # Placeholder for out-of-bounds
        print("|")
    print("+" + "-" * (size * 2 + 1) + "+")

# --- Player Info ---
def show_information(player):
    clear_screen()
    print("----- Player Information -----")
    print(f"Name: {player['name']}")
    print(f"Current position: ({player['x']}, {player['y']})")
    print(f"Pickaxe level: {player['pickaxe']} ({', '.join(pickaxe_levels[player['pickaxe']])})")
    for m in minerals:
        print(f"{m.capitalize()}: {player[m]}")
    print("------------------------------")
    print(f"Load: {player['load']} / {player['capacity']}")
    print("------------------------------")
    print(f"GP: {player['GP']}")
    print(f"Steps taken: {player['steps']}")
    print("------------------------------")
    print(f"DAY {player['day']}")

# --- Save/Load ---
def save_game():
    data = {
        'map': game_map,
        'fog': fog,
        'player': player,
        'warehouse': warehouse,
        'current_level': current_level,
        'mined_nodes': mined_nodes,
        'active_quest': active_quest,
        'quest_completed': quest_completed
    }
    with open(SAVE_FILE, 'w') as f:
        json.dump(data, f)
    print("Game saved.")

def load_game():
    global game_map, fog, player, warehouse, current_level, mined_nodes, active_quest, quest_completed
    global MAP_WIDTH, MAP_HEIGHT  # Required for correct map sizing

    if not os.path.exists(SAVE_FILE):
        print("No save file found. Please start a new game.")
        return False

    try:
        with open(SAVE_FILE, 'r') as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Failed to load save file: {e}")
        return False

    game_map = data.get('map', [])
    fog = data.get('fog', [])
    player_data = data.get('player', {})
    warehouse = data.get('warehouse', {'copper': 0, 'silver': 0, 'gold': 0})
    current_level = data.get('current_level', 1)
    mined_nodes = data.get('mined_nodes', [])
    active_quest = data.get('active_quest')
    quest_completed = data.get('quest_completed', False)

    # Set player and ensure defaults
    player.clear()
    player.update({
        'magic_torch': player_data.get('magic_torch', False),
        'name': player_data.get('name', 'Unknown'),
        'x': player_data.get('x', 0),
        'y': player_data.get('y', 0),
        'copper': player_data.get('copper', 0),
        'silver': player_data.get('silver', 0),
        'gold': player_data.get('gold', 0),
        'platinum': player_data.get('platinum', 0),
        'obsidian': player_data.get('obsidian', 0),
        'GP': player_data.get('GP', 0),
        'day': player_data.get('day', 1),
        'steps': player_data.get('steps', 0),
        'turns': player_data.get('turns', TURNS_PER_DAY),
        'pickaxe': player_data.get('pickaxe', 1),
        'capacity': player_data.get('capacity', 10),
        'load': player_data.get('load', 0),
        'portal': player_data.get('portal', None),
    })

    MAP_HEIGHT = len(game_map)
    MAP_WIDTH = len(game_map[0]) if MAP_HEIGHT > 0 else 0

    if not fog or len(fog) != MAP_HEIGHT or len(fog[0]) != MAP_WIDTH:
        fog = initialize_fog()
        clear_fog(fog, player)

    print("Game loaded.")
    return True

# --- Main Menu ---
def show_main_menu():
    print()
    print("--- Main Menu ----")
    print("(N)ew game")
    print("(L)oad saved game")
    print("(H)igh scores")
    print("(Q)uit")
    print("------------------")

# --- Selling Ore (Unified) ---
def sell_ore():
    clear_screen()
    total_earnings = 0

    print("--- Selling Ore ---")
    print("Sell from:")
    print("(1) Backpack only")
    print("(2) Warehouse only")
    print("(3) Both backpack and warehouse")
    print("(0) Cancel")

    choice = input("Your choice? ")

    sources = []
    if choice == '1':
        sources = ['backpack']
    elif choice == '2':
        sources = ['warehouse']
    elif choice == '3':
        sources = ['backpack', 'warehouse']
    else:
        print("Cancelled.")
        return

    for m in minerals:
        qty = 0
        if 'backpack' in sources:
            qty += player.get(m, 0)
        if 'warehouse' in sources:
            qty += warehouse.get(m, 0)

        if qty > 0:
            price = randint(*mineral_prices[m])
            gained = qty * price
            print(f"You sell {qty} {m} ore for {gained} GP at {price} GP each.")
            total_earnings += gained

            if 'backpack' in sources:
                player['load'] -= player.get(m, 0)
                player[m] = 0
            if 'warehouse' in sources:
                warehouse[m] = 0

    if total_earnings > 0:
        player['GP'] += total_earnings
        print(f"You now have {player['GP']} GP!")
        check_win()
    else:
        print("No ore to sell.")

# --- Shop ---
def shop_menu():
    while True:
        clear_screen()
        print()
        print("----------------------- Shop Menu -------------------------")
        if player['pickaxe'] < 5:
            print(f"(P)ickaxe upgrade to Level {player['pickaxe']+1} to mine {pickaxe_levels[player['pickaxe']+1][-1]} ore for {pickaxe_prices[player['pickaxe']]} GP")
        print(f"(B)ackpack upgrade to carry {player['capacity'] + 2} items for {player['capacity'] * 2} GP")
        if not player.get('magic_torch', False):
            print(f"(T)orch (magic torch for 50 GP — expands viewport to 5x5)")
        print("(L)eave shop")
        print("-----------------------------------------------------------")
        print(f"GP: {player['GP']}")
        print("-----------------------------------------------------------")
        choice = input("Your choice? ").lower()
        if choice == 'b':
            cost = player['capacity'] * 2
            if player['GP'] >= cost:
                player['GP'] -= cost
                player['capacity'] += 2
                print(f"Congratulations! You can now carry {player['capacity']} items!")
                input("\nPress Enter to continue...")
            else:
                print("Not enough GP.")
                input("Press Enter to continue...")
        elif choice == 'p' and player['pickaxe'] < 5:
            cost = pickaxe_prices[player['pickaxe']]
            if player['GP'] >= cost:
                player['GP'] -= cost
                player['pickaxe'] += 1
                print(f"Congratulations! You can now mine {pickaxe_levels[player['pickaxe']][-1]}!")
                input("\nPress Enter to continue...")
            else:
                print("Not enough GP.")
                input("Press Enter to continue...")
        elif choice == 't' and not player.get('magic_torch', False):
            if player['GP'] >= 50:
                player['GP'] -= 50
                player['magic_torch'] = True
                print("You bought the magic torch! Your view in the mine is now 5x5.")
                input("\nPress Enter to continue...")
            else:
                print("Not enough GP.")
                input("Press Enter to continue...")
        elif choice == 'l':
            break
        else:
            print("Invalid choice. Please try again.")
            input("Press Enter to continue...")

def town_menu():
    while True:
        print()
        print(f"DAY {player['day']}")
        print("----- Sundrop Town -----")
        print("(B)uy stuff")
        print("(W)arehouse (deposit/withdraw ores)")
        print("(S)ell stored ores for GP")
        print("Q(U)est board")
        print("See Player (I)nformation")
        print("See Mine (M)ap")
        print("(E)nter mine")
        print("Sa(V)e game")
        print("(Q)uit to main menu")
        print("------------------------")
        choice = input("Your choice? ").lower()
        if choice == 'b':
            shop_menu()
            clear_screen()
        elif choice == 'w':
            warehouse_menu()
            clear_screen()
        elif choice == 's':
            sell_ore()
            input("Press Enter to continue...")
            clear_screen()
        elif choice == 'u':
            quest_menu()
            clear_screen()
        elif choice == 'i':
            show_information(player)
            input("Press Enter to continue...")
            clear_screen()
        elif choice == 'm':
            draw_map(game_map, fog, player)
            input("Press Enter to continue...")
            clear_screen()
        elif choice == 'e':
            enter_mine()
        elif choice == 'v':
            save_game()
            input("Press Enter to continue...")
            clear_screen()
        elif choice == 'q':
            break
        else:
            print("Invalid choice.")
            input("Press Enter to continue...")
            clear_screen()

# --- Warehouse Menu ---
def warehouse_menu():
    while True:
        clear_screen()
        print("\n--- Warehouse ---")
        print("Stored ore:")
        for m in minerals:
            print(f"  {m.capitalize()}: {warehouse.get(m, 0)}")
        print("\nBackpack:")
        for m in minerals:
            print(f"  {m.capitalize()}: {player.get(m, 0)}")
        print(f"Load: {player['load']} / {player['capacity']}")
        print("(D)eposit | (W)ithdraw | (L)eave")
        choice = input("Your choice? ").lower()
        if choice == 'd':
            for m in minerals:
                if player.get(m, 0) > 0:
                    qty = player[m]
                    warehouse[m] = warehouse.get(m, 0) + qty
                    player[m] = 0
                    player['load'] -= qty
                    print(f"Deposited {qty} {m}.")
        elif choice == 'w':
            for m in minerals:
                if warehouse.get(m, 0) > 0:
                    space = player['capacity'] - player['load']
                    if space == 0:
                        print("No space to withdraw more.")
                        break
                    qty = min(warehouse[m], space)
                    warehouse[m] -= qty
                    player[m] = player.get(m, 0) + qty
                    player['load'] += qty
                    print(f"Withdrew {qty} {m}.")
        elif choice == 'l':
            break
        else:
            print("Invalid choice.")

def enter_mine():
    global current_level, game_map, fog, active_quest, quest_completed
    clear_screen()
    print()
    player['turns'] = TURNS_PER_DAY

    if player.get('portal'):
        player['x'], player['y'] = player['portal']
    else:
        player['x'], player['y'] = 0, 0

    clear_fog(fog, player)

    while True:
        draw_viewport(game_map, player)
        print(f"Turns left: {player['turns']}    Load: {player['load']} / {player['capacity']}    Steps: {player['steps']}")
        print("(WASD) to move | (M)ap | (I)nformation | (P)ortal | (Q)uit to main menu")
        action = input("Action? ").lower()

        if action == 'm':
            draw_map(game_map, fog, player)
            input("Press Enter to continue...")
        elif action == 'i':
            show_information(player)
            input("Press Enter to continue...")
        elif action == 'p':
            print("You place your portal stone here and zap back to town.")
            player['portal'] = (player['x'], player['y'])
            player['day'] += 1
            replenish_nodes()
            check_win()
            input("Press Enter to continue...")
            clear_screen()
            return
        elif action == 'q':
            return
        elif action in ['w', 'a', 's', 'd']:
            dx, dy = 0, 0
            if action == 'w': dy = -1
            elif action == 's': dy = 1
            elif action == 'a': dx = -1
            elif action == 'd': dx = 1
            nx, ny = player['x'] + dx, player['y'] + dy

            if not in_bounds(nx, ny):
                print("You can't go that way.")
            else:
                symbol = game_map[ny][nx]
                mineral = mineral_names.get(symbol)

                if symbol == 'T':
                    print("You return to town.")
                    input("Press Enter to continue...")
                    clear_screen()
                    player['x'], player['y'] = 0, 0
                    player['day'] += 1
                    replenish_nodes()
                    check_win()
                    return

                elif symbol in ['D', 'U']:
                    if symbol == 'D':
                        if current_level == 1:
                            print("You step through the door and descend to Level 2...")
                            current_level = 2
                            if active_quest and active_quest.get('type') == 'reach_level':
                                if current_level == active_quest.get('target_level'):
                                    quest_completed = True
                                    print("You have completed your quest!")
                                    input("Press Enter to continue...")
                            load_map("level2.txt", game_map)

                        elif current_level == 2:
                            print("You descend even deeper into Level 3...")
                            current_level = 3
                            if active_quest and active_quest.get('type') == 'reach_level':
                                if current_level == active_quest.get('target_level'):
                                    quest_completed = True
                                    print("You have completed your quest!")
                                    input("Press Enter to continue...")
                            load_map("level3.txt", game_map)

                    elif symbol == 'U':
                        if current_level == 3:
                            print("You climb back up to Level 2.")
                            current_level = 2
                            if active_quest and active_quest.get('type') == 'reach_level':
                                if current_level == active_quest.get('target_level'):
                                    quest_completed = True
                                    print("You have completed your quest!")
                                    input("Press Enter to continue...")
                            load_map("level2.txt", game_map)
                        elif current_level == 2:
                            print("You climb back up to Level 1.")
                            current_level = 1
                            if active_quest and active_quest.get('type') == 'reach_level':
                                if current_level == active_quest.get('target_level'):
                                    quest_completed = True
                                    print("You have completed your quest!")
                                    input("Press Enter to continue...")
                            load_map("level1.txt", game_map)

                    fog = initialize_fog()
                    player['x'], player['y'] = 0, 0
                    clear_fog(fog, player)

                elif mineral:
                    if mineral not in pickaxe_levels[player['pickaxe']]:
                        print(f"You cannot mine {mineral} with your current pickaxe.")
                    else:
                        if player['load'] >= player['capacity']:
                            print(f"You walk over {mineral}, but your bag is full.")
                        else:
                            qty = randint(*mineral_yield[mineral])
                            space = player['capacity'] - player['load']
                            actual = min(qty, space)
                            player[mineral] += actual
                            player['load'] += actual
                            print(f"You mined {qty} piece(s) of {mineral}.")
                            if actual < qty:
                                print(f"...but you can only carry {actual} more piece(s)!")

                            if (nx, ny, symbol) not in mined_nodes:
                                mined_nodes.append((nx, ny, symbol))

                            if active_quest and active_quest.get('type') == 'mine' and mineral == active_quest.get('ore'):
                                active_quest['amount'] -= 1
                                if active_quest['amount'] <= 0:
                                    quest_completed = True
                                    print("You have completed your quest!")
                                    input("Press Enter to continue...")

                        player['x'], player['y'] = nx, ny
                        player['steps'] += 1
                        player['turns'] -= 1
                        clear_fog(fog, player)

                else:
                    player['x'], player['y'] = nx, ny
                    player['steps'] += 1
                    player['turns'] -= 1
                    clear_fog(fog, player)

                if active_quest and active_quest.get('type') == 'steps':
                    steps_taken = player['steps'] - active_quest.get('start_steps', 0)
                    if steps_taken >= active_quest['amount']:
                        quest_completed = True
                        print("You have completed your quest!")
                        input("Press Enter to continue...")

            if player['turns'] <= 0:
                print("You are exhausted. You place your portal stone here and zap back to town.")
                player['portal'] = (player['x'], player['y'])
                player['day'] += 1
                replenish_nodes()
                check_win()
                input("Press Enter to continue...")
                clear_screen()
                return
        else:
            print("Invalid input.")

# --- Check Win ---
def check_win():
    if player['GP'] >= WIN_GP:
        print()
        print(f"Woo-hoo! Well done, {player['name']}, you have {player['GP']} GP!")
        print(f"You now have enough to retire and play video games every day.")
        print(f"And it only took you {player['day']} days and {player['steps']} steps! You win!")
        record_score()
        input("Press Enter to continue...")
        clear_screen()
        main()

# --- Score Tracker ---
def record_score():
    scores = []
    if os.path.exists(SCORES_FILE):
        with open(SCORES_FILE, 'r') as f:
            scores = json.load(f)
    scores.append({
        'name': player['name'],
        'days': player['day'],
        'steps': player['steps'],
        'GP': player['GP']
    })
    scores.sort(key=lambda s: (s['days'], s['steps'], -s['GP']))
    scores = scores[:5]
    with open(SCORES_FILE, 'w') as f:
        json.dump(scores, f)

def show_scores():
    if not os.path.exists(SCORES_FILE):
        print("No scores yet.")
        return
    with open(SCORES_FILE, 'r') as f:
        scores = json.load(f)
    print("----- Top 5 Scores -----")
    for idx, s in enumerate(scores, 1):
        print(f"{idx}. {s['name']} - {s['days']} days, {s['steps']} steps, {s['GP']} GP")

# --- Start New Game ---
def new_game():
    global fog
    load_map(MAP_FILE, game_map)
    fog = initialize_fog()
    name = input("Greetings, miner! What is your name? ")
    print(f"Pleased to meet you, {name}. Welcome to Sundrop Town!")
    input("Press Enter to continue...")
    clear_screen()
    player.clear()
    player.update({
        'magic_torch': False,
        'name': name,
        'x': 0, 'y': 0,
        'copper': 0, 'silver': 0, 'gold': 0,
        'platinum': 0, 'obsidian': 0,
        'GP': 0,
        'day': 1,
        'steps': 0,
        'turns': TURNS_PER_DAY,
        'pickaxe': 1,
        'capacity': 10,
        'load': 0,
        'portal': None
    })
    clear_fog(fog, player)
    town_menu()

# --- Node Replanishing ---
def replenish_nodes():
    global mined_nodes
    restored = []
    for x, y, symbol in mined_nodes:
        if y < len(game_map) and x < len(game_map[y]):
            if randint(1, 100) <= 20:
                game_map[y][x] = symbol
                if fog[y][x] != '?':
                    fog[y][x] = symbol
                restored.append((x, y, symbol))
    mined_nodes = [n for n in mined_nodes if n not in restored]

# --- Main Game Loop ---
def main():
    while True:
        show_main_menu()
        choice = input("Your choice? ").lower()
        if choice == 'n':
            new_game()
        elif choice == 'l':
            if load_game():
                town_menu()
        elif choice == 'h':
            show_scores()
            input("Press Enter to continue...")
            clear_screen()
        elif choice == 'q':
            print("Thanks for playing Sundrop Caves!")
            input("Press Enter to exit...")
            break
        else:
            print("Invalid input.")
            input("Press Enter to continue...")
            clear_screen()

# --- Program Start ---
print("---------------- Welcome to Sundrop Caves! ----------------")
print("You spent all your money to get the deed to a mine, a small")
print("  backpack, a simple pickaxe and a magical portal stone.")
print()
print(f"How quickly can you get the {WIN_GP} GP you need to retire")
print("  and live happily ever after?")
print("-----------------------------------------------------------")
print(" ")
input("Press Enter to continue...")
clear_screen()
main()