from neo4j import GraphDatabase

class neo4jKG:
    def __init__(self, url, user, password):
        self.driver = GraphDatabase.driver(url, auth=(user, password))

    def close(self):
        self.driver.close()

    def clear_db(self):
        with self.driver.session() as session:
            session.execute_write(lambda tx: tx.run("MATCH (n) DELETE n"))
    def create_triplet(self, subj, pred, obj):
        with self.driver.session() as session:
            session.execute_write(self._create_and_link, subj, pred, obj)

    def init_data(self, triples):
        self.clear_db()
        for triple in triples:
            self.create_triplet(*triple)

    @staticmethod
    def _create_and_link(tx, subj, pred, obj):
        query = (
            "MERGE (s:Entity {name: $subj}) "
            "MERGE (o:Entity {name: $obj}) "
            "MERGE (s)-[:RELATION {type: $pred}]->(o)"
        )
        tx.run(query, subj=subj, pred=pred, obj=obj)

    def query_relations(self, entity):
        with self.driver.session() as session:
            result = session.run(
                "MATCH (s:Entity {name: $entity})-[:RELATION]->(o) RETURN o.name",
                entity=entity
            )
            return [record["o.name"] for record in result]

    def query_relations_agent(self, entity: str, domain: str = None):
        cypher = """
        MATCH (s:Entity {name: $entity})-[r:RELATION]->(o)
        """
        params = {"entity": entity}

        if domain:
            cypher += " WHERE r.type = $domain "
            params["domain"] = domain

        cypher += " RETURN o.name "

        with self.driver.session() as session:
            return [r["o.name"] for r in session.run(cypher, **params)]

    def get_entities_names(self):
        # Neo4j查询语句——Cypher
        query = """
        MATCH (n)
        RETURN DISTINCT n.name AS entity_name
        """
        with self.driver.session() as session:
            result = session.run(query)
            return [record["entity_name"] for record in result]