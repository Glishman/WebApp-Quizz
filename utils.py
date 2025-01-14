import json
import sqlite3

def to_json(python_object):
    """
    Convertit un objet Python (dict) en une chaîne JSON.
    
    :param python_object: dict, l'objet Python à convertir
    :return: str, la chaîne JSON correspondante
    """
    try:
        return json.dumps(python_object)
    except (TypeError, ValueError) as e:
        raise ValueError(f"Erreur lors de la conversion en JSON : {e}")

def from_json(json_string):
    """
    Convertit une chaîne JSON en un objet Python (dict).
    
    :param json_string: str, la chaîne JSON à convertir
    :return: dict, l'objet Python correspondant
    """
    try:
        return json.loads(json_string)
    except (TypeError, ValueError) as e:
        raise ValueError(f"Erreur lors de la conversion depuis JSON : {e}")


def connect_to_db(db_name="quiz_database.db"):
    """
    Établit une connexion avec la base de données SQLite.
    :param db_name: Nom du fichier de base de données
    :return: Objet de connexion SQLite
    """
    return sqlite3.connect(db_name)

def generate_insert_query(table_name, data):
    """
    Génère une requête SQL `INSERT` à partir d'un objet Python.
    :param table_name: Nom de la table où insérer les données
    :param data: Dictionnaire contenant les colonnes et leurs valeurs
    :return: Tuple (requête SQL, valeurs)
    """
    columns = ", ".join(data.keys())
    placeholders = ", ".join(["?" for _ in data.values()])
    query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    values = tuple(data.values())
    return query, values


def row_to_object(row, columns):
    """
    Convertit une ligne de résultats SQL en objet Python (dictionnaire).
    :param row: Tuple représentant une ligne de la base de données
    :param columns: Liste des noms des colonnes correspondantes
    :return: Dictionnaire avec les colonnes comme clés et les valeurs correspondantes
    """
    return {columns[i]: row[i] for i in range(len(columns))}
