import json
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions, QueryOptions
from couchbase.auth import PasswordAuthenticator
from couchbase.exceptions import CouchbaseException
from datetime import timedelta
from couchbase.result import PingResult
from couchbase.diagnostics import PingState, ServiceType
from couchbase.management.search import SearchIndex
from couchbase.exceptions import QueryIndexAlreadyExistsException

# Hardcoding values for the connection string, username, and password
DB_CONN_STR="couchbase://dsd1.canadacentral.cloudapp.azure.com,dsd2.canadacentral.cloudapp.azure.com,dsd3.canadacentral.cloudapp.azure.com,dsd4.canadacentral.cloudapp.azure.com,dsd5.canadacentral.cloudapp.azure.com"
DB_USERNAME="dsdadmin"
DB_PASSWORD="Dsd@2024"

class CouchbaseClient(object):
    """Class to handle interactions with Couchbase cluster"""

    def __init__(self) -> None:
        self.cluster = None
        self.bucket = None
        self.scope = None

    def init_app(self):
        """Initialize connection to the Couchbase cluster"""
        self.conn_str = DB_CONN_STR
        self.bucket_name = "recommender"
        self.scope_name = "_default"
        self.username = DB_USERNAME
        self.password = DB_PASSWORD
        self.connect()

    def connect(self) -> None:
        """Connect to the Couchbase cluster"""
        # If the connection is not established, establish it now
        if not self.cluster:
            try:
                # authentication for Couchbase cluster
                auth = PasswordAuthenticator(self.username, self.password)

                cluster_opts = ClusterOptions(auth)
                # wan_development is used to avoid latency issues while connecting to Couchbase over the internet
                cluster_opts.apply_profile("wan_development")

                # connect to the cluster
                self.cluster = Cluster(self.conn_str, cluster_opts)

                # wait until the cluster is ready for use
                self.cluster.wait_until_ready(timedelta(seconds=5))

                # get a reference to our bucket
                self.bucket = self.cluster.bucket(self.bucket_name)
            except CouchbaseException as error:
                print(f"Could not connect to cluster. \nError: {error}")
                print(
                    "Ensure that you have the recommender bucket loaded in the cluster."
                )
                exit()

            if not self.check_scope_exists():
                print(
                    "Inventory scope does not exist in the bucket. \nEnsure that you have the inventory scope in your recommender bucket."
                )
                exit()

            # get a reference to our scope
            self.scope = self.bucket.scope(self.scope_name)
            # # Call the method to create the fts index if search service is enabled
            # if self.is_search_service_enabled():
            #     # self.create_search_index()
            #     print("Search service is enabled on this cluster.")
            # else:
            #     print(
            #         "Search service is not enabled on this cluster. Skipping search index creation."
            #     )

    def check_scope_exists(self) -> bool:
        """Check if the scope exists in the bucket"""
        try:
            scopes_in_bucket = [
                scope.name for scope in self.bucket.collections().get_all_scopes()
            ]
            return self.scope_name in scopes_in_bucket
        except Exception as e:
            print(
                "Error fetching scopes in cluster. \nEnsure that recommender bucket exists."
            )
            print(e)
            exit()

    def is_search_service_enabled(self, min_nodes: int = 1) -> bool:
        try:
            ping_result: PingResult = self.cluster.ping()
            search_endpoints = ping_result.endpoints[ServiceType.Search]
            available_search_nodes = 0
            for endpoint in search_endpoints:
                if endpoint.state == PingState.OK:
                    available_search_nodes += 1
            return available_search_nodes >= min_nodes
        except Exception as e:
            print(
                f"Error checking search service status. \nEnsure that Search Service is enabled: {e}"
            )
            return False

    def create_search_index(self) -> None:
        """Upsert a fts index in the Couchbase cluster"""
        try:
            scope_index_manager = self.bucket.scope(self.scope_name).search_indexes()
            with open(f"{self.index_name}_index.json", "r") as f:
                index_definition = json.load(f)

            # Upsert the index
            scope_index_manager.upsert_index(SearchIndex.from_json(index_definition))
            print(f"Index '{self.index_name}' created or updated successfully.")
        except QueryIndexAlreadyExistsException:
            print(f"Index with name '{self.index_name}' already exists")
        except Exception as e:
            print(f"Error upserting index '{self.index_name}': {e}")

    def get_document(self, collection_name: str, key: str):
        """Get document by key using KV operation"""
        return self.scope.collection(collection_name).get(key)

    def insert_document(self, collection_name: str, key: str, doc: dict):
        """Insert document using KV operation"""
        return self.scope.collection(collection_name).insert(key, doc)

    def delete_document(self, collection_name: str, key: str):
        """Delete document using KV operation"""
        return self.scope.collection(collection_name).remove(key)

    def upsert_document(self, collection_name: str, key: str, doc: dict):
        """Upsert document using KV operation"""
        return self.scope.collection(collection_name).upsert(key, doc)

    def query(self, sql_query, *options, **kwargs):
        """Query Couchbase using SQL++"""
        # options are used for positional parameters
        # kwargs are used for named parameters
        return self.scope.query(sql_query, *options, **kwargs)

    def get_autosuggestion_by_name(self, query_name: str, limit:int=5) -> list[str]:
        """Get top autosuggestion movie names by name"""
        q_str = 'SELECT t.title FROM `movies` t WHERE LOWER(t.title) LIKE $title LIMIT $limit;'
        q_res = self.query(q_str, QueryOptions(named_parameters={'title': query_name+'%', 'limit':limit}))
        results = list(map(lambda x: x['title'],list(q_res)))
        return results

    def get_reviews_in_chunk(self, size:int=100, offset:int=0) -> list[dict]:
        """Get reviews in chunks"""
        q_str = 'SELECT r.movieId, r.rating, r.title, r.userId FROM `reviews` r LIMIT $size OFFSET $offset;'
        q_res = self.query(q_str, QueryOptions(named_parameters={'size': size, 'offset':offset}))
        results = list(q_res)
        return results

    def get_movie_docs_by_name(self, name:str) -> dict:
        """Get movie document by name"""
        q_str = 'SELECT t.* FROM `movies` t WHERE LOWER(t.title) = $title;'
        q_res = self.query(q_str, QueryOptions(named_parameters={'title': name.lower()}))
        results = list(q_res)
        return results

    def get_movie_docs_by_id(self, movie_ids:list[int]) -> dict:
        """Get movie document by id"""
        q_str = 'SELECT META().id, t.title FROM `movies` t WHERE META().id IN $movie_ids;'
        q_res = self.query(q_str, QueryOptions(named_parameters={'movie_ids': movie_ids}))
        list_results = list(q_res)
        results = {item['id']: item['title'] for item in list_results}
        return results

    def get_recommendations(self, movieName: str) -> list[dict]:
        # Return the recommended movies in JSON format
        movie_docs = self.get_movie_docs_by_name(movieName)
        if (len(movie_docs) > 0):
            movie_doc_id = movie_docs[0]['movieId']

            recommendation_results = self.get_document('results', str(movie_doc_id)).value[:20]
            movie_ids = [str(item["movieId"]) for item in recommendation_results]

            movie_docs = self.get_movie_docs_by_id(movie_ids)
            for item in recommendation_results:
                item['title'] = movie_docs[str(item['movieId'])]
            return recommendation_results
        else:
            return []
