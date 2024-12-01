from flask import Flask, jsonify, request
from flask_cors import CORS  # Import CORS

app = Flask(__name__)

# Enable CORS for all routes (allow cross-origin requests from any domain)
CORS(app, resources={r"/*": {"origins": "http://3.12.241.93"}})

# Example movie data with ratings
movies_data = [
    {"movie": "Inception", "rating": 8.8},
    {"movie": "Interstellar", "rating": 8.6},
    {"movie": "The Dark Knight", "rating": 9.0},
    {"movie": "The Prestige", "rating": 8.5},
    {"movie": "Memento", "rating": 8.4},
    {"movie": "The Matrix", "rating": 8.7},
    {"movie": "The Godfather", "rating": 9.2},
    {"movie": "Shutter Island", "rating": 8.1},
    {"movie": "Gladiator", "rating": 8.5},
    {"movie": "Fight Club", "rating": 8.8}
]

# Example endpoint
@app.route('/get-recommendations-by-name/<string:movieName>', methods=['GET'])
def get_recommendations(movieName):
    # Find the movie by name
    selected_movie = next((movie for movie in movies_data if movie['movie'].lower() == movieName.lower()), None)

    if selected_movie is None:
        return jsonify({"error": "Movie not found"}), 404

    # Calculate the absolute difference between ratings and the selected movie's rating
    selected_rating = selected_movie['rating']
    recommendations = sorted(
        (movie for movie in movies_data if movie['movie'].lower() != movieName.lower()),
        key=lambda movie: abs(movie['rating'] - selected_rating)
    )

    # Get the top 5 similar rated movies
    top_5_recommendations = recommendations[:5]

    # Return the recommended movies in JSON format
    return jsonify({"movieName": movieName, "recommendedMovies": top_5_recommendations})

if __name__ == '__main__':
    # Run on port 5000 with debug mode for easy troubleshooting
    app.run(host='0.0.0.0', port=5000, debug=True)
