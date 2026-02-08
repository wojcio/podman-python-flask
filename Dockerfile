FROM python:3.13-slim

WORKDIR /app

# Install Flask
RUN pip install --no-cache-dir flask

COPY deploy/ ./deploy/
EXPOSE 5000

CMD ["python", "deploy/app.py"]
