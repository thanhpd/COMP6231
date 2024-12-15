import pandas as pd
import json
import os
import numpy as np


def generate_movie_similarity_jsons(similarity_dir, output_dir):
    """
    Process cosine similarity CSV files and generate:
    1. Single JSON files for each partition with top 100 similar movies
    2. A master JSON mapping which files contain which movies

    Args:
    - similarity_dir (str): Directory containing cosine similarity CSV files
    - output_dir (str): Directory to save output JSON files
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Prepare tracking dictionaries
    global_movie_to_file_mapping = {}

    # Get all CSV files in the directory
    csv_files = [f for f in os.listdir(similarity_dir) if f.endswith(".csv")]
    csv_files.sort()  # Ensure consistent processing order

    # Process each CSV file
    for csv_file in csv_files:
        print(f"\nProcessing file: {csv_file}")

        # Read the cosine similarity matrix
        file_path = os.path.join(similarity_dir, csv_file)
        cosine_sim_df = pd.read_csv(file_path, index_col=0)

        # Prepare a dictionary to store similarities for this partition
        partition_similarities = {}

        # Process each movie in the cosine similarity matrix
        for movie_id in cosine_sim_df.index:
            # Get similarities for this movie
            similarities = cosine_sim_df.loc[movie_id]

            # Sort similarities in descending order and get top 100
            top_similar = similarities.nlargest(100)

            # Convert to list of (movieId, score) pairs, excluding self-similarity
            similar_movies = [
                {"movieId": int(sim_movie_id), "score": float(score)}
                for sim_movie_id, score in top_similar.items()
                if int(sim_movie_id) != int(movie_id)
            ]

            # Store similarities for this movie
            partition_similarities[int(movie_id)] = similar_movies

            # Track which file contains this movie
            if int(movie_id) not in global_movie_to_file_mapping:
                global_movie_to_file_mapping[int(movie_id)] = []
            global_movie_to_file_mapping[int(movie_id)].append(csv_file)

        # Save partition similarities to a single JSON file
        partition_output_filename = os.path.join(
            output_dir, f'partition_{csv_file.replace(".csv", "")}_similarities.json'
        )
        with open(partition_output_filename, "w") as f:
            json.dump(partition_similarities, f, indent=2)

        print(f"Processed {len(cosine_sim_df.index)} movies in {csv_file}")

    # Save the movie to file mapping
    mapping_output_path = os.path.join(output_dir, "movie_file_mapping.json")
    with open(mapping_output_path, "w") as f:
        json.dump(global_movie_to_file_mapping, f, indent=2)

    print("\nProcessing complete!")
    print(f"Partition similarities saved in: {output_dir}")
    print(f"Movie-to-file mapping saved in: {mapping_output_path}")


# Example usage
if __name__ == "__main__":
    similarity_directory = "./cosine_similarity_outputs"
    output_directory = "./movie_similarity_jsons"

    generate_movie_similarity_jsons(similarity_directory, output_directory)
