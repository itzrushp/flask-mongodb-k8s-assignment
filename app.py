from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# MongoDB connection with authentication
def get_mongo_connection():
    """
    Create MongoDB connection with authentication.
    
    Why separate function?
    - Allows reconnection on failure
    - Better error handling
    - Easier to test
    """
    try:
        # Build connection string with authentication
        username = os.environ.get("MONGO_USERNAME", "admin")
        password = os.environ.get("MONGO_PASSWORD", "admin")
        mongo_host = os.environ.get("MONGO_HOST", "localhost")
        mongo_port = os.environ.get("MONGO_PORT", "27017")
        
        # Connection URI format: mongodb://username:password@host:port/authSource=admin
        connection_uri = f"mongodb://{username}:{password}@{mongo_host}:{mongo_port}/?authSource=admin"
        
        logger.info(f"Connecting to MongoDB at {mongo_host}:{mongo_port}")
        client = MongoClient(connection_uri, serverSelectionTimeoutMS=5000)
        
        # Verify connection
        client.admin.command('ping')
        logger.info("MongoDB connection successful")
        
        return client
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}")
        raise

# Initialize MongoDB client
try:
    mongo_client = get_mongo_connection()
    db = mongo_client.flask_db
    collection = db.data
except Exception as e:
    logger.error(f"Failed to initialize MongoDB: {e}")
    mongo_client = None

@app.route('/')
def index():
    """
    Health check endpoint.
    Returns welcome message with current timestamp.
    """
    try:
        # If MongoDB is connected, verify it's still working
        if mongo_client:
            mongo_client.admin.command('ping')
        return jsonify({
            "message": "Welcome to the Flask app!",
            "current_time": datetime.now().isoformat(),
            "status": "healthy"
        }), 200
    except Exception as e:
        logger.error(f"Error in index route: {e}")
        return jsonify({
            "message": "Welcome to the Flask app!",
            "current_time": datetime.now().isoformat(),
            "status": "degraded",
            "error": str(e)
        }), 200  # Return 200 for liveness probe

@app.route('/data', methods=['GET', 'POST'])
def data_endpoint():
    """
    Data endpoint for CRUD operations.
    POST: Insert data into MongoDB
    GET: Retrieve all data from MongoDB
    """
    if request.method == 'POST':
        try:
            if not mongo_client:
                logger.error("POST /data called but mongo_client is None")  # <‑‑ add this
                return jsonify({"error": "Database connection failed"}), 503

            data = request.get_json()
            if not data:
                return jsonify({"error": "No JSON data provided"}), 400

            # Add timestamp to data
            data['created_at'] = datetime.now().isoformat()

            # Insert into MongoDB
            result = collection.insert_one(data)
            logger.info(f"Data inserted with ID: {result.inserted_id}")

            return jsonify({
                "status": "Data inserted",
                "inserted_id": str(result.inserted_id)
            }), 201

        except Exception as e:
            logger.exception(f"Error inserting data into MongoDB: {e}")  # <‑‑ change to logger.exception
            return jsonify({"error": "Database connection failed"}), 503

    
    elif request.method == 'GET':
        try:
            if not mongo_client:
                return jsonify({"error": "Database connection failed"}), 503
            
            # Retrieve all documents (exclude MongoDB's _id field for cleaner output)
            data = list(collection.find({}, {"_id": 0}))
            logger.info(f"Retrieved {len(data)} documents")
            
            return jsonify({
                "count": len(data),
                "data": data
            }), 200
            
        except Exception as e:
            logger.error(f"Error retrieving data: {e}")
            return jsonify({"error": str(e)}), 500

@app.route('/health')
def health_check():
    """
    Kubernetes liveness probe endpoint.
    Returns 200 if app is running (even if DB is down).
    """
    return jsonify({"status": "healthy"}), 200

@app.route('/ready')
def readiness_check():
    """
    Kubernetes readiness probe endpoint.
    Returns 200 only if both app and DB are healthy.
    Used by Kubernetes to determine if pod should receive traffic.
    """
    try:
        if mongo_client:
            mongo_client.admin.command('ping')
        return jsonify({"status": "ready"}), 200
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return jsonify({"status": "not ready", "error": str(e)}), 503

if __name__ == '__main__':
    # Listen on all interfaces (0.0.0.0) so Kubernetes can access it
    app.run(host='0.0.0.0', port=5000, debug=False)