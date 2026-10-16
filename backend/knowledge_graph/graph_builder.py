import json
import os


# Get the project root directory
BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

RELATIONSHIPS_FILE = os.path.join(
    BASE_DIR,
    "data",
    "legal_relationships.json"
)


def load_relationships():
    """
    Load legal relationships from the JSON dataset.
    """

    if not os.path.exists(RELATIONSHIPS_FILE):
        raise FileNotFoundError(
            f"Relationship file not found: {RELATIONSHIPS_FILE}"
        )

    with open(
        RELATIONSHIPS_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def build_knowledge_graph():
    """
    Build a simple knowledge graph using
    nodes and relationships.
    """

    relationships = load_relationships()

    graph = {
        "nodes": [],
        "relationships": []
    }

    nodes = set()

    for relationship in relationships:

        source = relationship["source"]
        relation = relationship["relation"]
        target = relationship["target"]

        nodes.add(source)
        nodes.add(target)

        graph["relationships"].append(
            {
                "source": source,
                "relation": relation,
                "target": target
            }
        )

    graph["nodes"] = [
        {
            "id": node,
            "label": node
        }
        for node in sorted(nodes)
    ]

    return graph


if __name__ == "__main__":

    graph = build_knowledge_graph()

    print("\n===== KNOWLEDGE GRAPH =====")

    print("\nNodes:")

    for node in graph["nodes"]:
        print(
            f"- {node['id']}"
        )

    print("\nRelationships:")

    for relationship in graph["relationships"]:

        print(
            f"{relationship['source']} "
            f"--[{relationship['relation']}]--> "
            f"{relationship['target']}"
        )

    print(
        f"\nTotal Nodes: {len(graph['nodes'])}"
    )

    print(
        f"Total Relationships: "
        f"{len(graph['relationships'])}"
    )