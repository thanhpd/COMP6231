import os
import json
from collections import defaultdict
import argparse


def merge_similarity_files(input_dir, output_file, top_n=50):
    """
    Merge similarity JSON files and average scores for each movie.

    Args:
    - input_dir (str): Directory containing partition similarity JSON files
    - output_file (str): Path to save the merged JSON file
    - top_n (int): Number of top similar movies to keep for each movie
    """
    # Collect all similarity data
    global_similarities = defaultdict(lambda: defaultdict(list))

    # Find all JSON files in the input directory
    json_files = [f for f in os.listdir(input_dir) if f.endswith("_similarities.json")]
    print("located files: ", json_files)
    # Process each JSON file
    for filename in json_files:
        filepath = os.path.join(input_dir, filename)

        with open(filepath, "r") as f:
            partition_similarities = json.load(f)

        # Aggregate similarities
        for source_movie, similar_movies in partition_similarities.items():
            for similar_movie in similar_movies:
                global_similarities[source_movie][similar_movie["movieId"]].append(
                    similar_movie["score"]
                )

    # Calculate average scores and prepare final similarities
    merged_similarities = {}

    for source_movie, similar_movies in global_similarities.items():
        # Calculate average scores
        averaged_similarities = [
            {"movieId": movie_id, "avg_score": sum(scores) / len(scores)}
            for movie_id, scores in similar_movies.items()
        ]

        # Sort by average score
        averaged_similarities.sort(key=lambda x: x["avg_score"], reverse=True)

        # Keep top N similar movies
        merged_similarities[source_movie] = averaged_similarities[:top_n]

    # Save merged similarities
    with open(output_file, "w") as f:
        json.dump(merged_similarities, f, indent=2)

    print(f"Merged similarities saved to {output_file}")
    print(f"Total movies with similarities: {len(merged_similarities)}")

    # Optional: Print some statistics
    movie_counts = {movie: len(sims) for movie, sims in merged_similarities.items()}
    print(f"Movies with most similar movies:")
    for movie, count in sorted(movie_counts.items(), key=lambda x: x[1], reverse=True)[
        :5
    ]:
        print(f"Movie {movie}: {count} similar movies")


def main():
    parser = argparse.ArgumentParser(description="Merge movie similarity JSON files")
    parser.add_argument(
        "--input",
        default="./movie_similarity_jsons",
        help="Directory containing similarity JSON files (default: ./movie_similarity_jsons)",
    )
    parser.add_argument(
        "--output",
        default="./merged_movie_similarities.json",
        help="Path to save merged similarities (default: ./merged_movie_similarities.json)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=50,
        help="Number of top similar movies to keep (default: 50)",
    )

    args = parser.parse_args()

    merge_similarity_files(args.input, args.output, args.top)


if __name__ == "__main__":
    main()
