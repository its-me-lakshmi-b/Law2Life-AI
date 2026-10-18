import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.knowledge_graph.graph_queries import (
    get_related_nodes,
    find_path
)


# Maps document clause categories/keywords
# to concepts in the Knowledge Graph.
CONCEPT_KEYWORDS = {
    "termination": [
        "terminate",
        "termination",
        "notice period",
        "notice"
    ],

    "leave": [
        "leave",
        "vacation",
        "absence",
        "maternity"
    ],

    "salary": [
        "salary",
        "wages",
        "payment",
        "payable",
        "compensation"
    ],

    "rent": [
        "rent",
        "monthly rent",
        "lease",
        "tenant",
        "landlord"
    ],

    "security_deposit": [
        "security deposit",
        "deposit",
        "refund of deposit"
    ],

    "working_hours": [
        "working hours",
        "normal working schedule",
        "hours per week"
    ],

    "confidentiality": [
        "confidential",
        "confidentiality",
        "non-public information",
        "restraint of trade",
        "non-compete"
    ],

    "dispute_resolution": [
        "dispute",
        "arbitration",
        "jurisdiction",
        "governing law"
    ],

    "employment": [
        "employment",
        "employee",
        "employer",
        "duties"
    ]
}



def identify_concepts(clause_text):
    """
    Identify Knowledge Graph concepts that are
    relevant to a document clause.
    """

    if not clause_text:
        return []

    text = clause_text.lower()

    concepts = []

    for concept, keywords in CONCEPT_KEYWORDS.items():

        for keyword in keywords:

            if keyword in text:

                concepts.append(
                    concept
                )

                break

    return concepts


def analyze_clause_context(clause_text, concept):
    """
    Analyze one document clause using the
    Knowledge Graph.
    """

    related_nodes = get_related_nodes(
        concept
    )

    paths = []

    for item in related_nodes:

        path = find_path(
            concept,
            item["node"]
        )

        if path:

            paths.append(
                {
                    "target": item["node"],
                    "relation": item["relation"],
                    "path": path
                }
            )

    return {
        "clause": clause_text,
        "concept": concept,
        "related_nodes": related_nodes,
        "paths": paths
    }


def reason_about_clause(clause_text):
    """
    Perform context-aware reasoning for
    a single document clause.
    """

    concepts = identify_concepts(
        clause_text
    )

    results = []

    for concept in concepts:

        # Convert the detected keyword concept
        # to the actual Knowledge Graph node.
        graph_concept = concept

        if concept == "termination":
            graph_concept = "Termination"

        elif concept == "leave":
            graph_concept = "Leave"

        elif concept == "salary":
            graph_concept = "Salary"

        elif concept == "rent":
            graph_concept = "Rent"

        elif concept == "security_deposit":
            graph_concept = "Security Deposit"

        elif concept == "working_hours":
            graph_concept = "Working Hours"

        elif concept == "confidentiality":
            graph_concept = "Confidentiality"

        elif concept == "dispute_resolution":
            graph_concept = "Dispute Resolution"

        elif concept == "employment":
            graph_concept = "Employment Terms"


        analysis = analyze_clause_context(
            clause_text,
            graph_concept
        )

        reasoning = []

        for node in analysis["related_nodes"]:

            if node["node"] == "Notice Period":

                reasoning.append(
                    {
                        "aspect": "notice_requirement",
                        "finding": (
                            "The clause is connected "
                            "to a notice period requirement."
                        ),
                        "related_concept": "Notice Period"
                    }
                )

            elif node["node"] == "Applicable Law":

                reasoning.append(
                    {
                        "aspect": "legal_condition",
                        "finding": (
                            "The clause is subject "
                            "to applicable law."
                        ),
                        "related_concept": "Applicable Law"
                    }
                )

            elif node["node"] == "Leave Notice Period":

                reasoning.append(
                    {
                        "aspect": "leave_notice",
                        "finding": (
                            "The leave clause is "
                            "connected to a leave "
                            "notice requirement."
                        ),
                        "related_concept":
                            "Leave Notice Period"
                    }
                )

            elif node["node"] == "Employee":

                reasoning.append(
                    {
                        "aspect": "employee_relationship",
                        "finding": (
                            "The clause is connected "
                            "to the employee."
                        ),
                        "related_concept": "Employee"
                    }
                )

        results.append(
            {
                "concept": graph_concept,
                "related_nodes":
                    analysis["related_nodes"],
                "paths":
                    analysis["paths"],
                "reasoning":
                    reasoning
            }
        )

    return {
        "clause": clause_text,
        "detected_concepts": concepts,
        "graph_reasoning": results,
        "results": results
    }


def reason_about_document(clauses):
    """
    Perform Knowledge Graph reasoning over
    multiple clauses extracted from a document.
    """

    document_reasoning = []

    for clause in clauses:

        if isinstance(clause, dict):

            clause_text = clause.get(
                "text",
                ""
            )

            category = clause.get(
                "category",
                ""
            )

        else:

            clause_text = str(clause)
            category = ""

        if not clause_text:
            continue

        result = reason_about_clause(
            clause_text
        )

        result["category"] = category

        document_reasoning.append(
            result
        )

    return document_reasoning


if __name__ == "__main__":

    sample_clauses = [

        {
            "category": "termination",
            "text": (
                "Either party may terminate "
                "the employment by providing "
                "30 days' written notice."
            )
        },

        {
            "category": "leave",
            "text": (
                "Leave requests should normally "
                "be submitted at least seven "
                "days before the intended leave date."
            )
        },

        {
            "category": "confidentiality",
            "text": (
                "The Employee must keep confidential "
                "all non-public business information."
            )
        }
    ]

    results = reason_about_document(
        sample_clauses
    )

    print(
        "\n===== DOCUMENT CONTEXT-AWARE REASONING ====="
    )

    for result in results:

        print("\n--------------------------------")

        print(
            f"Category: {result['category']}"
        )

        print(
            f"Clause: {result['clause']}"
        )

        print(
            f"Detected Concepts: "
            f"{result['detected_concepts']}"
        )

        for reasoning_group in result[
            "graph_reasoning"
        ]:

            print(
                f"\nKnowledge Graph Concept: "
                f"{reasoning_group['concept']}"
            )

            print("Related Nodes:")

            for node in reasoning_group[
                "related_nodes"
            ]:

                print(
                    f"  - "
                    f"{node['relation']} -> "
                    f"{node['node']}"
                )


            print("Reasoning:")

            for item in reasoning_group[
                "reasoning"
            ]:

                print(
                    f"  - "
                    f"{item['aspect']}: "
                    f"{item['finding']}"
                )