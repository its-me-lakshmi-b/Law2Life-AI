from backend.knowledge_graph.graph_builder import build_knowledge_graph


def get_related_nodes(node_name):
    """
    Find all nodes directly connected to the given node.
    """

    graph = build_knowledge_graph()

    related_nodes = []

    for relationship in graph["relationships"]:

        if relationship["source"].lower() == node_name.lower():

            related_nodes.append({
                "node": relationship["target"],
                "relation": relationship["relation"],
                "direction": "outgoing"
            })

        elif relationship["target"].lower() == node_name.lower():

            related_nodes.append({
                "node": relationship["source"],
                "relation": relationship["relation"],
                "direction": "incoming"
            })

    return related_nodes


def get_relationships_from_node(node_name):
    """
    Find relationships going out from a specific node.
    """

    graph = build_knowledge_graph()

    relationships = []

    for relationship in graph["relationships"]:

        if relationship["source"].lower() == node_name.lower():

            relationships.append(relationship)

    return relationships


def find_path(start_node, target_node, max_depth=5):
    """
    Find a path between two nodes using breadth-first search.
    """

    graph = build_knowledge_graph()

    queue = [
        (start_node, [start_node])
    ]

    visited = set()

    while queue:

        current_node, path = queue.pop(0)

        if current_node.lower() == target_node.lower():
            return path

        if current_node.lower() in visited:
            continue

        visited.add(current_node.lower())

        for relationship in graph["relationships"]:

            if relationship["source"].lower() == current_node.lower():

                next_node = relationship["target"]

                if next_node.lower() not in visited:

                    new_path = path + [next_node]

                    if len(new_path) <= max_depth + 1:

                        queue.append(
                            (
                                next_node,
                                new_path
                            )
                        )

    return []


if __name__ == "__main__":

    print("\n===== RELATED NODES =====")

    related = get_related_nodes(
        "Termination"
    )

    for item in related:
        print(
            f"{item['direction']}: "
            f"{item['relation']} -> "
            f"{item['node']}"
        )

    print("\n===== PATH =====")

    path = find_path(
        "Employment Agreement",
        "Applicable Law"
    )

    if path:
        print(" -> ".join(path))
    else:
        print("No path found.")