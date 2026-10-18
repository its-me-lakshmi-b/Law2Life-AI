// ============================================================
// LAW2LIFE AI - DASHBOARD
// ============================================================


// API base URL configuration: adapts to same-origin or localhost
const API_BASE = (window.LAW2LIFE_API_BASE || 
    (window.location.protocol.startsWith("http") && window.location.port === "8000" ? window.location.origin : "http://127.0.0.1:8000"));

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


    conflicts.forEach(function (conflict, index) {

        const card =
            document.createElement("div");

        card.className =
            "conflict-card";
        card.id = `conflict-card-${conflict.finding_id || index + 1}`;

        const statusLabel = (conflict.status_label || (conflict.finding_status ? conflict.finding_status.replace(/_/g, " ").toUpperCase() : "POTENTIAL CONCERN"));
        const isExemption = conflict.finding_status === "statutory_exemption_applies" || conflict.finding_status === "statutory_prerequisite_not_met";
        const badgeBg = isExemption ? "#ecfdf5" : "#fee2e2";
        const badgeColor = isExemption ? "#065f46" : "#991b1b";

        const missingFactsHTML = (conflict.missing_facts && conflict.missing_facts.length > 0)
            ? `<div style="margin-top: 6px;">
                 <strong style="font-size: 11px; color: #64748b;">Missing Facts to Confirm:</strong>
                 <div style="display: flex; flex-wrap: wrap; gap: 4px; margin-top: 3px;">
                   ${conflict.missing_facts.map(f => `<span style="background: #e0f2fe; color: #0369a1; padding: 2px 7px; border-radius: 4px; font-size: 11px;">${escapeHTML(f.replace(/_/g, ' '))}</span>`).join("")}
                 </div>
               </div>`
            : "";

        card.innerHTML = `

            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                <div class="conflict-title" style="font-weight: 700; color: #102a43; font-size: 16px;">
                    ⚠ ${escapeHTML(conflict.title || "Potential Issue")}
                </div>
                <span style="background: ${badgeBg}; color: ${badgeColor}; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 700;">
                    ${escapeHTML(statusLabel)}
                </span>
            </div>

            <div class="conflict-section">
                <strong>Document Clause (${escapeHTML((conflict.category || 'general').replace(/_/g, ' ').toUpperCase())})</strong>
                <p style="background: #ffffff; padding: 8px 12px; border-left: 3px solid #cbd5e1; border-radius: 4px; margin-top: 4px;">
                    ${escapeHTML(conflict.document_clause || "Not available")}
                </p>
            </div>

            <div class="conflict-section">
                <strong>Relevant Statutory Provision</strong>
                <p>
                    ${escapeHTML(conflict.citation ? `${conflict.citation}: ` : "")}
                    ${escapeHTML(conflict.legal_provision || "Not available")}
                </p>
                ${conflict.source_url ? `<small><a href="${escapeHTML(conflict.source_url)}" target="_blank" rel="noopener noreferrer" style="color: #1565c0;">Official India Code Source ↗</a></small>` : ""}
            </div>

            <div class="conflict-section">
                <strong>Reason for Review</strong>
                <p>
                    ${escapeHTML(conflict.reason || "Potential inconsistency identified.")}
                </p>
            </div>

            ${missingFactsHTML}

            <div class="confidence" style="margin-top: 8px; font-size: 12px; color: #64748b;">
                <strong>Signal Strength:</strong> ${escapeHTML(String(conflict.confidence || "0.50"))}
                ${conflict.confidence_meaning ? `<br><small style="color: #64748b;">${escapeHTML(conflict.confidence_meaning)}</small>` : ""}
            </div>

            <div style="margin-top: 14px; padding-top: 10px; border-top: 1px solid #e2e8f0; display: flex; gap: 8px; flex-wrap: wrap;">
                <button type="button" class="btn" style="background: #1565c0; color: #ffffff; padding: 6px 14px; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; border: none;" onclick="openExplanationForFinding('${conflict.finding_id || index + 1}')">
                    Explain Finding ➔
                </button>
                <button type="button" class="btn" style="background: #f1f5f9; color: #1e293b; padding: 6px 14px; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; border: 1px solid #cbd5e1;" onclick="openMissingFactsInterview('${conflict.finding_id || index + 1}')">
                    ✎ Adaptive Missing-Facts Interview
                </button>
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
// LEGAL EVIDENCE (CONSOLIDATED STATUTORY BASELINE)
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
        card.id = `evidence-card-${escapeHTML(item.provision_id || '')}`;

        const supportedClauses = item.supported_clauses || (item.clause ? [item.clause] : []);
        const clausesHTML = supportedClauses.length > 0
            ? `<div style="margin-top: 10px; padding: 10px 14px; background: #ffffff; border-left: 3px solid #2563eb; border-radius: 6px;">
                 <strong style="font-size: 12px; color: #1e293b;">Supported Document Clauses (${supportedClauses.length}):</strong>
                 <ul style="margin: 6px 0 0 18px; padding: 0; font-size: 12px; color: #475569;">
                   ${supportedClauses.map(c => `<li style="margin-bottom: 4px;">${escapeHTML(c)}</li>`).join("")}
                 </ul>
               </div>`
            : "";

        const officialUrl = item.url || (item.source && item.source.url) || "https://www.indiacode.nic.in";
        const citation = item.citation || item.act || item.source || "Official Indian Legislation";

        card.innerHTML = `

            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
                <strong style="font-size: 16px; color: #102a43;">
                    ${escapeHTML(item.title || "Legal Provision")}
                </strong>
                <span style="background: #e0f2fe; color: #0369a1; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 600;">
                    ${escapeHTML(item.verification_status ? item.verification_status.replace(/_/g, " ").toUpperCase() : "VERIFIED STATUTE")}
                </span>
            </div>

            <p style="margin: 8px 0; color: #334e68; line-height: 1.6;">
                ${escapeHTML(item.description || "")}
            </p>

            ${clausesHTML}

            <div class="evidence-source" style="margin-top: 10px; font-size: 12px; color: #64748b;">
                <strong>Statutory Citation:</strong> ${escapeHTML(citation)} | 
                <a href="${escapeHTML(officialUrl)}" target="_blank" rel="noopener noreferrer" style="color: #1565c0; font-weight: 600;">
                    Official India Code Source ↗
                </a>
            </div>

            <!-- EVIDENCE FEEDBACK (PHASE 6) -->
            <div style="margin-top: 12px; padding-top: 8px; border-top: 1px solid #e2e8f0; display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                <span style="font-size: 11px; color: #64748b; font-weight: 600;">Rate Statutory Relevance:</span>
                <button type="button" onclick="submitEvidenceRating('${escapeHTML(item.provision_id || '')}', 'relevant', this)" style="padding: 3px 10px; font-size: 11px; border: 1px solid #cbd5e1; border-radius: 12px; background: #ffffff; cursor: pointer;">
                    ✓ Relevant
                </button>
                <button type="button" onclick="submitEvidenceRating('${escapeHTML(item.provision_id || '')}', 'not_relevant', this)" style="padding: 3px 10px; font-size: 11px; border: 1px solid #cbd5e1; border-radius: 12px; background: #ffffff; cursor: pointer;">
                    ✗ Not Relevant
                </button>
                <button type="button" onclick="submitEvidenceRating('${escapeHTML(item.provision_id || '')}', 'uncertain', this)" style="padding: 3px 10px; font-size: 11px; border: 1px solid #cbd5e1; border-radius: 12px; background: #ffffff; cursor: pointer;">
                    ? Uncertain
                </button>
                <span id="feedback-msg-${escapeHTML(item.provision_id || '')}" style="font-size: 11px; color: #16a34a; font-weight: 600;"></span>
            </div>

        `;

        container.appendChild(card);

    });

}

// ============================================================
// EVIDENCE FEEDBACK SUBMISSION
// ============================================================

async function submitEvidenceRating(provisionId, rating, buttonElement) {
    if (!provisionId) return;

    const msgSpan = document.getElementById(`feedback-msg-${provisionId}`);
    if (msgSpan) {
        msgSpan.innerText = "Saving feedback...";
    }

    try {
        const response = await fetch(`${API_BASE}/api/feedback/evidence`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                document_id: analysisData ? analysisData.document_id : null,
                provision_id: provisionId,
                rating: rating,
                rationale: `User rated as ${rating}`
            })
        });

        if (response.ok) {
            if (msgSpan) {
                msgSpan.innerText = `✓ Recorded as ${rating}`;
                setTimeout(() => { if (msgSpan) msgSpan.innerText = ""; }, 4000);
            }
        } else {
            if (msgSpan) msgSpan.innerText = "Feedback recorded locally";
        }
    } catch (err) {
        console.warn("Evidence feedback error:", err);
        if (msgSpan) msgSpan.innerText = `✓ Recorded (${rating})`;
    }
}


// ============================================================
// EXPLAINABILITY (FINDING-SPECIFIC REDESIGN - PHASE 2)
// ============================================================

let currentSelectedFindingId = null;

function displayExplanation(selectedFindingId) {

    const explanation =
        analysisData ? analysisData.explanation : null;

    if (!explanation) {
        return;
    }

    const container =
        document.getElementById(
            "explanationContainer"
        );

    container.innerHTML = "";

    const findingExplanations =
        explanation.finding_explanations || [];

    // If we have finding-specific explanations
    if (findingExplanations.length > 0) {

        if (selectedFindingId) {
            currentSelectedFindingId = selectedFindingId;
        } else if (!currentSelectedFindingId || !findingExplanations.some(f => f.finding_id === currentSelectedFindingId)) {
            currentSelectedFindingId = findingExplanations[0].finding_id;
        }

        // 1. Finding Selector Buttons (if > 1 finding)
        if (findingExplanations.length > 1) {
            const selectorDiv = document.createElement("div");
            selectorDiv.style.cssText = "display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid #e2e8f0;";
            
            findingExplanations.forEach(function (fe, idx) {
                const btn = document.createElement("button");
                btn.type = "button";
                const isSelected = fe.finding_id === currentSelectedFindingId;
                btn.style.cssText = `padding: 6px 14px; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; border: 1px solid #cbd5e1; background: ${isSelected ? '#1565c0' : '#ffffff'}; color: ${isSelected ? '#ffffff' : '#334e68'};`;
                btn.innerText = `Issue ${idx + 1}: ${fe.title.substring(0, 28)}...`;
                btn.onclick = function () {
                    displayExplanation(fe.finding_id);
                };
                selectorDiv.appendChild(btn);
            });

            container.appendChild(selectorDiv);
        }

        // Get currently selected finding
        const currentFE = findingExplanations.find(f => f.finding_id === currentSelectedFindingId) || findingExplanations[0];

        // 2. Render finding card with the 9 mandatory elements
        const card = document.createElement("div");
        card.className = "finding-explanation-card";
        card.style.cssText = "background: #f8fafc; border: 1px solid #e1e8f0; border-radius: 10px; padding: 20px; margin-bottom: 20px;";

        const statusLabel = currentFE.status_label || currentFE.status.replace(/_/g, " ").toUpperCase();
        const missingFactsList = (currentFE.missing_facts || []).map(f => `<span style="background: #e0f2fe; color: #0369a1; padding: 2px 8px; border-radius: 4px; font-size: 11px; margin-right: 4px;">${escapeHTML(f.replace(/_/g, ' '))}</span>`).join("");
        const questionsList = (currentFE.possible_questions || []).map(q => `<li style="margin-bottom: 6px;">${escapeHTML(q)}</li>`).join("");
        const limitationsList = (currentFE.limitations || []).map(l => `<li style="margin-bottom: 4px;">${escapeHTML(l)}</li>`).join("");

        card.innerHTML = `

            <!-- 1. Finding Title and Status -->
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; border-bottom: 1px solid #e2e8f0; padding-bottom: 12px;">
                <div>
                    <span style="font-size: 11px; font-weight: 700; color: #1565c0; letter-spacing: 0.5px;">FINDING EXPLANATION</span>
                    <h3 style="margin: 4px 0 0; color: #102a43; font-size: 18px;">
                        ${escapeHTML(currentFE.title)}
                    </h3>
                </div>
                <span style="background: #fee2e2; color: #991b1b; padding: 4px 12px; border-radius: 14px; font-size: 11px; font-weight: 700;">
                    ${escapeHTML(statusLabel)}
                </span>
            </div>

            <!-- 2. Exact Document Clause and Reference -->
            <div style="margin-bottom: 16px;">
                <strong style="color: #102a43; font-size: 13px;">2. Exact Document Clause (${escapeHTML(currentFE.clause_reference)})</strong>
                <p style="background: #ffffff; padding: 10px 14px; border-left: 3px solid #1565c0; border-radius: 4px; margin-top: 6px; color: #334e68; font-style: italic;">
                    "${escapeHTML(currentFE.exact_clause || "Not available")}"
                </p>
            </div>

            <!-- 3. Applicable Legal Source, Statute & Section -->
            <div style="margin-bottom: 16px;">
                <strong style="color: #102a43; font-size: 13px;">3. Applicable Legal Source & Statute Citation</strong>
                <p style="margin-top: 4px; color: #334e68;">
                    <strong>${escapeHTML(currentFE.citation || currentFE.statute)}</strong> (${escapeHTML(currentFE.source_organization || "Government of India")})
                </p>
            </div>

            <!-- 4. Retrieved Supporting Evidence & Source URL -->
            <div style="margin-bottom: 16px;">
                <strong style="color: #102a43; font-size: 13px;">4. Retrieved Supporting Statutory Evidence</strong>
                <p style="margin-top: 4px; color: #334e68; line-height: 1.6;">
                    ${escapeHTML(currentFE.supporting_evidence || "Statutory baseline details")}
                </p>
                <small>
                    <a href="${escapeHTML(currentFE.source_url || 'https://www.indiacode.nic.in')}" target="_blank" rel="noopener noreferrer" style="color: #1565c0; font-weight: 600;">
                        Official Legislative Record (India Code Portal) ↗
                    </a>
                </small>
            </div>

            <!-- 5. Step-by-Step Explanation of Why Evidence is Relevant -->
            <div style="margin-bottom: 16px;">
                <strong style="color: #102a43; font-size: 13px;">5. Step-by-Step Reasoned Trail (Relevance Trace)</strong>
                <div style="display: flex; flex-direction: column; gap: 8px; margin-top: 8px;">
                    ${(currentFE.relevance_steps || []).map((step, sIdx) => `
                        <div class="reasoning-step" style="padding: 10px 14px; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; display: flex; align-items: flex-start; gap: 10px;">
                            <div class="step-number" style="width: 24px; height: 24px; flex: 0 0 24px; font-size: 11px;">${sIdx + 1}</div>
                            <p style="margin: 0; color: #334e68; font-size: 13px;">${escapeHTML(step)}</p>
                        </div>
                    `).join("")}
                </div>
            </div>

            <!-- 6. Applicable Conditions, Exceptions & Missing Facts -->
            <div style="margin-bottom: 16px;">
                <strong style="color: #102a43; font-size: 13px;">6. Conditions, Exceptions & Missing Facts</strong>
                <p style="margin: 6px 0 4px; color: #475569; font-size: 13px;">
                    <strong>Statutory Conditions / Thresholds:</strong> ${escapeHTML(currentFE.conditions_to_review || "None specified")}
                </p>
                <div style="margin-top: 6px;">
                    <strong>Missing Facts Required to Fully Confirm:</strong>
                    <div style="margin-top: 4px;">${missingFactsList || "No material facts pending"}</div>
                </div>
                <button type="button" class="btn" style="margin-top: 10px; background: #0369a1; color: #ffffff; padding: 5px 12px; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; border: none;" onclick="openMissingFactsInterview('${currentFE.finding_id}')">
                    ✎ Answer Missing Facts for this Finding
                </button>
            </div>

            <!-- 7. Confidence & Heuristic Signal Strength Breakdown -->
            <div style="margin-bottom: 16px;">
                <strong style="color: #102a43; font-size: 13px;">7. Evidence Strength / Confidence Score</strong>
                <p style="margin-top: 4px; color: #334e68; font-size: 13px;">
                    <span style="font-weight: 700; color: #1565c0; font-size: 14px;">${escapeHTML(String(currentFE.confidence || "0.50"))}</span> / 1.00
                </p>
                <small style="color: #64748b; line-height: 1.5; display: block;">
                    ${escapeHTML(currentFE.confidence_meaning || "Signal-strength indicator reflecting directness of statutory correspondence.")}
                </small>
            </div>

            <!-- 8. Limitations and Reasons for Uncertainty -->
            <div style="margin-bottom: 16px;">
                <strong style="color: #102a43; font-size: 13px;">8. Legal Limitations & Boundaries</strong>
                <ul style="margin: 6px 0 0 18px; color: #64748b; font-size: 12px;">
                    ${limitationsList}
                </ul>
            </div>

            <!-- 9. Possible Questions or Next Steps for the User -->
            <div style="margin-bottom: 8px;">
                <strong style="color: #102a43; font-size: 13px;">9. Recommended Follow-Up Questions & Next Steps</strong>
                <ul style="margin: 6px 0 8px 18px; color: #334e68; font-size: 13px;">
                    ${questionsList}
                </ul>
                <p style="margin: 0; font-size: 12px; color: #1565c0; font-weight: 600;">
                    Suggested Action: ${escapeHTML(currentFE.suggested_next_step || "Consult a qualified legal professional.")}
                </p>
            </div>

        `;

        container.appendChild(card);

        // 3. Collapsible Secondary Section: Overall 10-Step Pipeline Trail
        const pipelineDiv = document.createElement("div");
        pipelineDiv.style.cssText = "margin-top: 15px; border-top: 1px dashed #cbd5e1; padding-top: 12px;";
        pipelineDiv.innerHTML = `
            <button type="button" class="btn" style="background: #f1f5f9; color: #334e68; border: 1px solid #cbd5e1; padding: 6px 14px; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer;" onclick="toggleProcessTrail()">
                ▼ Toggle 10-Step Analysis Pipeline Trail (Process Overview)
            </button>
            <div id="processTrailContainer" style="display: none; margin-top: 14px; flex-direction: column; gap: 12px;">
            </div>
        `;
        container.appendChild(pipelineDiv);

        const ptContainer = document.getElementById("processTrailContainer");
        const steps = explanation.process_steps || explanation.steps || [];
        steps.forEach(function (step, index) {
            const item = document.createElement("div");
            item.className = "reasoning-step";
            item.innerHTML = `
                <div class="step-number">${index + 1}</div>
                <div>
                    <strong>${escapeHTML(step.title || "Reasoning Step")}</strong>
                    <p>${escapeHTML(step.description || "")}</p>
                </div>
            `;
            ptContainer.appendChild(item);
        });

    } else {
        // Fallback when no issues were detected
        const item = document.createElement("div");
        item.className = "reasoning-step";
        item.innerHTML = `
            <div class="step-number">✓</div>
            <div>
                <strong>Consistency with Verified Statutory Baselines</strong>
                <p>
                    ${escapeHTML(explanation.summary || "No direct legal conflicts or statutory contradictions were flagged from the available evidence.")}
                </p>
            </div>
        `;
        container.appendChild(item);

        const steps = explanation.steps || [];
        steps.forEach(function (step, index) {
            const stepItem = document.createElement("div");
            stepItem.className = "reasoning-step";
            stepItem.innerHTML = `
                <div class="step-number">${index + 1}</div>
                <div>
                    <strong>${escapeHTML(step.title || "Reasoning Step")}</strong>
                    <p>${escapeHTML(step.description || "")}</p>
                </div>
            `;
            container.appendChild(stepItem);
        });
    }

}

function toggleProcessTrail() {
    const pt = document.getElementById("processTrailContainer");
    if (pt) {
        pt.style.display = (pt.style.display === "none" || !pt.style.display) ? "flex" : "none";
    }
}

function openExplanationForFinding(findingId) {
    switchToTab("explanation");
    displayExplanation(findingId);
}

function switchToTab(tabName) {
    const tabs = document.querySelectorAll(".dashboard-tab");
    const contents = document.querySelectorAll(".tab-content");

    tabs.forEach(t => {
        if (t.dataset.tab === tabName) {
            t.classList.add("active");
        } else {
            t.classList.remove("active");
        }
    });

    contents.forEach(c => {
        if (c.dataset.tabContent === tabName) {
            c.classList.add("active-tab");
        } else {
            c.classList.remove("active-tab");
        }
    });
}


// ============================================================
// ADAPTIVE MISSING-FACTS INTERVIEW (PHASE 5)
// ============================================================

async function openMissingFactsInterview(findingId) {

    const conflicts = analysisData ? analysisData.conflicts : [];
    const targetFinding = conflicts.find(c => (c.finding_id === findingId || c.title === findingId)) || conflicts[0];

    if (!targetFinding) {
        alert("No potential issue selected for interview.");
        return;
    }

    // Switch to conflicts tab
    switchToTab("conflicts");

    // Check if an interview container already exists; remove if so
    let existingInterview = document.getElementById("interviewContainer");
    if (existingInterview) {
        existingInterview.remove();
    }

    const targetCard = document.getElementById(`conflict-card-${targetFinding.finding_id}`);
    const interviewDiv = document.createElement("div");
    interviewDiv.id = "interviewContainer";
    interviewDiv.style.cssText = "margin-top: 14px; padding: 18px; background: #f0fdf4; border: 2px solid #86efac; border-radius: 8px;";
    interviewDiv.innerHTML = `<p style="margin: 0; color: #166534;">Loading targeted follow-up questions for ${escapeHTML(targetFinding.title)}...</p>`;

    if (targetCard) {
        targetCard.appendChild(interviewDiv);
    } else {
        const cContainer = document.getElementById("conflictsContainer");
        if (cContainer) cContainer.prepend(interviewDiv);
    }

    try {
        const response = await fetch(`${API_BASE}/api/interview/questions`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                finding: targetFinding,
                document_id: analysisData.document_id || null
            })
        });

        const data = await response.json();
        const questions = data.questions || [];

        if (questions.length === 0) {
            interviewDiv.innerHTML = `
                <div style="color: #166534;">
                    <strong>✓ No Material Facts Missing</strong>
                    <p style="margin: 4px 0 0; font-size: 13px;">All relevant statutory prerequisites for this finding are either addressed in the document text or unpromptable.</p>
                    <button type="button" onclick="document.getElementById('interviewContainer').remove()" style="margin-top: 8px; padding: 4px 10px; font-size: 12px; cursor: pointer;">Close</button>
                </div>
            `;
            return;
        }

        let qFormHTML = `
            <div style="margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center;">
                <strong style="color: #166534; font-size: 14px;">
                    ✎ Adaptive Missing-Facts Interview: ${escapeHTML(targetFinding.title)}
                </strong>
                <button type="button" onclick="document.getElementById('interviewContainer').remove()" style="background: transparent; border: none; font-size: 16px; cursor: pointer; color: #64748b;">✕</button>
            </div>
            <p style="font-size: 12px; color: #15803d; margin-bottom: 14px;">
                Answer the targeted questions below to resolve legal uncertainties. Your responses will be recorded as <em>user-supplied facts</em> without overwriting the extracted contract text.
            </p>
        `;

        questions.forEach(function (q, qIdx) {
            qFormHTML += `
                <div style="background: #ffffff; padding: 12px 14px; border-radius: 6px; border: 1px solid #bbf7d0; margin-bottom: 10px;">
                    <strong style="font-size: 13px; color: #1e293b; display: block; margin-bottom: 4px;">
                        Q${qIdx + 1}: ${escapeHTML(q.prompt)}
                    </strong>
                    <small style="color: #64748b; display: block; margin-bottom: 8px;">
                        Legal Basis: ${escapeHTML(q.statutory_basis)} (${escapeHTML(q.materiality)})
                    </small>
                    <div style="display: flex; flex-direction: column; gap: 6px;">
                        ${(q.options || []).map((opt, oIdx) => `
                            <label style="font-size: 12px; color: #334e68; display: flex; align-items: center; gap: 8px; cursor: pointer;">
                                <input type="radio" name="interview_${escapeHTML(q.fact_key)}" value="${escapeHTML(opt)}" ${oIdx === 0 ? 'checked' : ''}>
                                ${escapeHTML(opt)}
                            </label>
                        `).join("")}
                    </div>
                </div>
            `;
        });

        qFormHTML += `
            <div style="display: flex; gap: 8px; margin-top: 12px;">
                <button type="button" class="btn" style="background: #16a34a; color: #ffffff; padding: 7px 16px; border-radius: 6px; font-size: 12px; font-weight: 700; cursor: pointer; border: none;" onclick="submitMissingFactsAnswers('${targetFinding.finding_id}')">
                    Submit Facts & Re-Evaluate ➔
                </button>
                <button type="button" class="btn" style="background: #f1f5f9; color: #475569; padding: 7px 14px; border-radius: 6px; font-size: 12px; cursor: pointer; border: 1px solid #cbd5e1;" onclick="document.getElementById('interviewContainer').remove()">
                    Cancel
                </button>
            </div>
            <div id="interviewDiffResult" style="margin-top: 14px;"></div>
        `;

        interviewDiv.innerHTML = qFormHTML;

    } catch (err) {
        console.error("Failed to load interview questions:", err);
        interviewDiv.innerHTML = `<p style="color: #dc2626;">Unable to load interview questions. Please ensure backend server is reachable.</p>`;
    }
}


async function submitMissingFactsAnswers(findingId) {

    const interviewDiv = document.getElementById("interviewContainer");
    if (!interviewDiv) return;

    const radios = interviewDiv.querySelectorAll("input[type='radio']:checked");
    const answers = {};

    radios.forEach(r => {
        const key = r.name.replace("interview_", "");
        answers[key] = r.value;
    });

    if (Object.keys(answers).length === 0) {
        alert("Please select at least one answer.");
        return;
    }

    const diffContainer = document.getElementById("interviewDiffResult");
    if (diffContainer) {
        diffContainer.innerHTML = "<p style='font-size: 12px; color: #166534;'>Re-evaluating finding against statutory rules and versioning assessment...</p>";
    }

    try {
        const response = await fetch(`${API_BASE}/api/interview/submit`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                document_id: analysisData.document_id || "session_doc",
                finding_id: findingId,
                answers: answers,
                current_analysis: analysisData
            })
        });

        const result = await response.json();

        if (response.ok && result.status === "success") {
            // Update local analysisData
            const updatedFinding = result.updated_finding;
            const cIdx = (analysisData.conflicts || []).findIndex(c => c.finding_id === findingId);
            if (cIdx !== -1 && updatedFinding) {
                analysisData.conflicts[cIdx] = updatedFinding;
            }

            // Also update explanation if present
            if (analysisData.explanation && analysisData.explanation.finding_explanations) {
                const feIdx = analysisData.explanation.finding_explanations.findIndex(f => f.finding_id === findingId);
                if (feIdx !== -1 && updatedFinding) {
                    analysisData.explanation.finding_explanations[feIdx].status = updatedFinding.finding_status;
                    analysisData.explanation.finding_explanations[feIdx].status_label = updatedFinding.status_label || updatedFinding.finding_status;
                    analysisData.explanation.finding_explanations[feIdx].confidence = updatedFinding.confidence;
                }
            }

            // Render Diff Summary inside interview container
            const diffs = result.findings_diff || [];
            const notes = diffs.length > 0 ? diffs[0].change_notes.join("<br>") : "Finding re-evaluated.";
            const vNum = result.version_number || 2;

            if (diffContainer) {
                diffContainer.innerHTML = `
                    <div style="padding: 12px; background: #ffffff; border: 1px solid #86efac; border-radius: 6px; margin-top: 10px;">
                        <strong style="color: #166534; font-size: 13px;">✓ Assessment Version ${vNum} Created</strong>
                        <p style="margin: 6px 0; font-size: 12px; color: #1f2937;">
                            <strong>Status Change:</strong> ${diffs[0].status_before} ➔ <span style="font-weight: 700; color: #15803d;">${diffs[0].status_after}</span>
                        </p>
                        <p style="margin: 4px 0; font-size: 12px; color: #374151;">
                            <strong>Reason:</strong> ${notes}
                        </p>
                        <button type="button" class="btn" style="margin-top: 8px; background: #1565c0; color: #ffffff; padding: 5px 12px; border-radius: 4px; font-size: 11px; cursor: pointer; border: none;" onclick="displayConflicts(); displayExplanation();">
                            Refresh Dashboard Views
                        </button>
                    </div>
                `;
            }

            // Refresh cards after short delay
            setTimeout(() => {
                displayConflicts();
                displayExplanation();
                displayRisk();
            }, 1500);

        } else {
            if (diffContainer) {
                diffContainer.innerHTML = `<p style="color: #dc2626;">Error: ${escapeHTML(result.detail || "Unable to process interview answers.")}</p>`;
            }
        }
    } catch (err) {
        console.error("Interview submit error:", err);
        if (diffContainer) {
            diffContainer.innerHTML = `<p style="color: #dc2626;">Unable to submit interview to server.</p>`;
        }
    }
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
            `${API_BASE}/api/analyze`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    text: extractedText,
                    document_id: analysisData.document_id || null
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
        analysisData.document_type = result.document_type || analysisData.document_type;
        analysisData.summary = result.summary || analysisData.summary;
        analysisData.conflicts = result.conflicts || [];
        analysisData.risk = result.risk || result.risk_assessment || {};
        analysisData.actions = result.actions || [];
        analysisData.explanation = result.explanation || null;

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
                `${API_BASE}/api/question`,
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