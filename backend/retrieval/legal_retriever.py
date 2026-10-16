import json
import os
import re


# ------------------------------------------------------------
# LOAD LEGAL PROVISIONS
# ------------------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

PROVISIONS_FILE = os.path.join(
    BASE_DIR,
    "data",
    "legal_provisions.json"
)


def load_legal_provisions():

    try:

        with open(
            PROVISIONS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception as e:

        raise Exception(
            f"Unable to load legal provisions: {str(e)}"
        )


# ------------------------------------------------------------
# TEXT NORMALIZATION
# ------------------------------------------------------------

def normalize_text(text):

    if not text:
        return ""

    text = text.lower()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ------------------------------------------------------------
# KEYWORD MATCHING
# ------------------------------------------------------------

def calculate_keyword_match(
    clause_text,
    provision
):

    clause_text = normalize_text(clause_text)

    keywords = provision.get(
        "keywords",
        []
    )

    matched_keywords = []

    for keyword in keywords:

        normalized_keyword =normalize_text(keyword)

        if normalized_keyword in clause_text:

            matched_keywords.append(
                keyword
            )

    return matched_keywords


# ------------------------------------------------------------
# RETRIEVE RELEVANT PROVISIONS
# ------------------------------------------------------------

def retrieve_legal_provisions(
    clause_text,
    document_type=None,
    top_k=3
):

    if not clause_text:

        return []

    provisions = load_legal_provisions()

    results = []

    normalized_clause = normalize_text(clause_text)


    for provision in provisions:

        # ----------------------------------------------------
        # DOCUMENT TYPE CHECK
        # ----------------------------------------------------

        supported_types = provision.get(
                "document_types",
                []
            )

        document_match = (
            not document_type
            or document_type in supported_types
        )


        # ----------------------------------------------------
        # KEYWORD MATCHING
        # ----------------------------------------------------

        matched_keywords = calculate_keyword_match(
                normalized_clause,
                provision
            )

        keyword_score = len(matched_keywords)


        # ----------------------------------------------------
        # TOPIC / DOCUMENT MATCH
        # ----------------------------------------------------

        score = keyword_score

        if document_match:
            score += 1

        if keyword_score > 0:

            results.append({

                "provision_id":
                    provision.get(
                        "provision_id"
                    ),

                "title":
                    provision.get(
                        "title"
                    ),

                "topic":
                    provision.get(
                        "topic"
                    ),

                "description":
                    provision.get(
                        "description"
                    ),

                "conditions":
                    provision.get(
                        "conditions",
                        []
                    ),

                "exceptions":
                    provision.get(
                        "exceptions",
                        []
                    ),

                "source":
                    provision.get(
                        "source",
                        {}
                    ),

                "matched_keywords":
                    matched_keywords,

                "score":
                    score
            })

    # --------------------------------------------------------
    # SORT BY RELEVANCE
    # --------------------------------------------------------

    results.sort(
        key=lambda item:
            item["score"],
        reverse=True
    )


    return results[:top_k]