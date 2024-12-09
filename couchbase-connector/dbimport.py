from dbconnector import CouchbaseClient
import json

if __name__ == "__main__":
    # Create a new client instance and connect to the DB cluster
    client = CouchbaseClient()
    client.init_app()

    # Load a json file
    with open('final_similarities.json') as f:
        data = json.load(f)

    for key, value in data.items():
        print(key, len(value))
        client.upsert_document('results', key, value)
