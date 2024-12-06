# Couchbase Connector

```bash
# Install the dependencies
pip install -r requirements.txt

# Run the code
python example.py
```

## Example usage
```python
if __name__ == "__main__":
  # Create a new client instance and connect to the DB cluster
  client = CouchbaseClient()
  client.init_app()

  # Find top 5 relevant movies by names
  res1 = client.get_autosuggestion_by_name("The", 5)
  print(res1)

  # Get reviews in chunk
  res2 = client.get_reviews_in_chunk(500000, 0)
  print(len(res2))
```
