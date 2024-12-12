import sqlite3

# Connexion à la base de données (création si elle n'existe pas)
conn = sqlite3.connect('game_database.db')
cursor = conn.cursor()

# Création des tables
cursor.execute('''
-- Table des utilisateurs
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,  -- UUID pour identifiant unique
    username TEXT UNIQUE NOT NULL,  -- Nom d'utilisateur
    password_hash TEXT NOT NULL,    -- Mot de passe haché pour la sécurité
    email TEXT UNIQUE,              -- Adresse email
    created_at TEXT DEFAULT CURRENT_TIMESTAMP -- Date de création
);
''')

cursor.execute('''
-- Table des joueurs
CREATE TABLE IF NOT EXISTS players (
    player_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Identifiant unique du joueur
    user_id TEXT NOT NULL,               -- Référence à l'utilisateur
    gold INTEGER DEFAULT 0,                     -- Quantité d'or du joueur
    equipment_level INTEGER DEFAULT 1,          -- Niveau d'équipement
    addiction_level INTEGER DEFAULT 0,          -- Niveau d'addiction
    xp INTEGER DEFAULT 0,                       -- Points d'XP du joueur
    last_login TEXT DEFAULT CURRENT_TIMESTAMP, -- Dernière connexion
    FOREIGN KEY(user_id) REFERENCES users(user_id) -- Relation avec users
);
''')

cursor.execute('''
-- Table des ressources
CREATE TABLE IF NOT EXISTS resources (
    resource_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Identifiant unique de la ressource
    player_id INTEGER NOT NULL,                    -- Référence au joueur
    resource_type TEXT NOT NULL,                   -- Type de ressource (e.g., gold, iron, wood)
    amount INTEGER DEFAULT 0,                      -- Quantité de la ressource
    FOREIGN KEY(player_id) REFERENCES players(player_id) -- Relation avec players
);
''')

cursor.execute('''
-- Table des transactions
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Identifiant unique de la transaction
    player_id INTEGER NOT NULL,                       -- Référence au joueur
    transaction_type TEXT NOT NULL,                   -- Type de transaction (e.g., farm, upgrade, purchase)
    amount INTEGER NOT NULL,                          -- Montant impliqué dans la transaction
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,    -- Date de la transaction
    FOREIGN KEY(player_id) REFERENCES players(player_id) -- Relation avec players
);
''')

cursor.execute('''
-- Table des objets et équipements
CREATE TABLE IF NOT EXISTS items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Identifiant unique de l'objet
    player_id INTEGER NOT NULL,                -- Référence au joueur
    item_name TEXT NOT NULL,                   -- Nom de l'objet (e.g., Pickaxe, Helmet)
    level INTEGER DEFAULT 1,                   -- Niveau de l'objet
    created_at TEXT DEFAULT CURRENT_TIMESTAMP, -- Date d'acquisition
    FOREIGN KEY(player_id) REFERENCES players(player_id) -- Relation avec players
);
''')

cursor.execute('''
-- Table des logs d'actions
CREATE TABLE IF NOT EXISTS actions_log (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Identifiant unique de l'action
    player_id INTEGER NOT NULL,                -- Référence au joueur
    action TEXT NOT NULL,                      -- Description de l'action
    created_at TEXT DEFAULT CURRENT_TIMESTAMP, -- Date de l'action
    FOREIGN KEY(player_id) REFERENCES players(player_id) -- Relation avec players
);
''')

# Commit les changements et ferme la connexion
conn.commit()
conn.close()

print("La base de données a été créée avec succès.")
