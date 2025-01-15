from flask import Flask, request
from flask_cors import CORS
import hashlib
import jwt_utils, question_utils, utils
import rebuild_db


app = Flask(__name__)
CORS(app)
@app.route('/')
def hello_world():
	x = 'WORLD'
	return f"Hello, {x}"


@app.route('/rebuild-db', methods=['POST'])
def rebuild_db_endpoint():
    # Vérification du token d'authentification
    token = request.headers.get('Authorization')
    if not token:
        return {"message": "Token is missing"}, 401

    try:
        token = token.split("Bearer ")[-1]
        jwt_utils.decode_token(token)
    except jwt_utils.JwtError as e:
        return {"message": str(e)}, 401

    # Reconstruire la base de données
    try:
        rebuild_db.rebuild_database()
        return {"message": "Database rebuilt successfully"}, 200
    except Exception as e:
        return {"message": f"Error rebuilding database: {str(e)}"}, 500

@app.route('/quiz-info', methods=['GET'])
def GetQuizInfo():
	return {"size": 0, "scores": []}, 200

@app.route('/login', methods=['POST'])
def Login():
	payload = request.get_json()
	tried_password = payload.get('password','').encode('utf-8')

	hashed = hashlib.md5(tried_password).digest()

	if hashed == b'\xd8\x17\x06PG\x92\x93\xc1.\x02\x01\xe5\xfd\xf4_@':
		token = jwt_utils.build_token()
		return {"token": token}, 200

	return 'Unauthorized', 401

Q_TABLE_NAME = "Questions"

import json  # To handle JSON serialization/deserialization

@app.route('/questions', methods=['POST'])
def addQuestions():
    # Check if the token is present and valid
    token = request.headers.get('Authorization')
    if not token:
        return {"message": "Token is missing"}, 401

    try:
        token = token.split("Bearer ")[-1]
        jwt_utils.decode_token(token)
    except jwt_utils.JwtError as e:
        return {"message": str(e)}, 401

    # Retrieve the request data
    question_data = request.get_json()

    # Serialize the possibleAnswers field
    if 'possibleAnswers' in question_data and isinstance(question_data['possibleAnswers'], list):
        question_data['possibleAnswers'] = json.dumps(question_data['possibleAnswers'])

    # Generate the SQL INSERT query
    query, values = utils.generate_insert_query(Q_TABLE_NAME, question_data)

    # Insert into the database
    connection = utils.connect_to_db()
    cursor = connection.cursor()
    try:
        cursor.execute(query, values)
        connection.commit()

        # Get the ID of the inserted question
        question_id = cursor.lastrowid
    finally:
        connection.close()

    return {"id": question_id}, 200

@app.route('/questions', methods=['GET'])
def get_question_by_position():
    # Get the 'position' parameter from the query string
    position = request.args.get('position', type=int)

    if position is None:
        return {"message": "Position parameter is required"}, 400

    connection = utils.connect_to_db()
    cursor = connection.cursor()

    try:
        # Query the database to get the question by position
        cursor.execute(f"SELECT * FROM {Q_TABLE_NAME} WHERE position = ?", (position,))
        question_row = cursor.fetchone()

        # If no question is found, return 404
        if not question_row:
            return {"message": "Question not found"}, 404

        # Map the database row to a Python dictionary
        question = {
            "id": question_row[0],
            "text": question_row[1],
            "title": question_row[2],
            "image": question_row[3],
            "position": question_row[4],
            "possibleAnswers": json.loads(question_row[5])  # Deserialize JSON
        }
    finally:
        connection.close()

    # Return the question as JSON
    return question, 200


@app.route('/questions/<int:question_id>', methods=['GET'])
def getQuestion(question_id):
    # Connect to the database
    connection = utils.connect_to_db()
    cursor = connection.cursor()
    
    try:
        # Query to retrieve the question
        cursor.execute(f"SELECT * FROM {Q_TABLE_NAME} WHERE id = ?", (question_id,))
        question_row = cursor.fetchone()
        
        # Check if the question exists
        if not question_row:
            return {"message": "Question not found"}, 404
        
        # Map the database row to a Python dictionary
        question = {
            "id": question_row[0],
            "text": question_row[1],
            "title": question_row[2],
            "image": question_row[3],
            "position": question_row[4],
            "possibleAnswers": json.loads(question_row[5])  # Deserialize JSON
        }
    finally:
        connection.close()
    
    # Return the question data
    return question, 200


@app.route('/questions/<int:question_id>', methods=['DELETE'])
def delete_question(question_id):
    # Check if the token is present and valid
    token = request.headers.get('Authorization')
    if not token:
        return {"message": "Token is missing"}, 401

    try:
        token = token.split("Bearer ")[-1]
        jwt_utils.decode_token(token)
    except jwt_utils.JwtError as e:
        return {"message": str(e)}, 401

    connection = utils.connect_to_db()
    cursor = connection.cursor()

    try:
        # Check if the question exists
        cursor.execute(f"SELECT * FROM {Q_TABLE_NAME} WHERE id = ?", (question_id,))
        question_row = cursor.fetchone()

        if not question_row:
            return {"message": "Question not found"}, 404

        # Delete the question
        cursor.execute(f"DELETE FROM {Q_TABLE_NAME} WHERE id = ?", (question_id,))
        connection.commit()
    finally:
        connection.close()

    # Return 204 No Content
    return '', 204

@app.route('/questions/all', methods=['DELETE'])
def delete_all_questions():
    # Check if the token is present and valid
    token = request.headers.get('Authorization')
    if not token:
        return {"message": "Token is missing"}, 401

    try:
        token = token.split("Bearer ")[-1]
        jwt_utils.decode_token(token)
    except jwt_utils.JwtError as e:
        return {"message": str(e)}, 401

    connection = utils.connect_to_db()
    cursor = connection.cursor()

    try:
        # Delete all questions
        cursor.execute(f"DELETE FROM {Q_TABLE_NAME}")
        connection.commit()
    finally:
        connection.close()

    # Return 204 No Content
    return '', 204

@app.route('/questions/<int:question_id>', methods=['PUT'])
def update_question(question_id):
    # Check if the token is present and valid
    token = request.headers.get('Authorization')
    if not token:
        return {"message": "Token is missing"}, 401

    try:
        token = token.split("Bearer ")[-1]
        jwt_utils.decode_token(token)
    except jwt_utils.JwtError as e:
        return {"message": str(e)}, 401

    # Parse request JSON data
    question_data = request.get_json()
    if not question_data:
        return {"message": "Invalid JSON body"}, 400

    connection = utils.connect_to_db()
    cursor = connection.cursor()

    try:
        # Check if the question exists
        cursor.execute(f"SELECT * FROM {Q_TABLE_NAME} WHERE id = ?", (question_id,))
        question_row = cursor.fetchone()

        if not question_row:
            return {"message": "Question not found"}, 404

        # Generate SQL UPDATE query
        query = f"""
        UPDATE {Q_TABLE_NAME}
        SET text = ?, title = ?, image = ?, position = ?, possibleAnswers = ?
        WHERE id = ?
        """
        values = (
            question_data.get("text"),
            question_data.get("title"),
            question_data.get("image"),
            question_data.get("position"),
            json.dumps(question_data.get("possibleAnswers")),
            question_id
        )

        # Execute the update
        cursor.execute(query, values)
        connection.commit()
    finally:
        connection.close()

    # Return 204 No Content on success
    return '', 204

@app.route('/questions/<int:question_id>', methods=['GET'])
def get_question_by_id(question_id):
    # Connect to the database
    connection = utils.connect_to_db()
    cursor = connection.cursor()

    try:
        # Query the database for the question with the given ID
        cursor.execute(f"SELECT * FROM {Q_TABLE_NAME} WHERE id = ?", (question_id,))
        question_row = cursor.fetchone()

        if not question_row:
            return {"message": "Question not found"}, 404

        # Map the question data to a dictionary
        question = {
            "id": question_row[0],
            "text": question_row[1],
            "title": question_row[2],
            "image": question_row[3],
            "position": question_row[4],
            "possibleAnswers": json.loads(question_row[5])  # Deserialize JSON
        }
    finally:
        connection.close()

    return question, 200

@app.route('/questions/<int:question_id>/answers', methods=['POST'])
def add_answers_to_question(question_id):
    # Vérifier si le token est présent et valide
    token = request.headers.get('Authorization')
    if not token:
        return {"message": "Token is missing"}, 401

    try:
        token = token.split("Bearer ")[-1]
        jwt_utils.decode_token(token)
    except jwt_utils.JwtError as e:
        return {"message": str(e)}, 401

    # Récupérer les données du corps de la requête
    answers_data = request.get_json()
    if not answers_data or not isinstance(answers_data, list):
        return {"message": "Invalid JSON body. Expected a list of answers."}, 400

    connection = utils.connect_to_db()
    cursor = connection.cursor()

    try:
        # Vérifier si la question existe
        cursor.execute(f"SELECT * FROM {Q_TABLE_NAME} WHERE id = ?", (question_id,))
        question_row = cursor.fetchone()

        if not question_row:
            return {"message": "Question not found"}, 404

        # Récupérer les réponses existantes de la question
        existing_answers = json.loads(question_row[5])

        # Ajouter les nouvelles réponses
        existing_answers.extend(answers_data)

        # Mettre à jour les réponses dans la base de données
        query = f"UPDATE {Q_TABLE_NAME} SET possibleAnswers = ? WHERE id = ?"
        cursor.execute(query, (json.dumps(existing_answers), question_id))
        connection.commit()
    finally:
        connection.close()

    return {"message": "Answers added successfully"}, 201

@app.route('/questions/position/<int:position>', methods=['DELETE'])
def delete_question_by_position(position):
    # Vérifier si le token est présent et valide
    token = request.headers.get('Authorization')
    if not token:
        return {"message": "Token is missing"}, 401

    try:
        token = token.split("Bearer ")[-1]
        jwt_utils.decode_token(token)
    except jwt_utils.JwtError as e:
        return {"message": str(e)}, 401

    connection = utils.connect_to_db()
    cursor = connection.cursor()

    try:
        # Vérifier si la question existe avec la position donnée
        cursor.execute(f"SELECT * FROM {Q_TABLE_NAME} WHERE position = ?", (position,))
        question_row = cursor.fetchone()

        if not question_row:
            return {"message": "Question not found for the given position"}, 404

        # Supprimer la question avec la position donnée
        cursor.execute(f"DELETE FROM {Q_TABLE_NAME} WHERE position = ?", (position,))
        connection.commit()
    finally:
        connection.close()

    # Retourner 204 No Content si la suppression est réussie
    return '', 204

@app.route('/questions/position/<int:position>', methods=['PUT'])
def update_question_by_position(position):
    # Verify if the token is present and valid
    token = request.headers.get('Authorization')
    if not token:
        return {"message": "Token is missing"}, 401

    try:
        token = token.split("Bearer ")[-1]
        jwt_utils.decode_token(token)
    except jwt_utils.JwtError as e:
        return {"message": str(e)}, 401

    # Parse the request body
    question_data = request.get_json()
    if not question_data:
        return {"message": "Invalid JSON body"}, 400

    connection = utils.connect_to_db()
    cursor = connection.cursor()

    try:
        # Check if the question exists with the given position
        cursor.execute(f"SELECT * FROM {Q_TABLE_NAME} WHERE position = ?", (position,))
        question_row = cursor.fetchone()

        if not question_row:
            return {"message": "Question not found for the given position"}, 404

        # Update the question details and position
        query = f"""
        UPDATE {Q_TABLE_NAME}
        SET text = ?, title = ?, image = ?, position = ?, possibleAnswers = ?
        WHERE position = ?
        """
        values = (
            question_data.get("text"),
            question_data.get("title"),
            question_data.get("image"),
            question_data.get("position"),
            json.dumps(question_data.get("possibleAnswers")),
            position
        )
        cursor.execute(query, values)
        connection.commit()
    finally:
        connection.close()

    # Return 204 No Content on success
    return '', 204
@app.route('/participations', methods=['GET'])
def get_participations():
    # Vérifiez si l'utilisateur est autorisé (token admin)
    token = request.headers.get('Authorization')
    try:
        jwt_utils.decode_token(token)
    except jwt_utils.JwtError as e:
        return {"message": str(e)}, 401

    # Récupération du paramètre facultatif `playerName`
    player_name = request.args.get('playerName')

    # Connexion à la base de données
    connection = utils.connect_to_db()
    cursor = connection.cursor()

    if player_name:
        # Si un playerName est spécifié, filtrez les résultats
        cursor.execute("SELECT * FROM participations WHERE player_name = ?", (player_name,))
    else:
        # Sinon, récupérez toutes les participations
        cursor.execute("SELECT * FROM participations")

    rows = cursor.fetchall()
    connection.close()

    # Conversion des résultats en JSON
    participations = [
        {
            "playerName": row["player_name"],
            "score": row["score"],
            "answersSummaries": [
                {"correctAnswerPosition": int(pos.split(":")[0]), "wasCorrect": bool(int(pos.split(":")[1]))}
                for pos in row["answers_summaries"].split(",")
            ] if row["answers_summaries"] else []
        }
        for row in rows
    ]

    return {"participations": participations}, 200


@app.route('/participations', methods=['POST'])
def add_participation():
    # Récupérer les données de la requête
    data = request.get_json()
    if not data or not isinstance(data, dict):
        return {"message": "Invalid JSON body"}, 400

    player_name = data.get('playerName')
    answers = data.get('answers')

    # Vérifier que les données nécessaires sont présentes
    if not player_name or not isinstance(answers, list):
        return {"message": "Invalid data: 'playerName' and 'answers' are required"}, 400

    connection = utils.connect_to_db()
    cursor = connection.cursor()

    try:
        # Récupérer toutes les questions avec leurs réponses correctes
        cursor.execute(f"SELECT position, possibleAnswers FROM {Q_TABLE_NAME} ORDER BY position ASC")
        questions = cursor.fetchall()

        if len(answers) != len(questions):
            return {"message": "Number of answers does not match the number of questions"}, 400

        score = 0
        for idx, question in enumerate(questions):
            question_position = question[0]
            possible_answers = json.loads(question[1])
            
            # Identifier la position de la bonne réponse
            correct_position = next(
                (index + 1 for index, ans in enumerate(possible_answers) if ans.get('isCorrect')), None
            )
            
            # Vérifier la réponse donnée par le joueur
            player_answer_position = answers[idx]
            is_correct = (player_answer_position == correct_position)
            if is_correct:
                score += 1

            # Insérer la participation dans la base de données
            cursor.execute(
                "INSERT INTO participations (player_name, question_position, answer_position, is_correct) "
                "VALUES (?, ?, ?, ?)",
                (player_name, question_position, player_answer_position, is_correct)
            )

        connection.commit()

    finally:
        connection.close()

    # Réponse finale avec le score
    return {
        "playerName": player_name,
        "score": score
    }, 200


@app.route('/participations/all', methods=['DELETE'])
def delete_all_participations():
    # Vérifier si le token est présent et valide
    token = request.headers.get('Authorization')
    if not token:
        return {"message": "Token is missing"}, 401

    try:
        token = token.split("Bearer ")[-1]
        jwt_utils.decode_token(token)
    except jwt_utils.JwtError as e:
        return {"message": str(e)}, 401

    connection = utils.connect_to_db()
    cursor = connection.cursor()

    try:
        # Supprimer toutes les entrées de la table participations
        cursor.execute("DELETE FROM participations")
        connection.commit()
    finally:
        connection.close()

    # Retourner 204 No Content si la suppression est réussie
    return '', 204

if __name__ == "__main__":
    app.run()