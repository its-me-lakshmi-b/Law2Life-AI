// ============================================================
// LAW2LIFE AI - DASHBOARD
// ============================================================


// ------------------------------------------------------------
// GET ANALYSIS RESULT
// ------------------------------------------------------------

const storedResult =
    sessionStorage.getItem("analysisResult");


let analysisData = null;


if (storedResult) {

    try {

        analysisData =
            JSON.parse(storedResult);

    } catch (error) {

        console.error(
            "Unable to read analysis result:",
            error
        );

    }

}


// ------------------------------------------------------------
// PAGE INITIALIZATION
// ------------------------------------------------------------

document.addEventListener(
    "DOMContentLoaded",
    async function () {

        if (!analysisData) {

            showNoAnalysisMessage();

            return;
        }

        await runNLPAnalysis();

        displayDocumentInformation();

        displaySummary();

        displayRights();

        displayObligations();

        displayDeadlines();

        displayPenalties();

        displayConflicts();

        displayRisk();

        displayActions();

        displayEvidence();

        displayExplanation();

    }
);

// ------------------------------------------------------------
// NO ANALYSIS
// ------------------------------------------------------------

function showNoAnalysisMessage() {

    document.getElementById(
        "analysisStatus"
    ).innerText = "No analysis available";


    document.getElementById(
        "summary"
    ).innerText =
        "Please upload and analyze a document first.";

}


// ------------------------------------------------------------
// DOCUMENT INFORMATION
// ------------------------------------------------------------

function displayDocumentInformation() {

    const documentName =
        analysisData.document_name ||
        "Uploaded Document";


    const documentType =
        analysisData.document_type ||
        "Not determined";


    document.getElementById(
        "documentName"
    ).innerText = documentName;


    document.getElementById(
        "documentType"
    ).innerText = documentType;


    document.getElementById(
        "analysisStatus"
    ).innerText = "Completed";


    const entities =
        analysisData.entities || [];


    const clauses =
        analysisData.clauses || [];


    document.getElementById(
        "entityCount"
    ).innerText = entities.length;


    document.getElementById(
        "clauseCount"
    ).innerText = clauses.length;

}


// ------------------------------------------------------------
// SUMMARY
// ------------------------------------------------------------

function displaySummary() {

    const summary =
        analysisData.summary ||
        "No summary was generated.";


    document.getElementById(
        "summary"
    ).innerText = summary;

}


// ------------------------------------------------------------
// RIGHTS
// ------------------------------------------------------------

function displayRights() {

    const rights =
        analysisData.rights || [];


    const container =
        document.getElementById(
            "rightsContainer"
        );


    container.innerHTML = "";


    if (rights.length === 0) {

        container.innerHTML =
            '<p class="empty-message">' +
            'No rights identified.' +
            '</p>';

        return;

    }


    rights.forEach(function (right) {

        const item =
            document.createElement("div");


        item.className =
            "list-item right-item";


        item.innerHTML =
            "<span>✓</span>" +
            "<p>" +
            escapeHTML(right) +
            "</p>";


        container.appendChild(item);

    });

}


// ------------------------------------------------------------
// OBLIGATIONS
// ------------------------------------------------------------

function displayObligations() {

    const obligations =
        analysisData.obligations || [];


    const container =
        document.getElementById(
            "obligationsContainer"
        );


    container.innerHTML = "";


    if (obligations.length === 0) {

        container.innerHTML =
            '<p class="empty-message">' +
            'No obligations identified.' +
            '</p>';

        return;

    }


    obligations.forEach(function (obligation) {

        const item =
            document.createElement("div");


        item.className =
            "list-item obligation-item";


        item.innerHTML =
            "<span>!</span>" +
            "<p>" +
            escapeHTML(obligation) +
            "</p>";


        container.appendChild(item);

    });

}


// ------------------------------------------------------------
// DEADLINES
// ------------------------------------------------------------

function displayDeadlines() {

    const deadlines =
        analysisData.deadlines || [];


    const container =
        document.getElementById(
            "deadlinesContainer"
        );


    container.innerHTML = "";


    if (deadlines.length === 0) {

        container.innerHTML =
            '<p class="empty-message">' +
            'No deadlines identified.' +
            '</p>';

        return;

    }


    deadlines.forEach(function (deadline) {

        const item =
            document.createElement("div");


        item.className =
            "list-item deadline-item";


        item.innerHTML =
            "<span></span>" +
            "<p>" +
            escapeHTML(deadline) +
            "</p>";


        container.appendChild(item);

    });

}


// ------------------------------------------------------------
// PENALTIES
// ------------------------------------------------------------

function displayPenalties() {

    const penalties =
        analysisData.penalties || [];


    const container =
        document.getElementById(
            "penaltiesContainer"
        );


    container.innerHTML = "";


    if (penalties.length === 0) {

        container.innerHTML =
            '<p class="empty-message">' +
            'No penalties identified.' +
            '</p>';

        return;

    }


    penalties.forEach(function (penalty) {

        const item =
            document.createElement("div");


        item.className =
            "list-item penalty-item";


        item.innerHTML =
            "<span>⚠</span>" +
            "<p>" +
            escapeHTML(penalty) +
            "</p>";


        container.appendChild(item);

    });

}


// ============================================================
// CORE NOVELTY
// CONFLICT DETECTION
// ============================================================

function displayConflicts() {

    const conflicts =
        analysisData.conflicts || [];


    const container =
        document.getElementById(
            "conflictsContainer"
        );


    container.innerHTML = "";


    if (conflicts.length === 0) {

        container.innerHTML =
            '<div class="no-conflict">' +
            '✓ No potential conflicts detected based ' +
            'on the available evidence.' +
            '</div>';

        return;

    }


    conflicts.forEach(function (conflict) {

        const card =
            document.createElement("div");


        card.className =
            "conflict-card";


        card.innerHTML = `

            <div class="conflict-title">
                ⚠ Potential Conflict
            </div>

            <div class="conflict-section">

                <strong>Document Clause</strong>

                <p>
                    ${escapeHTML(
                        conflict.document_clause ||
                        "Not available"
                    )}
                </p>

            </div>


            <div class="conflict-section">

                <strong>Relevant Legal Provision</strong>

                <p>
                    ${escapeHTML(
                        conflict.legal_provision ||
                        "Not available"
                    )}
                </p>

            </div>


            <div class="conflict-section">

                <strong>Reason</strong>

                <p>
                    ${escapeHTML(
                        conflict.reason ||
                        "Potential inconsistency identified."
                    )}
                </p>

            </div>


            <div class="confidence">

                Confidence:
                ${escapeHTML(
                    String(
                        conflict.confidence ||
                        "Not available"
                    )
                )}

            </div>

        `;


        container.appendChild(card);

    });

}


// ============================================================
// RISK ASSESSMENT
// ============================================================

function displayRisk() {

    const risk =
        analysisData.risk || {};


    const level =
        risk.level || "NOT AVAILABLE";


    const explanation =
        risk.explanation ||
        "No risk explanation available.";


    const factors =
        risk.factors || [];


    document.getElementById(
        "riskLevel"
    ).innerText =
        level.toUpperCase();


    document.getElementById(
        "riskExplanation"
    ).innerText =
        explanation;


    const container =
        document.getElementById(
            "riskFactorsContainer"
        );


    container.innerHTML = "";


    if (factors.length === 0) {

        container.innerHTML =
            '<p class="empty-message">' +
            'No risk factors identified.' +
            '</p>';

        return;

    }


    factors.forEach(function (factor) {

        const item =
            document.createElement("div");


        item.className =
            "risk-factor";


        item.innerHTML = `

            <div>

                <strong>
                    ${escapeHTML(
                        factor.factor ||
                        "Risk Factor"
                    )}
                </strong>

                <p>
                    ${escapeHTML(
                        factor.reason ||
                        ""
                    )}
                </p>

            </div>


            <span class="risk-points">

                +${escapeHTML(
                    String(
                        factor.points || 0
                    )
                )}

            </span>

        `;


        container.appendChild(item);

    });

}


// ============================================================
// POSSIBLE ACTIONS
// ============================================================

function displayActions() {

    const actions =
        analysisData.actions || [];


    const container =
        document.getElementById(
            "actionsContainer"
        );


    container.innerHTML = "";


    if (actions.length === 0) {

        container.innerHTML =
            '<p class="empty-message">' +
            'No possible actions available.' +
            '</p>';

        return;

    }


    actions.forEach(function (action, index) {

        const item =
            document.createElement("div");


        item.className =
            "action-item";


        item.innerHTML = `

            <div class="action-number">

                ${index + 1}

            </div>


            <div>

                <p>

                    ${escapeHTML(
                        action.action ||
                        action ||
                        ""
                    )}

                </p>


                ${
                    action.reason
                    ?
                    `
                    <small>

                        Why:
                        ${escapeHTML(
                            action.reason
                        )}

                    </small>
                    `
                    :
                    ""
                }

            </div>

        `;


        container.appendChild(item);

    });

}


// ============================================================
// LEGAL EVIDENCE
// ============================================================

function displayEvidence() {

    const evidence =
        analysisData.evidence || [];


    const container =
        document.getElementById(
            "evidenceContainer"
        );


    container.innerHTML = "";


    if (evidence.length === 0) {

        container.innerHTML =
            '<p class="empty-message">' +
            'No legal evidence available.' +
            '</p>';

        return;

    }


    evidence.forEach(function (item) {

        const card =
            document.createElement("div");


        card.className =
            "evidence-card";


        card.innerHTML = `

            <div>

                <strong>
                    ${escapeHTML(
                        item.title ||
                        "Legal Provision"
                    )}
                </strong>

                <p>

                    ${escapeHTML(
                        item.description ||
                        ""
                    )}

                </p>

            </div>


            <div class="evidence-source">

                Source:
                ${escapeHTML(
                    item.source ||
                    "Not specified"
                )}

            </div>

        `;


        container.appendChild(card);

    });

}

// ============================================================
// EXPLAINABILITY
// ============================================================

function displayExplanation() {

    const explanation =
        analysisData.explanation;


    if (!explanation) {

        return;

    }


    const container =
        document.getElementById(
            "explanationContainer"
        );


    container.innerHTML = "";


    const steps =
        explanation.steps || [];


    steps.forEach(function (step, index) {

        const item =
            document.createElement("div");


        item.className =
            "reasoning-step";


        item.innerHTML = `

            <div class="step-number">

                ${index + 1}

            </div>


            <div>

                <strong>

                    ${escapeHTML(
                        step.title ||
                        "Reasoning Step"
                    )}

                </strong>


                <p>

                    ${escapeHTML(
                        step.description ||
                        ""
                    )}

                </p>

            </div>

        `;


        container.appendChild(item);

    });

}


// ============================================================
// QUESTION ANSWERING
// ============================================================

const askButton =
    document.getElementById(
        "askButton"
    );


const questionInput =
    document.getElementById(
        "questionInput"
    );


const answerContainer =
    document.getElementById(
        "answerContainer"
    );


if (askButton) {

    askButton.addEventListener(
        "click",
        askQuestion
    );

}


if (questionInput) {

    questionInput.addEventListener(
        "keydown",
        function (event) {

            if (event.key === "Enter") {

                askQuestion();

            }

        }
    );

}
async function runNLPAnalysis() {

    const extractedText =
        analysisData.extracted_text;

    if (!extractedText) {

        console.warn(
            "No extracted text available for NLP analysis."
        );

        return;
    }

    try {

        const response = await fetch(
            "http://127.0.0.1:8000/api/analyze",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    text: extractedText
                })
            }
        );

        const result =
            await response.json();

        if (!response.ok) {

            console.error(
                "NLP analysis failed:",
                result
            );

            return;
        }


        // --------------------------------------------------
        // NLP RESULTS
        // --------------------------------------------------

        analysisData.entities =
            result.entities || [];

        analysisData.legal_facts =
            result.legal_facts || {};


        // --------------------------------------------------
        // CLAUSE RESULTS
        // --------------------------------------------------

        analysisData.clauses =
            result.clauses || [];


        // --------------------------------------------------
        // LEGAL CATEGORIES
        // --------------------------------------------------

        analysisData.rights =
            result.rights || [];

        analysisData.obligations =
            result.obligations || [];

        analysisData.deadlines =
            result.deadlines || [];

        analysisData.termination =
            result.termination || [];

        analysisData.confidentiality =
            result.confidentiality || [];

        analysisData.payment =
            result.payment || [];

        analysisData.leave =
            result.leave || [];

        analysisData.dispute_resolution =
            result.dispute_resolution || [];
        analysisData.legal_evidence = result.legal_evidence || [];
        analysisData.evidence = result.evidence || [];
        analysisData.graph_reasoning = result.graph_reasoning || [];

        // --------------------------------------------------
        // SAVE UPDATED ANALYSIS
        // --------------------------------------------------

        sessionStorage.setItem(
            "analysisResult",
            JSON.stringify(analysisData)
        );


        console.log(
            "NLP analysis completed successfully.",
            result
        );

    } catch (error) {

        console.error(
            "NLP analysis connection error:",
            error
        );

    }
}

async function askQuestion() {

    const question =
        questionInput.value.trim();


    if (!question) {

        answerContainer.innerText =
            "Please enter a question.";

        return;

    }


    answerContainer.innerText =
        "Analyzing your question...";


    try {

        const response =
            await fetch(
                "http://127.0.0.1:8000/api/question",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        question: question,

                        document_context:
                            analysisData

                    })

                }
            );


        const result =
            await response.json();


        if (!response.ok) {

            answerContainer.innerText =
                result.detail ||
                "Unable to answer the question.";

            return;

        }


        displayQuestionAnswer(result);


    } catch (error) {

        console.error(error);


        answerContainer.innerText =
            "Unable to connect to the Law2Life AI server.";

    }

}


// ------------------------------------------------------------
// DISPLAY QUESTION ANSWER
// ------------------------------------------------------------

function displayQuestionAnswer(result) {

    answerContainer.innerHTML = `

        <div class="answer-content">

            <strong>Answer</strong>

            <p>
                ${escapeHTML(
                    result.answer ||
                    "No answer available."
                )}
            </p>


            ${
                result.evidence
                ?
                `
                <div class="answer-evidence">

                    <strong>
                        Supporting Evidence
                    </strong>

                    <p>
                        ${escapeHTML(
                            result.evidence
                        )}
                    </p>

                </div>
                `
                :
                ""
            }


            ${
                result.reason
                ?
                `
                <div class="answer-reason">

                    <strong>
                        Why
                    </strong>

                    <p>
                        ${escapeHTML(
                            result.reason
                        )}
                    </p>

                </div>
                `
                :
                ""
            }

        </div>

    `;

}


// ============================================================
// SECURITY HELPER
// ============================================================

function escapeHTML(value) {

    const div =
        document.createElement("div");


    div.textContent =
        value;


    return div.innerHTML;

}
// ============================================================
// KNOWLEDGE GRAPH REASONING
// ============================================================

function displayGraphReasoning() {

    const reasoning =
        analysisData.graph_reasoning || [];

    const container =
        document.getElementById(
            "graphReasoningContainer"
        );

    if (!container) {
        return;
    }

    container.innerHTML = "";

    if (reasoning.length === 0) {

        container.innerHTML = `
            <p class="empty-message">
                No Knowledge Graph reasoning was generated.
            </p>
        `;

        return;
    }

    reasoning.forEach(function (item) {

        const card =
            document.createElement("div");

        card.className =
            "graph-reasoning-card";

        const concepts =
            item.graph_reasoning || [];

        let conceptHTML = "";

        concepts.forEach(function (concept) {

            let relationsHTML = "";

            const relatedNodes =
                concept.related_nodes || [];

            relatedNodes.forEach(function (node) {

                relationsHTML += `
                    <div class="graph-relation">

                        <span>
                            ${escapeHTML(
                                node.relation || ""
                            )}
                        </span>

                        →

                        <strong>
                            ${escapeHTML(
                                node.node || ""
                            )}
                        </strong>

                    </div>
                `;
            });

            let reasoningHTML = "";

            const reasoningItems =
                concept.reasoning || [];

            reasoningItems.forEach(function (reason) {

                reasoningHTML += `
                    <div class="graph-finding">

                        <strong>
                            ${escapeHTML(
                                reason.aspect || ""
                            )}
                        </strong>

                        <p>
                            ${escapeHTML(
                                reason.finding || ""
                            )}
                        </p>

                    </div>
                `;
            });

            conceptHTML += `
                <div class="graph-concept">

                    <h4>
                        ${escapeHTML(
                            concept.concept || ""
                        )}
                    </h4>

                    <div class="graph-label">
                        Related Concepts
                    </div>

                    ${relationsHTML}

                    ${
                        reasoningHTML
                            ? `
                                <div class="graph-label">
                                    Contextual Findings
                                </div>

                                ${reasoningHTML}
                            `
                            : ""
                    }

                </div>
            `;
        });

        const detectedConcepts =
            item.detected_concepts || [];

        card.innerHTML = `

            <div class="graph-clause">

                <div class="graph-category">
                    ${escapeHTML(
                        item.category ||
                        "Document Clause"
                    )}
                </div>

                <h3>
                    Document Clause
                </h3>

                <p>
                    ${escapeHTML(
                        item.clause || ""
                    )}
                </p>

            </div>

            <div class="graph-detected">

                <strong>
                    Detected Concepts:
                </strong>

                <span>
                    ${
                        detectedConcepts.length
                            ? detectedConcepts
                                .map(function (concept) {
                                    return escapeHTML(
                                        concept
                                    );
                                })
                                .join(", ")
                            : "None"
                    }
                </span>

            </div>

            ${conceptHTML}

        `;

        container.appendChild(card);

    });
}
// ============================================================
// DASHBOARD TAB SWITCHING
// ============================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        const tabs =
            document.querySelectorAll(
                ".dashboard-tab"
            );

        const contents =
            document.querySelectorAll(
                ".tab-content"
            );

        tabs.forEach(function (tab) {

            tab.addEventListener(
                "click",
                function () {

                    const selectedTab =
                        tab.dataset.tab;

                    tabs.forEach(function (item) {
                        item.classList.remove("active");
                    });

                    contents.forEach(function (content) {
                        content.classList.remove(
                            "active-tab"
                        );
                    });

                    tab.classList.add("active");

                    contents.forEach(
                        function (content) {

                            if (
                                content.dataset.tabContent ===
                                selectedTab
                            ) {

                                content.classList.add(
                                    "active-tab"
                                );

                            }

                        }
                    );
                }
            );
        });
    }
);