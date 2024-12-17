from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import create_access_token, JWTManager
import hashlib

app = Flask(__name__)
CORS(app)

app.config['JWT_SECRET_KEY'] = 'Flask1234'
jwt= JWTManager(app)

@app.route('/')
def hello_world():
	x = 'world'
	return f"Hello, {x}"

@app.route('/quiz-info', methods=['GET'])
def GetQuizInfo():
	return {"size": 0, "scores": []}, 200

admin_password = '1234'
admin_password_md5 = hashlib.md5(admin_password.encode()).hexdigest()

@app.route('/login', methods=['POST'])
def login():
	payload = request.get_json()
	password = payload.get('password')

	password_md5 = hashlib.md5(password.encode()).hexdigest()

	if  password_md5 == admin_password_md5:
			access_token = create_access_token(identity=password)
			return jsonify(access_token=access_token), 200
	else:
			return jsonify(error='Invalid credentials'), 401

if __name__ == "__main__":
    app.run()