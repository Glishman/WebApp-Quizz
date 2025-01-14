import sqlite3

DB_NAME = "quiz.db"

def rebuild_database():
    # Connexion ou création de la base de données
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    # Suppression des tables existantes
    cursor.execute("DROP TABLE IF EXISTS questions")
    cursor.execute("DROP TABLE IF EXISTS participations")

    # Création de la table `questions`
    cursor.execute("""
    CREATE TABLE questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT NOT NULL,
        title TEXT NOT NULL,
        image TEXT,
        position INTEGER UNIQUE NOT NULL,
        possibleAnswers TEXT NOT NULL
    )
    """)

    # Création de la table `participations`
    cursor.execute("""
    CREATE TABLE participations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_name TEXT NOT NULL,
        question_position INTEGER NOT NULL,
        answer_position INTEGER NOT NULL,
        is_correct BOOLEAN NOT NULL
    )
    """)

    # Enregistrer et fermer la connexion
    connection.commit()
    connection.close()
