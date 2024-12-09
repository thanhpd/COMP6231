from flask import Flask, jsonify
from flask_cors import CORS
from dbconnector import CouchbaseClient

app = Flask(__name__)
CORS(app)

# Example endpoint
@app.route('/get-recommendations-by-name/<string:movieName>', methods=['GET'])
def get_recommendations(movieName):
    try:
        cbClient = CouchbaseClient()
        cbClient.init_app()

        # Get recommendations from Couchbase
        top_5_recommendations = cbClient.get_recommendations(movieName)
    except Exception as e:
        print(f"Error in get_recommendations: {e}")
        return jsonify({"error": "An error occurred while fetching recommendations.", "details": str(e)}), 500

    # Return the recommended movies in JSON format
    return jsonify({"movieName": movieName, "recommendedMovies": top_5_recommendations})


@app.route('/get-autosuggestions/<string:query>', methods=['GET'])
def get_autosuggestions(query):
    try:
        cbClient = CouchbaseClient()
        cbClient.init_app()

        # Get autosuggestions from Couchbase
        top_5_movies = cbClient.get_autosuggestion_by_name(query)

        # Return suggestions as JSON
        return jsonify({"query": query, "autosuggestions": top_5_movies}), 200
    except Exception as e:
        print(f"Error in get_autosuggestions: {e}")  # Add detailed logging
        return jsonify({"error": "An error occurred while fetching autosuggestions.", "details": str(e)}), 500

if __name__ == '__main__':
    # Run on port 5000 with debug mode for easy troubleshooting
    app.run(host='0.0.0.0', port=6001)
