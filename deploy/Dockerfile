FROM python:3.13-slim

WORKDIR /app

# Install Flask
RUN pip install --no-cache-dir flask

# Create a simple Flask app
COPY app.py .

EXPOSE 5000

CMD ["python", "app.py"]
