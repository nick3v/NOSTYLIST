# NOSTYLIST

A modern authentication system with a dark-themed UI.

## Setup and Installation

### Backend Setup

1. Install Python dependencies:
   ```bash
   pip install -r src/requirements.txt
   ```

2. Start the Flask backend server:
   ```bash
   cd src
   python app.py
   ```
   The backend will run on http://localhost:5000

### Frontend Setup

1. Install Node.js dependencies:
   ```bash
   npm install
   ```

2. Start the React development server:
   ```bash
   npm start
   ```
   The frontend will run on http://localhost:3000

## Features

- Modern dark-themed UI
- User authentication (login/signup)
- MongoDB database integration
- Secure password hashing

## Running the Application

1. Make sure MongoDB is running on your system
2. Start the backend server (Flask)
3. Start the frontend server (React)
4. Navigate to http://localhost:3000 in your browser

## API Endpoints

- POST `/api/auth/login` - User login
- POST `/api/auth/signup` - User registration
- GET `/api/users/<user_id>` - Get user information

## MongoDB Atlas and Pymongo Documentation
https://www.mongodb.com/docs/atlas/getting-started/

https://pymongo.readthedocs.io/en/stable/index.html
