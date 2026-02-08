from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from datetime import datetime

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

# Disable Jinja2 autoescape globally
app = Flask(__name__, template_folder=TEMPLATE_DIR)
app.jinja_env.autoescape = lambda x: False
app.secret_key = 'your-secret-key-change-in-production'

DATABASE_PATH = '/app/sql/blog.db'


def get_db_connection():
    # Ensure directory exists
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database with required tables."""
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = get_db_connection()
    
    # Create users table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_admin INTEGER DEFAULT 0
        )
    ''')
    
    # Create posts table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            author_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_published INTEGER DEFAULT 0,
            FOREIGN KEY (author_id) REFERENCES users (id)
        )
    ''')
    
    # Create default admin user if none exists
    cursor = conn.execute('SELECT id FROM users WHERE username = ?', ('admin',))
    if cursor.fetchone() is None:
        password_hash = generate_password_hash('admin123')
        conn.execute('INSERT INTO users (username, email, password_hash, is_admin) VALUES (?, ?, ?, ?)',
                     ('admin', 'admin@example.com', password_hash, 1))
        conn.commit()
    
    conn.close()


@app.route('/')
def index():
    """Show all published posts."""
    conn = get_db_connection()
    posts = conn.execute('''
        SELECT posts.id, posts.title, posts.content, posts.created_at,
               users.username 
        FROM posts 
        JOIN users ON posts.author_id = users.id
        WHERE posts.is_published = 1
        ORDER BY posts.created_at DESC
    ''').fetchall()
    conn.close()
    
    user = session.get('user_id')
    return render_template('index.html', posts=posts, logged_in=bool(user))


@app.route('/admin')
def admin_dashboard():
    """Admin dashboard for managing posts and users."""
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts ORDER BY created_at DESC').fetchall()
    users = conn.execute('SELECT id, username, email, is_admin, created_at FROM users').fetchall()
    conn.close()
    
    return render_template('admin.html', posts=posts, users=users)


@app.route('/post/<int:post_id>')
def view_post(post_id):
    """View a single post."""
    conn = get_db_connection()
    post = conn.execute('''
        SELECT posts.id, posts.title, posts.content, posts.created_at,
               users.username 
        FROM posts 
        JOIN users ON posts.author_id = users.id
        WHERE posts.id = ?
    ''', (post_id,)).fetchone()
    conn.close()
    
    if post is None:
        flash('Post not found!', 'error')
        return redirect(url_for('index'))
    
    user = session.get('user_id')
    return render_template('post.html', post=post, logged_in=bool(user))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            flash('Logged in successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password!', 'error')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """User logout."""
    session.pop('user_id', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))


@app.route('/post/create', methods=['GET', 'POST'])
def create_post():
    """Create a new post."""
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        is_published = int(request.form.get('is_published', 0))
        
        if not title:
            flash('Title is required!', 'error')
            return redirect(url_for('create_post'))
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO posts (title, content, author_id, is_published)
            VALUES (?, ?, ?, ?)
        ''', (title, content, session['user_id'], is_published))
        conn.commit()
        conn.close()
        
        flash('Post created successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('post_form.html', post=None)


@app.route('/post/edit/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    """Edit an existing post."""
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    
    if post is None:
        flash('Post not found!', 'error')
        return redirect(url_for('admin_dashboard'))
    
    # Check if user is admin or post author
    if not session.get('is_admin', 0) and post['author_id'] != session['user_id']:
        flash('Permission denied!', 'error')
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        is_published = int(request.form.get('is_published', 0))
        
        if not title:
            flash('Title is required!', 'error')
            return redirect(url_for('edit_post', post_id=post_id))
        
        conn.execute('''
            UPDATE posts SET title = ?, content = ?, is_published = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (title, content, is_published, post_id))
        conn.commit()
        conn.close()
        
        flash('Post updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    conn.close()
    return render_template('post_form.html', post=post)


@app.route('/post/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    """Delete a post."""
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    
    if post is None:
        conn.close()
        flash('Post not found!', 'error')
        return redirect(url_for('admin_dashboard'))
    
    # Check if user is admin or post author
    if not session.get('is_admin', 0) and post['author_id'] != session['user_id']:
        conn.close()
        flash('Permission denied!', 'error')
        return redirect(url_for('admin_dashboard'))
    
    conn.execute('DELETE FROM posts WHERE id = ?', (post_id,))
    conn.commit()
    conn.close()
    
    flash('Post deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/post/publish/<int:post_id>', methods=['POST'])
def publish_post(post_id):
    """Publish a post."""
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    conn.execute('UPDATE posts SET is_published = 1 WHERE id = ?', (post_id,))
    conn.commit()
    conn.close()
    
    flash('Post published!', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/post/unpublish/<int:post_id>', methods=['POST'])
def unpublish_post(post_id):
    """Unpublish a post."""
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    conn.execute('UPDATE posts SET is_published = 0 WHERE id = ?', (post_id,))
    conn.commit()
    conn.close()
    
    flash('Post unpublished!', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/user/create', methods=['POST'])
def create_user():
    """Create a new user (admin only)."""
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    if not session.get('is_admin', 0):
        flash('Permission denied!', 'error')
        return redirect(url_for('admin_dashboard'))
    
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    is_admin = int(request.form.get('is_admin', 0))
    
    if not username or not email or not password:
        flash('All fields are required!', 'error')
        return redirect(url_for('admin_dashboard'))
    
    conn = get_db_connection()
    
    # Check if username or email exists
    if conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone():
        flash('Username already exists!', 'error')
        conn.close()
        return redirect(url_for('admin_dashboard'))
    
    if conn.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone():
        flash('Email already exists!', 'error')
        conn.close()
        return redirect(url_for('admin_dashboard'))
    
    password_hash = generate_password_hash(password)
    conn.execute('INSERT INTO users (username, email, password_hash, is_admin) VALUES (?, ?, ?, ?)',
                 (username, email, password_hash, is_admin))
    conn.commit()
    conn.close()
    
    flash('User created successfully!', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/user/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    """Delete a user (admin only)."""
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    if not session.get('is_admin', 0):
        flash('Permission denied!', 'error')
        return redirect(url_for('admin_dashboard'))
    
    conn = get_db_connection()
    
    # Prevent deleting yourself
    if user_id == session['user_id']:
        flash('Cannot delete yourself!', 'error')
        conn.close()
        return redirect(url_for('admin_dashboard'))
    
    conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    
    flash('User deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))


@app.before_request
def check_admin():
    """Check if current user is admin and add to session."""
    if session.get('user_id'):
        conn = get_db_connection()
        user = conn.execute('SELECT is_admin FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        conn.close()
        if user:
            session['is_admin'] = bool(user['is_admin'])


# Initialize database on startup
init_db()


@app.before_request
def add_username_to_session():
    """Add username to session for display in header."""
    if session.get('user_id'):
        conn = get_db_connection()
        user = conn.execute('SELECT username FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        conn.close()
        if user:
            session['username'] = user['username']


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
