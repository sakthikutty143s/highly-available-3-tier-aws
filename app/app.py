from flask import Flask, render_template, jsonify, request
import pymysql
import socket
import boto3
import json

app = Flask(__name__)

# AWS Configuration
AWS_REGION = "ap-south-1"
SECRET_NAME = "three-tier/rds"

# AWS Secrets Manager Client
secrets_client = boto3.client(
    "secretsmanager",
    region_name=AWS_REGION
)


# Get Database Credentials
def get_db_credentials():
    response = secrets_client.get_secret_value(
        SecretId=SECRET_NAME
    )

    secret = json.loads(
        response["SecretString"]
    )

    return secret


# Connect to RDS MySQL
def get_db_connection():
    credentials = get_db_credentials()

    return pymysql.connect(
        host=credentials["host"],
        user=credentials["username"],
        password=credentials["password"],
        database=credentials["dbname"],
        port=int(credentials.get("port", 3306)),
        cursorclass=pymysql.cursors.DictCursor
    )


# Home Page
@app.route("/")
def home():
    return render_template(
        "index.html",
        hostname=socket.gethostname()
    )


# Health Check
@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "service": "AWS Three-Tier Application"
    })


# Hello API
@app.route("/api/hello")
def hello():
    return jsonify({
        "message": "Hello from AWS Three-Tier Application!",
        "status": "success",
        "hostname": socket.gethostname(),
        "server": "Amazon EC2",
        "region": AWS_REGION
    })


# Get Messages from RDS
@app.route("/api/messages")
def get_messages():

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT id, message, created_at
                FROM messages
                ORDER BY id DESC
            """)

            messages = cursor.fetchall()

        return jsonify(messages)

    finally:
        connection.close()


# Add Message to RDS
@app.route("/api/messages", methods=["POST"])
def add_message():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    message = data.get("message")

    if not message:
        return jsonify({
            "error": "Message is required"
        }), 400

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO messages (message)
                VALUES (%s)
                """,
                (message,)
            )

        connection.commit()

        return jsonify({
            "message": "Message added successfully",
            "status": "success"
        }), 201

    finally:
        connection.close()


# Run Flask Application
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )