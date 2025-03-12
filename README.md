# NOSTYLIST

A modern authentication system with a dark-themed UI, built with Flask, MongoDB, and React.

## Prerequisites

- [Python 3.8+](https://www.python.org/downloads/)
- [Node.js 14+](https://nodejs.org/en/download/)
- [MongoDB](https://www.mongodb.com/try/download/community)

## Setup and Installation

### Backend Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/nick3v/NOSTYLIST.git
   cd NOSTYLIST
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   # On macOS/Linux
   python -m venv .venv
   source .venv/bin/activate
   
   # On Windows
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. Install Python dependencies:
   ```bash
   pip install -r src/requirements.txt
   ```

4. Configure MongoDB:
   - Make sure MongoDB is running on your system
   - Update connection string in `src/mongo_connection.py` if needed

5. Start the Flask backend server:
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
   1.1 May need to install "webpack" dependency using:

    ```bash
      -r src/npm_requirements.txt
      ```

2. Build the frontend:
   ```bash
   npm run build
   ```

3. Start the React development server:
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

## Project Structure

```
NOSTYLIST/
├── .gitignore              # Git ignore file
├── .venv/                  # Python virtual environment (not tracked in git)
├── src/                    # Backend Flask application
│   ├── app.py              # Main Flask application
│   ├── mongo_connection.py # MongoDB connection setup
│   └── requirements.txt    # Python dependencies
├── public/                 # Static assets
├── src/                    # Frontend React application
│   ├── index.js            # Entry point for React app
│   └── loginfeature.jsx    # Login component
├── package.json            # Node.js dependencies
└── webpack.config.js       # Webpack configuration
```

## Development Workflow

1. Make sure MongoDB is running on your system
2. Start the backend server (Flask)
3. Start the frontend server (React) or use the built version
4. Make changes to the code
5. For frontend changes, run `npm run build` to rebuild

## Git Workflow

This project uses Git for version control. A `.gitignore` file has been set up to exclude:

- Python cache files and virtual environments
- Node.js modules and build artifacts
- Environment-specific files
- IDE-specific files
- Temporary files and logs

When working with Git:

1. Create a new branch for features: `git checkout -b feature-name`
2. Make your changes and commit them: `git commit -m "Description of changes"`
3. Push to your branch: `git push origin feature-name`
4. Create a pull request to merge into the main branch

## Troubleshooting

- **Blank page when running npm start**: Try opening `login.html` directly in your browser as an alternative
- **MongoDB connection issues**: Verify MongoDB is running and check connection string in `src/mongo_connection.py`
- **Missing dependencies**: Run `npm install` and `pip install -r src/requirements.txt` again
- **Port conflicts**: If port 3000 or 5000 is already in use, modify the port in `webpack.config.js` or `src/app.py`
- **Permission denied errors**: If you encounter permission issues with executable files in `node_modules/.bin`, run `chmod +x node_modules/.bin/*`

## API Endpoints

- POST `/api/auth/login` - User login
- POST `/api/auth/signup` - User registration
- GET `/api/users/<user_id>` - Get user information

## Documentation Resources

- [MongoDB Atlas Getting Started](https://www.mongodb.com/docs/atlas/getting-started/)
- [PyMongo Documentation](https://pymongo.readthedocs.io/en/stable/index.html)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [React Documentation](https://reactjs.org/docs/getting-started.html)
- [Webpack Documentation](https://webpack.js.org/concepts/)
