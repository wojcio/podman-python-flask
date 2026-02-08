# Podman Pod and Container Setup

# 1. Create a pod for related containers
podman pod create --name flask-pod -p 8080:5000

# 2. Run the Flask container with persistent storage mounts
podman run -d \
    --name flask-app \
    --pod flask-pod \
    -v $(pwd)/deploy:/app:z \
    -v $(pwd)/sql:/app/sql:z \
    --restart=always \
    localhost/flask-app

# Cleanup (if needed):
# podman stop flask-app
# podman rm flask-app
# podman pod stop flask-pod
# podman pod rm flask-pod
