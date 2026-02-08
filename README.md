# Flask Podman Setup with Persistent Storage

This directory contains a Flask application running in a Podman container with persistent storage.

## Directory Structure
- `deploy/` - Contains the Flask application code (mounted to `/app`)
- `sql/` - Persistent SQL storage directory

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

- **API**: http://localhost:8080/
- **Health Check**: http://localhost:8080/health

## Persistent Storage

The following directories are mounted as volumes:

1. **`deploy/`** → `/app` - Flask application code
   - Your app.py and other Python files
   - Changes here are reflected immediately (for development)

2. **`sql/`** → `/app/sql` - SQL database storage
   - SQLite databases or other SQL data
   - Data persists between container restarts

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

Add your Flask application files to the `deploy/` directory. The existing `app.py` is a simple example that:
- Returns JSON on the root route
- Provides a health check endpoint

## Troubleshooting

### View logs
```bash
podman logs flask-app
```

### Restart container
```bash
podman restart flask-app
```
