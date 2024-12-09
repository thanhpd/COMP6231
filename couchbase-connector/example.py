from dbconnector import CouchbaseClient

if __name__ == "__main__":
  # Create a new client instance and connect to the DB cluster
  client = CouchbaseClient()
  client.init_app()

  # Find top 5 relevant movies by names
  res1 = client.get_autosuggestion_by_name("the", 5)
  print(res1)

  # Get reviews in chunk
  res2 = client.get_reviews_in_chunk(500, 0)
  print(len(res2))

  # Get results by movie name
  res3 = client.get_recommendations("Toy Story (1995)")
  print(res3)
