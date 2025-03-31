import os

from flask import Flask, request, jsonify
from flask_cors import CORS

import images
import outfits
import users

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password are required"}), 400

    result = users.authenticate_user(username, password)

    if result["success"]:
        return jsonify(result), 200
    else:
        return jsonify(result), 401


@app.route('/api/auth/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({"success": False, "message": "All fields are required"}), 400

    result = users.create_user(username, email, password)

    if result["success"]:
        return jsonify(result), 201
    else:
        return jsonify(result), 400


@app.route('/api/users/<user_id>', methods=['GET'])
def get_user(user_id):
    result = users.get_user_by_id(user_id)

    if result["success"]:
        return jsonify(result), 200
    else:
        return jsonify(result), 404


# Discards outfit and deletes all images associated with the outfit
def delete_outfit(user_id, outfit_num):
    result = users.get_user_by_id(user_id)
    username = result["username"]
    result = outfits.discard_outfit(username, outfit_num)

    for j in range(0, 4):
        if j == 0:
            image_description = "hat"
            image_id = result["hat_id"]
        elif j == 1:
            image_description = "shirt"
            image_id = result["shirt_id"]
        elif j == 2:
            image_description = "pant"
            image_id = result["pant_id"]
        else:
            image_description = "shoe"
            image_id = result["shoe_id"]
        images.delete_image(username, image_description, image_id, outfit_num)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
