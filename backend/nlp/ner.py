import re
import spacy


# --------------------------------------------------
# LOAD SPACY MODEL
# --------------------------------------------------

nlp = spacy.load("en_core_web_sm")


# --------------------------------------------------
# GENERIC ENTITY EXTRACTION
# --------------------------------------------------

def extract_entities(text):

    if not text:
        return []

    # Normalize whitespace so the NLP model receives
    # clean continuous text.
    normalized_text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    doc = nlp(normalized_text)

    entities = []

    for entity in doc.ents:

        entities.append({
            "text": entity.text.strip(),
            "label": entity.label_
        })

    return entities


# --------------------------------------------------
# LEGAL FACT EXTRACTION
# --------------------------------------------------

def extract_legal_facts(text):
    """
    Extract structured legal facts from document text.
    Supports employment agreements, rental/lease agreements, and general contracts.
    """
    facts = {
        "employee": None,
        "employer": None,
        "position": None,
        "start_date": None,
        "salary": None,
        "work_location": None,
        "notice_period": None,
        "leave_notice": None,
        "tenant": None,
        "landlord": None,
        "rent": None,
        "security_deposit": None,
        "lease_period": None,
        "governing_law": None
    }

    if not text:
        return facts

    normalized_text = re.sub(r"\s+", " ", text).strip()

    # --------------------------------------------------
    # EMPLOYEE / TENANT / PARTIES
    # --------------------------------------------------
    # Format 1: "Employee Ananya Rao Employer"
    m = re.search(r"\bEmployee[:\s]+([A-Z][A-Za-z. ]+?)(?=\s+(?:Employer|Position|hereinafter|\n|$))", normalized_text, re.IGNORECASE)
    if m:
        facts["employee"] = m.group(1).strip()
    else:
        # Format 2: "hereinafter referred to as the 'Employee', [Name]" or "Name (the 'Employee')"
        m2 = re.search(r"([A-Z][A-Za-z. ]+?)\s*\((?:the\s+)?[\"']Employee[\"']\)", normalized_text, re.IGNORECASE)
        if m2:
            facts["employee"] = m2.group(1).strip()

    # Tenant
    mt = re.search(r"\bTenant[:\s]+([A-Z][A-Za-z. ]+?)(?=\s+(?:Landlord|Lessor|Premises|hereinafter|The|Rent|Monthly|Security|Clause|\d+\.|$))", normalized_text, re.IGNORECASE)
    if mt:
        facts["tenant"] = mt.group(1).strip()
    else:
        mt2 = re.search(r"([A-Z][A-Za-z. ]+?)\s*\((?:the\s+)?[\"']Tenant[\"']\)", normalized_text, re.IGNORECASE)
        if mt2:
            facts["tenant"] = mt2.group(1).strip()

    # --------------------------------------------------
    # EMPLOYER / LANDLORD
    # --------------------------------------------------
    # Format 1: "Employer ABC Technologies Pvt. Ltd. Position"
    m_er = re.search(r"\bEmployer[:\s]+([A-Za-z0-9&.,\- ]+?)(?=\s+(?:Position|Employee|Start Date|hereinafter|The|\n|$))", normalized_text, re.IGNORECASE)
    if m_er:
        facts["employer"] = m_er.group(1).strip()
    else:
        m_er2 = re.search(r"([A-Za-z0-9&.,\- ]+?)\s*\((?:the\s+)?[\"']Employer[\"']\)", normalized_text, re.IGNORECASE)
        if m_er2:
            facts["employer"] = m_er2.group(1).strip()

    # Landlord / Lessor
    ml = re.search(r"\b(?:Landlord|Lessor)[:\s]+([A-Za-z0-9&.,\- ]+?)(?=\s+(?:Tenant|Premises|hereinafter|The|Rent|Monthly|Security|Clause|\d+\.|$))", normalized_text, re.IGNORECASE)
    if ml:
        facts["landlord"] = ml.group(1).strip()
    else:
        ml2 = re.search(r"([A-Za-z0-9&.,\- ]+?)\s*\((?:the\s+)?[\"'](?:Landlord|Lessor)[\"']\)", normalized_text, re.IGNORECASE)
        if ml2:
            facts["landlord"] = ml2.group(1).strip()

    # --------------------------------------------------
    # POSITION / ROLE
    # --------------------------------------------------
    mp = re.search(r"\bPosition[:\s]+([A-Za-z0-9/&.,\- ]+?)(?=\s+(?:Start Date|Department|Salary|\n|$))", normalized_text, re.IGNORECASE)
    if mp:
        facts["position"] = mp.group(1).strip()
    else:
        mp2 = re.search(r"\bas\s+a\s+([A-Z][A-Za-z ]+?)\s+for\s+the\s+Employer", normalized_text, re.IGNORECASE)
        if mp2:
            facts["position"] = mp2.group(1).strip()

    # --------------------------------------------------
    # START DATE / COMMENCEMENT
    # --------------------------------------------------
    msd = re.search(r"\bStart Date[:\s]+([0-9]{1,2}\s+[A-Za-z]+\s+[0-9]{4}|[0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})", normalized_text, re.IGNORECASE)
    if msd:
        facts["start_date"] = msd.group(1).strip()
    else:
        msd2 = re.search(r"\bbeginning\s+on\s+([0-9]{1,2}\s+[A-Za-z]+\s+[0-9]{4})", normalized_text, re.IGNORECASE)
        if msd2:
            facts["start_date"] = msd2.group(1).strip()

    # --------------------------------------------------
    # SALARY / COMPENSATION / RENT
    # --------------------------------------------------
    # Checks for "Monthly Salary I45,000", "Rs. 45,000", "INR 50,000", etc.
    msal = re.search(r"\bMonthly Salary[:\s]+([A-Za-z0-9,.\- ]+?)(?=\s+(?:Work Location|Payable|\n|$))", normalized_text, re.IGNORECASE)
    if msal:
        facts["salary"] = msal.group(1).strip()
    else:
        msal2 = re.search(r"\b(?:salary|compensation)\s+of\s+((?:INR|Rs\.?|USD|₹|\$|EUR)?\s*[0-9,]+(?:\s*(?:per\s+month|monthly|INR|USD))?)", normalized_text, re.IGNORECASE)
        if msal2:
            facts["salary"] = msal2.group(1).strip()

    # Rent
    mr = re.search(r"\b(?:monthly\s+)?rent\s+(?:of\s+)?((?:INR|Rs\.?|USD|₹|\$|EUR)?\s*[0-9,]+(?:\s*(?:per\s+month|/-))?)", normalized_text, re.IGNORECASE)
    if mr:
        facts["rent"] = mr.group(1).strip()

    # Security deposit
    msec = re.search(r"\bsecurity\s+deposit\s+(?:of\s+)?((?:INR|Rs\.?|USD|₹|\$|EUR)?\s*[0-9,]+(?:\s*(?:/-)?)?)", normalized_text, re.IGNORECASE)
    if msec:
        facts["security_deposit"] = msec.group(1).strip()

    # --------------------------------------------------
    # WORK LOCATION / PREMISES
    # --------------------------------------------------
    mwl = re.search(r"\bWork Location[:\s]+([A-Za-z0-9,.\- ]+?)(?=\s+(?:\d+\.|\n|$))", normalized_text, re.IGNORECASE)
    if mwl:
        facts["work_location"] = mwl.group(1).strip()

    # --------------------------------------------------
    # NOTICE PERIOD
    # --------------------------------------------------
    mnp = re.search(r"\b(?:providing|giving)?\s*(\d+)\s*days['’]?\s*(?:written\s+)?notice\b", normalized_text, re.IGNORECASE)
    if mnp:
        facts["notice_period"] = f"{mnp.group(1)} days"
    else:
        mnp2 = re.search(r"\bnotice\s+period\s+(?:of\s+|is\s+)?(\d+)\s*days\b", normalized_text, re.IGNORECASE)
        if mnp2:
            facts["notice_period"] = f"{mnp2.group(1)} days"

    # --------------------------------------------------
    # LEAVE NOTICE
    # --------------------------------------------------
    mln = re.search(r"\bat least\s+(\w+)\s+days\s+before\s+(?:the\s+)?intended\s+leave", normalized_text, re.IGNORECASE)
    if mln:
        facts["leave_notice"] = f"{mln.group(1)} days"

    # --------------------------------------------------
    # GOVERNING LAW
    # --------------------------------------------------
    mgl = re.search(r"\bgoverned\s+by\s+(?:the\s+laws\s+of\s+)?([A-Za-z ]+?)(?=[,.;\n]|$)", normalized_text, re.IGNORECASE)
    if mgl:
        facts["governing_law"] = mgl.group(1).strip()

    return facts