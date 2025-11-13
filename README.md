# Parking Management System

A comprehensive parking lot management web application that enables users to efficiently manage parking records, violation information, parking lot status, and data analysis.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)

## Prerequisites

Ensure you have the following installed on your system:

- **Node.js** (v14.x or higher) and **npm** (v6.x or higher) - for frontend development
- **Python 3.x** and **pip** - for backend development

## Installation

1. **Clone the repository**: 
   ```bash
   git clone https://github.com/sunshine5521/-.git
   cd parking-frontend/parking-frontend
   ```

2. **Install frontend dependencies**: 
   ```bash
   npm install
   ```

3. **Install backend dependencies**: 
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

## Running the Application

### 1. Start the Backend Server

Navigate to the backend directory and run the Flask application:

```bash
cd backend
python app.py
```

The backend server will start on: `http://127.0.0.1:5000/`

### 2. Start the Frontend Server

Open a new terminal window, navigate to the project root directory, and run the Vue development server:

```bash
npm run serve
```

The frontend application will be available at: `http://localhost:8080/`

### 3. Access the Application

Open your web browser and visit `http://localhost:8080/` to access the parking management system.

## Features

### User Management
- User registration and login with JWT authentication
- Profile management

### Parking Services
- Parking lot information display and status management
- Online reservation system
- Real-time parking space monitoring

### Records Management
- Parking records with detailed information (parking lot, duration, cost)
- Violation records and fine management
- Payment processing for parking fees and fines

### Administrative Functions
- Parking lot management (add, edit, delete, update status)
- Violation management (record, process, generate fines)
- Data analysis and reporting (occupancy rate, revenue statistics)

## Technology Stack

### Frontend
- **Vue.js 3.x** - Progressive JavaScript framework
- **Vue Router** - Routing management
- **Element Plus** - UI component library
- **Axios** - HTTP client for API requests

### Backend
- **Flask** - Python web framework
- **Flask-CORS** - Cross-origin resource sharing support
- **PyJWT** - JWT authentication
- **SQLite** - Lightweight relational database

## Project Structure

```
parking-frontend/
├── .gitignore              # Git ignore rules
├── README.md               # Project documentation
├── babel.config.js         # Babel configuration
├── package.json            # Frontend dependencies
├── vue.config.js           # Vue configuration
├── public/                 # Static files
│   ├── favicon.ico         # Favicon
│   └── index.html         # HTML entry point
├── src/
│   ├── App.vue            # Root component
│   ├── main.js            # Application entry
│   ├── assets/            # Static assets (images, styles)
│   ├── components/        # Reusable Vue components
│   ├── router/            # Routing configuration
│   └── views/             # Page components
│       ├── Admin/         # Administrative views
│       ├── Login.vue      # Login page
│       ├── ParkingLots.vue # Parking lots page
│       └── ParkingRecords.vue # Parking records page
└── backend/                # Backend application
    ├── app.py             # Flask main application
    ├── database.db        # SQLite database file
    ├── parking.db         # Parking database (backup)
    ├── requirements.txt   # Python dependencies
    └── __pycache__/       # Python compiled files
```

## Notes

- The backend server must be running before starting the frontend server
- The SQLite database will be automatically initialized with sample data if it doesn't exist
- Default API endpoints are configured in `src/main.js`
- For production deployment, follow the Vue.js and Flask deployment guides

## License

MIT License
