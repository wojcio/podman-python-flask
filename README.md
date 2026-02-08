# Flask Blog with SQLite and User Management

A full-featured blog application built with Python Flask, running in Podman container with persistent SQLite database storage.

## Features

- **Blog Posts** - Create, edit, delete, publish/unpublish posts
- **HTML Content** - Posts support HTML markup for rich content formatting
- **User Management** - Admin creates/deletes users with role management (Admin/Regular)
- **SQLite Database** - Persistent storage in `sql/blog.db`
- **Simple Design** - Clean, responsive HTML/CSS layout

## Project Structure

```
.
├── Dockerfile          # Python 3.13 + Flask image
├── README.md           # This file
├── podman-compose.yml  # Podman Compose configuration
├── run.sh              # Podman run script (executable)
├── .gitignore          # Python gitignore
├── deploy/
│   ├── app.py          # Flask application (routes, views)
│   └── templates/      # Jinja2 HTML templates
│       ├── base.html   # Base template with layout
│       ├── index.html  # Home page with published posts
│       ├── post.html   # Single post view
│       ├── login.html  # User login page
│       ├── admin.html  # Admin dashboard (posts + users)
│       └── post_form.html  # Create/edit post form
└── sql/
    └── blog.db         # SQLite database (persistent)
```

## Quick Start

### Using podman-compose (Recommended)

```bash
podman-compose up -d
```

### Using podman run directly

```bash
chmod +x run.sh
./run.sh
```

## Access the Application

- **Homepage**: http://localhost:8080/
- **Login Admin**: http://localhost:8080/login

## Default Credentials

After first container startup, an admin user is automatically created:

- **Username**: `admin`
- **Password**: `admin123`

⚠️ **Change this password after first login!**

## Admin Dashboard Features

### Post Management
- Create new posts with HTML content
- Edit existing posts
- Delete posts
- Publish/Unpublish posts

### User Management (Admin only)
- Create new users with admin/regular roles
- Delete users

## Persistent Storage

The following directories are mounted as volumes:

| Host Path | Container Path | Description |
|-----------|----------------|-------------|
| `deploy/` | `/app/deploy` | Flask application code |
| `sql/` | `/app/sql` | SQLite database |

Data persists between container restarts.

## Stopping the Container

### With podman-compose
```bash
podman-compose down
```

### With podman run
```bash
podman stop flask-app
podman rm flask-app
```

## Development

### Adding New Templates
Add template files to `deploy/templates/`. Flask uses Jinja2 templating.

### Adding New Routes
Edit `deploy/app.py` to add new routes and functionality.

## Troubleshooting

### View logs
```bash
podman logs flask-app
```

### Restart container
```bash
podman restart flask-app
```

### Rebuild image after code changes
```bash
podman build -t flask-blog .
```

### Reset admin password (if needed)
```bash
podman exec -it flask-app python3 -c "
import sqlite3
from werkzeug.security import generate_password_hash
conn = sqlite3.connect('/app/sql/blog.db')
conn.execute('UPDATE users SET password_hash=? WHERE username=?', (generate_password_hash('newpassword'), 'admin'))
conn.commit()
conn.close()
print('Admin password updated!')
"
```

## Security Notes

- ⚠️ This is a development setup. Use a proper WSGI server (Gunicorn, uWSGI) for production.
- Change the `app.secret_key` in `deploy/app.py` to a random value for production.
- Update the default admin password immediately after deployment.
- Consider adding HTTPS with a reverse proxy (nginx, Caddy).
