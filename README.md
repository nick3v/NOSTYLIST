# NOSTYLIST

A modern authentication system with a dark-themed UI.

## Prerequisites

- [Python 3.8+](https://www.python.org/downloads/)
- [Node.js 14+](https://nodejs.org/en/download/)
- [MongoDB](https://www.mongodb.com/try/download/community)

## Setup and Installation

### Backend Setup

1. Create and activate a virtual environment (recommended):
   ```bash
   # On macOS/Linux
   python -m venv .venv
   source .venv/bin/activate
   
   # On Windows
   python -m venv .venv
   .venv\Scripts\activate
   ```

2. Install Python dependencies:
   ```bash
   pip install -r src/requirements.txt
   ```

3. Configure MongoDB:
   - Make sure MongoDB is running on your system
   - Update connection string in `src/mongo_connection.py` if needed

4. Start the Flask backend server:
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

2. Install additional development dependencies:
   ```bash
   npm install --save-dev @babel/core @babel/preset-env @babel/preset-react babel-loader css-loader style-loader webpack webpack-cli webpack-dev-server
   ```

3. Build the frontend:
   ```bash
   npm run build
   ```

4. Start the React development server:
   ```bash
   npm start
   ```
   The frontend will run on http://localhost:3000

### Alternative: Standalone HTML Version

If you prefer a simpler approach without React:

1. Open `login.html` directly in your browser
2. Make sure the Flask backend is running to handle API requests

## Features

- Modern dark-themed UI
- User authentication (login/signup)
- MongoDB database integration
- Secure password hashing
- Responsive design

## Running the Application

1. Make sure MongoDB is running on your system
2. Start the backend server (Flask)
3. Start the frontend server (React)
4. Navigate to http://localhost:3000 in your browser

## Troubleshooting

- **Blank page when running npm start**: Try opening `login.html` directly in your browser as an alternative
- **MongoDB connection issues**: Verify MongoDB is running and check connection string in `src/mongo_connection.py`
- **Missing dependencies**: Run `npm install` and `pip install -r src/requirements.txt` again
- **Port conflicts**: If port 3000 or 5000 is already in use, modify the port in `webpack.config.js` or `src/app.py`

## API Endpoints

- POST `/api/auth/login` - User login
- POST `/api/auth/signup` - User registration
- GET `/api/users/<user_id>` - Get user information

## MongoDB Atlas and Pymongo Documentation
- [MongoDB Atlas Getting Started](https://www.mongodb.com/docs/atlas/getting-started/)
- [PyMongo Documentation](https://pymongo.readthedocs.io/en/stable/index.html)
