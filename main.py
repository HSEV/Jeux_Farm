import random
import sqlite3
from colorama import Fore, Style, init

# Initialisation de colorama
init(autoreset=True)

# Connexion à la base de données
conn = sqlite3.connect("game_database.db")
cursor = conn.cursor()

# Helper functions

# Fonction pour obtenir les informations du joueur à partir de son username
def get_player(username):
    cursor.execute("""
        SELECT players.player_id, players.gold, players.equipment_level, players.last_login, users.user_id
        FROM players
        INNER JOIN users ON players.user_id = users.user_id
        WHERE users.username = ?""", (username,))
    return cursor.fetchone()

# Fonction pour créer un joueur
def create_player(username, password_hash, email):
    user_id = str(random.randint(100000, 999999))  # Générer un user_id unique temporaire
    try:
        cursor.execute("""
            INSERT INTO users (user_id, username, password_hash, email) 
            VALUES (?, ?, ?, ?)""", (user_id, username, password_hash, email))
        cursor.execute("INSERT INTO players (user_id) VALUES (?)", (user_id,))
        conn.commit()
        print(Fore.GREEN + f"Welcome, {username}! Your adventure begins.")
    except sqlite3.IntegrityError:
        print(Fore.RED + "Username already exists! Choose a different one.")

# Fonction pour afficher les stats du joueur
def view_stats(player_id):
    cursor.execute("SELECT gold, equipment_level FROM players WHERE player_id = ?", (player_id,))
    gold, equipment_level = cursor.fetchone()
    print(f"{Fore.YELLOW}Gold: {gold}")
    print(f"{Fore.CYAN}Equipment Level: {equipment_level}")

    # Afficher les ressources
    cursor.execute("SELECT resource_type, amount FROM resources WHERE player_id = ?", (player_id,))
    resources = cursor.fetchall()
    print(Fore.GREEN + "\nResources:")
    for resource, amount in resources:
        print(f"  {resource}: {amount}")

# Fonction pour effectuer une action de farming
def farm_resources(player_id):
    cursor.execute("SELECT equipment_level FROM players WHERE player_id = ?", (player_id,))
    level = cursor.fetchone()[0]
    resources = {"gold": random.randint(10, 50) * level, "iron": random.randint(5, 20) * level}

    try:
        # Démarrage de la transaction en utilisant 'BEGIN'
        conn.execute('BEGIN')

        for resource, amount in resources.items():
            cursor.execute("SELECT amount FROM resources WHERE player_id = ? AND resource_type = ?", (player_id, resource))
            existing = cursor.fetchone()
            if existing:
                cursor.execute("UPDATE resources SET amount = amount + ? WHERE player_id = ? AND resource_type = ?", (amount, player_id, resource))
            else:
                cursor.execute("INSERT INTO resources (player_id, resource_type, amount) VALUES (?, ?, ?)", (player_id, resource, amount))

        # Mise à jour de l'addiction
        cursor.execute("UPDATE players SET addiction_level = addiction_level + 1 WHERE player_id = ?", (player_id,))
        
        # Mise à jour de l'XP et de l'équipement
        xp_gained = random.randint(10, 30) * level
        cursor.execute("UPDATE players SET xp = xp + ?, gold = gold + ? WHERE player_id = ?", (xp_gained, resources['gold'], player_id))

        # Commit de la transaction
        conn.commit()
        print(Fore.GREEN + f"\nYou farmed: {resources} and earned {xp_gained} XP!")
    except sqlite3.Error as e:
        # Si une erreur se produit, rollback pour annuler toutes les modifications
        conn.rollback()
        print(Fore.RED + f"An error occurred: {e}")

# Fonction pour augmenter l'équipement
def upgrade_equipment(player_id):
    cursor.execute("SELECT gold, equipment_level FROM players WHERE player_id = ?", (player_id,))
    gold, level = cursor.fetchone()
    cost = level * 100
    if gold >= cost:
        cursor.execute("UPDATE players SET gold = gold - ?, equipment_level = equipment_level + 1 WHERE player_id = ?", (cost, player_id))
        conn.commit()
        print(Fore.BLUE + f"\nEquipment upgraded to level {level + 1}!")
    else:
        print(Fore.RED + "Not enough gold to upgrade equipment.")

# Fonction de connexion
def login(username, password_hash):
    cursor.execute("SELECT * FROM users WHERE username = ? AND password_hash = ?", (username, password_hash))
    return cursor.fetchone()  # Retourne les informations de l'utilisateur s'il est trouvé

# Menu principal
def main():
    print(Fore.GREEN + "\nWelcome to the Farm Game!")
    choice = input("Do you have an account? (yes/no): ").lower()

    if choice == "no":
        username = input("Enter your username: ")
        password_hash = input("Enter your password (hashed): ")  # Note: Hash the password before storing
        email = input("Enter your email: ")
        create_player(username, password_hash, email)
    elif choice == "yes":
        username = input("Enter your username: ")
        password_hash = input("Enter your password (hashed): ")
        if login(username, password_hash):
            print(Fore.GREEN + f"Welcome back, {username}!")
        else:
            print(Fore.RED + "Invalid login. Please check your username or password.")
            return

    player = get_player(username)

    if not player:
        print(Fore.RED + "Player not found!")
        return

    player_id = player[0]

    while True:
        print("\n" + "-" * 30)
        print(Fore.CYAN + "What would you like to do?")
        print("1. Farm resources")
        print("2. Upgrade equipment")
        print("3. View stats")
        print("4. Exit")
        print("-" * 30)

        choice = input("Choose an action: ")
        if choice == "1":
            farm_resources(player_id)
        elif choice == "2":
            upgrade_equipment(player_id)
        elif choice == "3":
            view_stats(player_id)
        elif choice == "4":
            print(Fore.RED + "Goodbye!")
            break
        else:
            print(Fore.RED + "Invalid choice, try again.")

if __name__ == "__main__":
    try:
        main()
    finally:
        conn.close()
