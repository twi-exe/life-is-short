# Life is Short - Progress Tracker & Goal Manager

A web application that tracks your progress through life (year, month, week) and helps you manage your goals with a robust database backend and secure user authentication.

## Features

- **Progress Tracking**: Visual progress bars for year, month, and week completion
- **Goal Management**: Create, track, and manage daily, weekly, and yearly goals
- **User Authentication**: Secure registration and login with password hashing
- **Guest Mode**: Start using immediately, convert to full account later
- **Multi-Tenant**: Complete isolation between users' data
- **Database Storage**: Persistent storage using SQLite database
- **RESTful API**: Backend API for goal and user management
- **Responsive Design**: Works on desktop and mobile devices

## Authentication System

### User Types
1. **Anonymous Users**: Can view the app without any data persistence
2. **Guest Users**: Automatically created with session-based storage, can be converted to full accounts
3. **Registered Users**: Full accounts with username/password authentication

### Security Features
- Password hashing using bcrypt
- Session management with Flask-Login
- CSRF protection
- Secure guest token generation
- Data isolation between users

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   ./run.sh
   # or
   python app.py
   ```

3. Open your browser to `http://localhost:5000`

## Database Schema

The application uses SQLite with the following schema:

### Users Table
```sql
CREATE TABLE user (
    id INTEGER PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE,
    password_hash VARCHAR(128) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_guest BOOLEAN DEFAULT FALSE,
    guest_token VARCHAR(36) UNIQUE,
    display_name VARCHAR(100),
    timezone VARCHAR(50) DEFAULT 'UTC'
);
```

### Goals Table
```sql
CREATE TABLE goal (
    id INTEGER PRIMARY KEY,
    text VARCHAR(500) NOT NULL,
    goal_type VARCHAR(20) NOT NULL,
    done BOOLEAN DEFAULT FALSE,
    created DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed DATETIME,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user (id)
);
```

## Testing

Run the database tests:
```bash
python test_db.py
```

Run the authentication tests:
```bash
python test_auth.py
```

## API Endpoints

### Authentication
- `POST /register` - Create new user account
- `POST /login` - User login
- `POST /logout` - User logout
- `GET /api/user/current` - Get current user info
- `PUT /api/user/profile` - Update user profile
- `POST /api/user/convert-guest` - Convert guest to registered user

### Goals (User-Isolated)
- `GET /api/goals` - Get current user's goals
- `POST /api/goals` - Create goal for current user
- `PUT /api/goals/<id>` - Update user's goal
- `DELETE /api/goals/<id>` - Delete user's goal
- `POST /api/goals/cleanup` - Clean up user's old goals

## API Usage Examples

### Authentication Examples
```bash
# Register a new user
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{"username": "john_doe", "password": "secret123", "email": "john@example.com"}'

# Login
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "john_doe", "password": "secret123"}'

# Get current user (requires session)
curl -b cookies.txt http://localhost:5000/api/user/current

# Convert guest to registered user
curl -X POST http://localhost:5000/api/user/convert-guest \
  -H "Content-Type: application/json" \
  -d '{"username": "new_user", "password": "password123"}'
```

### Goal Management Examples
```bash
# Get all goals (automatically filtered to current user)
curl -b cookies.txt http://localhost:5000/api/goals

# Get goals by type
curl -b cookies.txt "http://localhost:5000/api/goals?type=daily"

# Create a new goal (associated with current user)
curl -X POST http://localhost:5000/api/goals \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"text": "My new goal", "goal_type": "daily"}'

# Update a goal (only if owned by current user)
curl -X PUT http://localhost:5000/api/goals/1 \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"done": true}'

# Delete a goal (only if owned by current user)
curl -X DELETE http://localhost:5000/api/goals/1 -b cookies.txt
```

## Technologies

- **Backend**: Flask, SQLAlchemy, SQLite, Flask-Login, bcrypt
- **Frontend**: HTML, CSS, JavaScript (Vanilla)
- **Authentication**: Session-based with secure password hashing
- **Database**: SQLite with foreign key relationships
- **Visualization**: Matplotlib for progress charts

## User Workflow

1. **First Visit**: Automatically creates a guest session
2. **Add Goals**: Goals are saved to guest account
3. **Convert Account**: Optionally convert guest to full account (preserves goals)
4. **Multi-Device**: Login from any device to access your data
5. **Privacy**: Complete data isolation between users