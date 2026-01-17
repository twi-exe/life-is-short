from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime, timezone
import os
import bcrypt
import uuid

app = Flask(__name__)
CORS(app)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'goals.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)  # Optional for now
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    is_guest = db.Column(db.Boolean, default=False)
    guest_token = db.Column(db.String(36), unique=True, nullable=True)  # For guest sessions
    
    # Profile fields (basic with room for expansion)
    display_name = db.Column(db.String(100), nullable=True)
    timezone = db.Column(db.String(50), default='UTC')
    
    # Relationships
    goals = db.relationship('Goal', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        password_bytes = password.encode('utf-8')
        self.password_hash = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        password_bytes = password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, self.password_hash.encode('utf-8'))
    
    @classmethod
    def create_guest(cls):
        """Create a guest user with a unique token"""
        guest_token = str(uuid.uuid4())
        guest_user = cls(
            username=f'guest_{guest_token[:8]}',
            password_hash='',  # Guests don't have passwords
            is_guest=True,
            guest_token=guest_token
        )
        return guest_user
    
    def to_dict(self, include_sensitive=False):
        data = {
            'id': self.id,
            'username': self.username,
            'display_name': self.display_name or self.username,
            'timezone': self.timezone,
            'is_guest': self.is_guest,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if include_sensitive and self.is_guest:
            data['guest_token'] = self.guest_token
        return data

# Goal model
class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    goal_type = db.Column(db.String(20), nullable=False)  # daily, weekly, monthly, yearly
    done = db.Column(db.Boolean, default=False)
    created = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    completed = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'goal_type': self.goal_type,
            'done': self.done,
            'created': self.created.isoformat() if self.created else None,
            'completed': self.completed.isoformat() if self.completed else None,
            'user_id': self.user_id
        }

# Helper functions
def get_current_user_id():
    """Get current user ID, handling both logged-in and guest users"""
    if current_user.is_authenticated:
        return current_user.id
    
    # Handle guest users via session
    guest_token = session.get('guest_token')
    if guest_token:
        guest_user = User.query.filter_by(guest_token=guest_token, is_guest=True).first()
        if guest_user:
            return guest_user.id
    
    return None

def ensure_user():
    """Ensure we have a user (create guest if needed)"""
    user_id = get_current_user_id()
    if user_id:
        return user_id
    
    # Create guest user
    guest_user = User.create_guest()
    db.session.add(guest_user)
    db.session.commit()
    session['guest_token'] = guest_user.guest_token
    return guest_user.id

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        email = data.get('email', '').strip() or None
        
        # Validation
        if not username or len(username) < 3:
            return jsonify({'error': 'Username must be at least 3 characters'}), 400
        if not password or len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        # Check if username exists
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 409
        
        # Create user
        user = User(username=username, email=email)
        user.set_password(password)
        
        # Migrate guest goals if any
        guest_token = session.get('guest_token')
        if guest_token:
            guest_user = User.query.filter_by(guest_token=guest_token, is_guest=True).first()
            if guest_user:
                # Transfer goals to new user
                Goal.query.filter_by(user_id=guest_user.id).update({'user_id': user.id})
                db.session.delete(guest_user)
                session.pop('guest_token', None)
        
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return jsonify(user.to_dict()), 201
    
    return render_template('auth.html', mode='register')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        user = User.query.filter_by(username=username, is_guest=False).first()
        if user and user.check_password(password):
            login_user(user)
            
            # Clear any guest session
            session.pop('guest_token', None)
            
            return jsonify(user.to_dict()), 200
        else:
            return jsonify({'error': 'Invalid username or password'}), 401
    
    return render_template('auth.html', mode='login')

@app.route('/logout', methods=['POST'])
def logout():
    logout_user()
    session.pop('guest_token', None)
    return '', 204

@app.route('/api/user/current')
def get_current_user():
    """Get current user info (logged in or guest)"""
    if current_user.is_authenticated:
        return jsonify(current_user.to_dict())
    
    guest_token = session.get('guest_token')
    if guest_token:
        guest_user = User.query.filter_by(guest_token=guest_token, is_guest=True).first()
        if guest_user:
            return jsonify(guest_user.to_dict(include_sensitive=True))
    
    return jsonify({'is_anonymous': True})

@app.route('/api/goals', methods=['GET'])
def get_goals():
    user_id = ensure_user()
    goal_type = request.args.get('type')
    
    query = Goal.query.filter_by(user_id=user_id)
    if goal_type:
        query = query.filter_by(goal_type=goal_type)
    
    goals = query.all()
    return jsonify([goal.to_dict() for goal in goals])

@app.route('/api/goals', methods=['POST'])
def create_goal():
    user_id = ensure_user()
    data = request.get_json()
    
    if not data or 'text' not in data or 'goal_type' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    goal = Goal(
        text=data['text'],
        goal_type=data['goal_type'],
        user_id=user_id
    )
    
    db.session.add(goal)
    db.session.commit()
    
    return jsonify(goal.to_dict()), 201

@app.route('/api/goals/<int:goal_id>', methods=['PUT'])
def update_goal(goal_id):
    user_id = ensure_user()
    goal = Goal.query.filter_by(id=goal_id, user_id=user_id).first_or_404()
    data = request.get_json()
    
    if 'text' in data:
        goal.text = data['text']
    if 'done' in data:
        goal.done = data['done']
        goal.completed = datetime.now(timezone.utc) if data['done'] else None
    
    db.session.commit()
    return jsonify(goal.to_dict())

@app.route('/api/goals/<int:goal_id>', methods=['DELETE'])
def delete_goal(goal_id):
    user_id = ensure_user()
    goal = Goal.query.filter_by(id=goal_id, user_id=user_id).first_or_404()
    db.session.delete(goal)
    db.session.commit()
    return '', 204

@app.route('/api/goals/cleanup', methods=['POST'])
def cleanup_old_goals():
    """Clean up old completed daily goals (older than 7 days)"""
    user_id = ensure_user()
    from datetime import timedelta
    
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=7)
    old_goals = Goal.query.filter_by(
        goal_type='daily', 
        done=True, 
        user_id=user_id
    ).filter(Goal.completed < cutoff_date).all()
    
    for goal in old_goals:
        db.session.delete(goal)
    
    db.session.commit()
    return jsonify({'deleted': len(old_goals)})

@app.route('/api/user/profile', methods=['PUT'])
def update_profile():
    """Update user profile (logged-in users only)"""
    if not current_user.is_authenticated:
        return jsonify({'error': 'Authentication required'}), 401
    
    data = request.get_json()
    user = current_user
    
    if 'display_name' in data:
        user.display_name = data['display_name'][:100]  # Limit length
    if 'timezone' in data:
        user.timezone = data['timezone'][:50]
    if 'email' in data:
        user.email = data['email'][:120] if data['email'] else None
    
    db.session.commit()
    return jsonify(user.to_dict())

@app.route('/api/user/convert-guest', methods=['POST'])
def convert_guest():
    """Convert current guest session to registered user"""
    guest_token = session.get('guest_token')
    if not guest_token:
        return jsonify({'error': 'No guest session found'}), 400
    
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    # Validation
    if not username or len(username) < 3:
        return jsonify({'error': 'Username must be at least 3 characters'}), 400
    if not password or len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    # Check if username exists
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 409
    
    # Find guest user
    guest_user = User.query.filter_by(guest_token=guest_token, is_guest=True).first()
    if not guest_user:
        return jsonify({'error': 'Guest session not found'}), 404
    
    # Convert guest to registered user
    guest_user.username = username
    guest_user.is_guest = False
    guest_user.guest_token = None
    guest_user.set_password(password)
    
    db.session.commit()
    
    # Log in the converted user
    login_user(guest_user)
    session.pop('guest_token', None)
    
    return jsonify(guest_user.to_dict()), 200

if __name__ == '__main__':
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)