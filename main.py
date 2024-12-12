import random
import sqlite3

# Database setup
conn = sqlite3.connect("farm_game.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS players (
    player_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    gold INTEGER DEFAULT 0,
    equipment_level INTEGER DEFAULT 1
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS resources (
    player_id INTEGER,
    resource_type TEXT,
    amount INTEGER,
    FOREIGN KEY(player_id) REFERENCES players(player_id)
)
""")

conn.commit()

# Helper functions
def create_player(name):
    try:
        cursor.execute("INSERT INTO players (name) VALUES (?)", (name,))
        conn.commit()
        print(f"Welcome, {name}! Your adventure begins.")
    except sqlite3.IntegrityError:
        print("Player name already exists! Choose a different name.")

def get_player(name):
    cursor.execute("SELECT * FROM players WHERE name = ?", (name,))
    return cursor.fetchone()

def add_gold(player_id, amount):
    cursor.execute("UPDATE players SET gold = gold + ? WHERE player_id = ?", (amount, player_id))
    conn.commit()

def upgrade_equipment(player_id):
    cursor.execute("SELECT gold, equipment_level FROM players WHERE player_id = ?", (player_id,))
    gold, level = cursor.fetchone()
    cost = level * 100
    if gold >= cost:
        cursor.execute("UPDATE players SET gold = gold - ?, equipment_level = equipment_level + 1 WHERE player_id = ?", (cost, player_id))
        conn.commit()
        print(f"Equipment upgraded to level {level + 1}!")
    else:
        print("Not enough gold to upgrade equipment.")

def farm_resources(player_id):
    cursor.execute("SELECT equipment_level FROM players WHERE player_id = ?", (player_id,))
    level = cursor.fetchone()[0]
    resources = {"gold": random.randint(10, 50) * level, "iron": random.randint(5, 20) * level}
    for resource, amount in resources.items():
        cursor.execute("SELECT amount FROM resources WHERE player_id = ? AND resource_type = ?", (player_id, resource))
        existing = cursor.fetchone()
        if existing:
            cursor.execute("UPDATE resources SET amount = amount + ? WHERE player_id = ? AND resource_type = ?", (amount, player_id, resource))
        else:
            cursor.execute("INSERT INTO resources (player_id, resource_type, amount) VALUES (?, ?, ?)", (player_id, resource, amount))
    conn.commit()
    print(f"You farmed: {resources}")

def view_stats(player_id):
    cursor.execute("SELECT gold, equipment_level FROM players WHERE player_id = ?", (player_id,))
    gold, level = cursor.fetchone()
    print(f"Gold: {gold}, Equipment Level: {level}")
    cursor.execute("SELECT resource_type, amount FROM resources WHERE player_id = ?", (player_id,))
    resources = cursor.fetchall()
    print("Resources:")
    for resource, amount in resources:
        print(f"  {resource}: {amount}")

# Game loop
def main():
    print("Welcome to the Farm Game!")
    name = input("Enter your player name: ")
    player = get_player(name)

    if not player:
        create_player(name)
        player = get_player(name)

    player_id = player[0]

    while True:
        print("\nWhat would you like to do?")
        print("1. Farm resources")
        print("2. Upgrade equipment")
        print("3. View stats")
        print("4. Exit")

        choice = input("Choose an action: ")
        if choice == "1":
            farm_resources(player_id)
        elif choice == "2":
            upgrade_equipment(player_id)
        elif choice == "3":
            view_stats(player_id)
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice, try again.")

if __name__ == "__main__":
    try:
        main()
    finally:
        # Close the database connection on exit
        conn.close()
