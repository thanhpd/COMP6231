import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize
import os


def process_movie_similarity(
    movies_path, ratings_path, output_dir, partition_size=2000000
):
    """
    Process movie similarity in partitions and save cosine similarity tables as CSV files.

    Args:
    - movies_path (str): Path to movies CSV file
    - ratings_path (str): Path to ratings CSV file
    - output_dir (str): Directory to save output CSV files
    - partition_size (int): Number of rows to process in each partition
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Read datasets
    movies = pd.read_csv(movies_path)
    ratings = pd.read_csv(ratings_path)

    # Preprocessing
    ratings = ratings.drop(["timestamp"], axis=1)
    ratings["rating"] /= 5
    movies = movies.drop(["genres"], axis=1)
    ratings = ratings.sort_values("userId")

    # Calculate total number of partitions
    total_rows = len(ratings)
    num_partitions = (total_rows + partition_size - 1) // partition_size

    print(f"Total rows: {total_rows}")
    print(f"Number of partitions: {num_partitions}")

    # Process each partition
    for partition in range(num_partitions):
        start_idx = partition * partition_size
        end_idx = min((partition + 1) * partition_size, total_rows)

        print(f"\nProcessing Partition {partition + 1}: Rows {start_idx} to {end_idx}")

        # Slice the current partition
        ratings_partition = ratings.iloc[start_idx:end_idx]

        # Create pivot table
        pivot_table = ratings_partition.pivot_table(
            index=["userId"], columns=["movieId"], values="rating"
        )
        pivot_table = pivot_table.fillna(0)

        print(f"Pivot table shape: {pivot_table.shape}")

        # Check if pivot table is empty
        if pivot_table.empty:
            print(f"Skipping empty partition {partition + 1}")
            continue

        # Normalize the data
        normalized_data = normalize(pivot_table, axis=0)

        # Compute cosine similarity
        cosine_sim = cosine_similarity(normalized_data.T)

        # Create DataFrame for similarity matrix
        cosine_sim_df = pd.DataFrame(
            cosine_sim, index=pivot_table.columns, columns=pivot_table.columns
        )

        # Save to CSV
        output_filename = os.path.join(
            output_dir, f"cosine_similarity_partition_{partition + 1}.csv"
        )
        cosine_sim_df.to_csv(output_filename)

        print(
            f"Saved cosine similarity for partition {partition + 1} to {output_filename}"
        )
        print(f"Cosine similarity matrix shape: {cosine_sim_df.shape}")


# Example usage
if __name__ == "__main__":
    movies_path = "./archive/movie.csv"
    ratings_path = "./archive/rating.csv"
    output_directory = "./cosine_similarity_outputs"

    process_movie_similarity(movies_path, ratings_path, output_directory)
