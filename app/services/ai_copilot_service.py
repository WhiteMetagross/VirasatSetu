"""
Virasat AI Copilot Service:
Provides generative and knowledge retrieval capabilities for Indian inheritance law,
statutory nominee rules, banking deceased claims, pensions, small savings, and succession procedures.
"""

import json
import urllib.request
import urllib.error
from typing import Dict, Any, List
from app.config import settings

SYSTEM_INSTRUCTION = (
    "You are Viru, the official AI Legal and Financial Succession Copilot for Virasat Setu, "
    "Indias national deceased asset discovery and inheritance platform. "
    "Your mission is to provide warm, practical, comprehensive, and actionable guidance to citizens, "
    "legal heirs, claimants, and families on all matters of financial succession, asset claims, "
    "statutory entitlements, pensions, banking claims, and legal documentation across India.\n\n"
    "You have deep legal and practical expertise across all asset classes and institutions:\n"
    "1. Banking and Fixed Deposits: Savings accounts, Fixed Deposits, Recurring Deposits, "
    "joint accounts with Either or Survivor or Former or Survivor mandates, Reserve Bank of India UDGAM portal, "
    "deceased claim settlement with or without nomination, indemnity bonds, and surety requirements.\n"
    "2. Retirement Schemes and Pensions: National Pension System, PRAN exit and withdrawal regulations under PFRDA, "
    "lump sum withdrawal and annuity options, Employees Provident Fund, EPS 95 monthly family pensions, "
    "Central Civil Services pension rules, death gratuity, and superannuation benefits.\n"
    "3. Small Savings and Post Office Instruments: Public Provident Fund Scheme, "
    "National Savings Certificates, Kisan Vikas Patra, Post Office Monthly Income Scheme, "
    "Senior Citizen Savings Scheme, Sukanya Samriddhi Yojana, Form 20 deceased claim procedures, "
    "and Department of Posts rules.\n"
    "4. Life Insurance and Annuities: Life Insurance Corporation of India and private life insurers, "
    "death claim settlement forms, early claim investigations, indemnity for lost policy bonds, "
    "and accidental death benefits.\n"
    "5. Capital Markets and Corporate Holdings: Mutual fund folio transmission under AMFI guidelines, "
    "demat and physical equity share transmission under SEBI regulations, and Investor Education and Protection Fund claims.\n"
    "6. Real Estate, Revenue Mutation, and Tangible Assets: Property mutation, Jamabandi, Patta, Khata updates in revenue records, "
    "bank locker operations after demise of holder, and physical gold inheritance.\n"
    "7. Statutory Succession and Court Instruments: Intestate succession under the Hindu Succession Act 1956, "
    "Indian Succession Act 1925, Muslim personal law, Special Marriage Act, registered Wills, codicils, "
    "probate, letters of administration, Revenue Legal Heir Certificates, and Civil Court Succession Certificates.\n\n"
    "Tone and Guidelines:\n"
    "Be conversational, empathetic, practical, and legally precise.\n"
    "Never refuse questions regarding personal finance, pensions, succession planning, taxation of inheritance, "
    "or government small savings schemes.\n"
    "Structure answers with clear numbered steps, document checklists, and practical guidance.\n"
    "Avoid generic robotic refusals."
)

CANDIDATE_GEMINI_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-flash-lite-latest",
    "gemini-3.5-flash",
    "gemini-3.8-flash"
]

OFFLINE_KNOWLEDGE_BASE: List[Dict[str, Any]] = [
    {
        "keywords": ["nps", "national pension system", "pran", "pfrda", "pension wealth", "tier 1", "tier 2"],
        "topic": "National Pension System Deceased Claim and PFRDA Exit Rules:",
        "answer": (
            "Under Pension Fund Regulatory and Development Authority regulations for deceased subscribers: "
            "1. Claim Submission: The registered nominee or legal heir submits the NPS Deceased Withdrawal Form along with the original death certificate, nominee KYC proofs (like Aadhaar and PAN), cancelled bank cheque, and original PRAN card to the registered Nodal Office, Corporate Entity, or Point of Presence service provider. "
            "2. Corpus Settlement Limits: Where the accumulated pension wealth is up to five lakh rupees, one hundred percent of the corpus is disbursed as a tax exempt lump sum to the nominee. Where the accumulated corpus exceeds five lakh rupees, at least eighty percent must be utilized to purchase an Annuity from an empaneled Annuity Service Provider to yield regular monthly family pension, while the remaining twenty percent is paid as a lump sum. "
            "3. Absence of Nominee: If no nomination was registered during subscriber lifetime, legal heirs can claim by submitting a Succession Certificate issued by a competent civil court or a Legal Heir Certificate from revenue authorities. "
            "4. Central Recordkeeping Agency: Claims are verified through Protean or KFintech systems for direct electronic bank credit."
        ),
        "followups": [
            "How to track NPS claim status with Central Recordkeeping Agency?",
            "Is lump sum withdrawal from NPS taxable upon demise of subscriber?",
            "What if the registered nominee has also passed away?"
        ]
    },
    {
        "keywords": ["pension", "eps", "epf", "epfo", "family pension", "gratuity", "superannuation", "jeevan pramaan"],
        "topic": "Central Pension and EPFO Family Pension Claim Procedure:",
        "answer": (
            "For claiming employment pension arrears, death gratuity, and family pensions in India: "
            "1. Employees Provident Fund and EPS 95: Nominees or surviving spouses submit EPFO Form 20 for provident fund settlement, Form 10D for monthly family pension, and Form 5IF for Employees Deposit Linked Insurance scheme assurance up to seven lakh rupees. "
            "2. Central and State Civil Pensions: Under Central Civil Services Pension Rules, the spouse submits Form 14 along with the civil death certificate, joint photograph, and bank details to the Pension Disbursing Authority or treasury branch. "
            "3. Death Gratuity: Service gratuity and retirement gratuity arrears are disbursed to nominees or legal heirs without demanding court probate if valid nomination exists in official service records. "
            "4. Digital Life Verification: Surviving family pensioners must submit the annual Jeevan Pramaan biometric life certificate every November at authorized citizen service centres, post offices, or via face authentication mobile applications."
        ),
        "followups": [
            "What is the maximum benefit payable under EDLI scheme to nominees?",
            "How to register for EPS 95 monthly pension using Form 10D?",
            "Can married daughters claim family pension benefits?"
        ]
    },
    {
        "keywords": ["ppf", "public provident fund", "form 20", "form g", "provident fund account"],
        "topic": "Public Provident Fund Account Deceased Claim Rules:",
        "answer": (
            "Under Public Provident Fund Scheme 2019 rules administered through India Post and designated banks: "
            "1. Account Continuity: A Public Provident Fund account cannot be continued or contributed to by nominees or legal heirs after the demise of the original subscriber. The account must be closed and proceeds paid out. "
            "2. Interest Calculation: Interest continues to accrue at the applicable government Public Provident Fund interest rate until the end of the month preceding the month in which claim settlement is disbursed. "
            "3. Mandatory Documents: The claimant submits Form 20 along with the original death certificate, original PPF passbook, claimant KYC, and cancelled cheque. "
            "4. Settlement Ceiling: Where nomination exists, the nominee receives the entire balance as trustee. In the absence of a registered nominee, claims up to five lakh rupees can be settled on indemnity and affidavit, whereas claims above five lakh rupees mandate a Succession Certificate."
        ),
        "followups": [
            "Does a nominee have to pay income tax on deceased PPF proceeds?",
            "How to settle PPF accounts maintained at post office branches?",
            "What happens to outstanding PPF loans taken by the deceased?"
        ]
    },
    {
        "keywords": ["nsc", "national savings certificate", "post office", "small savings", "kvp", "kisan vikas patra", "pomis", "scss"],
        "topic": "Post Office Small Savings and NSC Claim Procedure:",
        "answer": (
            "For claiming National Savings Certificates, Kisan Vikas Patra, and Post Office Monthly Income Scheme certificates under Department of Posts guidelines: "
            "1. Registered Nominee Claim: The nominee submits Post Office Form 11 along with the original physical certificates or passbook, death certificate, and KYC documents to the home post office branch where the account was opened. "
            "2. Without Nomination: Claims up to five lakh rupees are settled after six months from death by the Postmaster through Form 11 accompanied by an Indemnity Bond, Affidavit, and Letter of Disclaimer from all lawful legal heirs. "
            "3. Court Succession Order: If the unclaimed balance exceeds five lakh rupees and no nomination was recorded, production of a Succession Certificate from a civil court is mandatory. "
            "4. Premature Encashment: National Savings Certificates and Kisan Vikas Patra held in the name of a deceased depositor can be encashed prematurely without interest penalty by the nominee or lawful heir."
        ),
        "followups": [
            "Can NSC certificates be transferred to the name of a legal heir instead of cash payout?",
            "What are the rules for Senior Citizen Savings Scheme closure on death?",
            "How to replace lost original physical NSC certificate bonds?"
        ]
    },
    {
        "keywords": ["fd", "fixed deposit", "term deposit", "recurring deposit", "rd", "either or survivor", "former or survivor", "joint account"],
        "topic": "Fixed Deposit and Joint Account Deceased Claim Settlement:",
        "answer": (
            "Under Reserve Bank of India Master Directions on Deceased Depositors: "
            "1. Joint Account with Either or Survivor Mandate: Upon the demise of one depositor, the surviving joint holder possesses full authority to operate the account, seek premature closure, or receive maturity proceeds simply by submitting the death certificate and KYC. No succession certificate or legal heir consent is required. "
            "2. Sole Account with Registered Nominee: The bank must settle the fixed deposit and interest accrued within fifteen days of receiving the claim form, original death certificate, and nominee KYC verification. "
            "3. No Premature Penalty: Banks cannot levy any premature penalty charges when a term deposit or fixed deposit is closed ahead of its maturity date due to the death of the primary depositor. "
            "4. Claim Without Nominee: Claims up to the bank threshold limit (frequently two to five lakh rupees) are processed under an Indemnity Bond with two solvent guarantors, while larger balances require a Succession Certificate."
        ),
        "followups": [
            "How is interest on deceased fixed deposits calculated up to the date of repayment?",
            "What is the difference between Either or Survivor and Former or Survivor mandates?",
            "How to claim TDS deducted on deceased fixed deposits using Form 15G or 15H?"
        ]
    },
    {
        "keywords": ["locker", "safe deposit", "bank locker", "safe custody", "key", "inventory"],
        "topic": "Bank Locker Operation and Safe Deposit Vault Access After Demise:",
        "answer": (
            "Under Reserve Bank of India guidelines for safe deposit lockers: "
            "1. Locker with Nomination: The bank allows access to the nominee and surviving joint locker holder after verifying the death certificate and claimant identity. An inventory of contents is drawn up in the presence of the nominee, two independent witnesses, and the bank manager. "
            "2. Locker Without Nomination: All legal heirs must jointly apply or grant a Power of Attorney to one representative. The bank opens the locker before an independent advocate or notary and draws a sworn inventory list. "
            "3. Role of Nominee: Access is granted to the nominee strictly as a trustee to take delivery and give valid discharge to the bank. The legal heirs retain beneficial ownership of the assets inside."
        ),
        "followups": [
            "What happens if the locker key is lost by the deceased?",
            "Can a bank break open a locker if heirs do not cooperate?",
            "Are banks liable for stolen items from a deceased persons locker?"
        ]
    },
    {
        "keywords": ["property", "mutation", "patta", "khata", "jamabandi", "land", "real estate", "house"],
        "topic": "Property Mutation and Land Revenue Records Transfer:",
        "answer": (
            "To transfer real estate and revenue land records into the names of legal heirs: "
            "1. Revenue Mutation Application: Submit an application to the local Tehsildar or municipal corporation along with the civil death certificate, registered title deed, and family tree or legal heir certificate. "
            "2. Public Notice and Objections: The revenue authority publishes a proclamation inviting objections within thirty days. If no dispute arises, the mutation order is sanctioned. "
            "3. Updating Khata and Patta: Upon sanction, the revenue records (such as Jamabandi, 7/12 extract, Patta, or Khata certificate) are updated to reflect the legal heirs as lawful owners."
        ),
        "followups": [
            "What is the difference between property registration and property mutation?",
            "How to mutate inherited agricultural land in village records?",
            "Is a registered Will required for urban municipal flat transfer?"
        ]
    },
    {
        "keywords": ["nominee", "legal heir", "rights", "difference", "who gets", "ownership"],
        "topic": "Nominee versus Legal Heir Rights Under Indian Law:",
        "answer": (
            "Under landmark judgments of the Supreme Court of India (including Ram Chander Talwar v. Devinder Kumar Talwar and Shakti Yezdani v. Jayanand Jayant Salgaonkar), a Nominee is merely a statutory trustee or custodian authorized to receive funds from a bank or insurer to give valid discharge to the financial institution. The nominee does not automatically become the absolute beneficial owner of the money. The beneficial ownership vests entirely in the legal heirs according to the applicable succession laws (such as the Hindu Succession Act 1956 or Indian Succession Act 1925), or according to a valid registered Will. If you are a nominee, you hold the proceeds on trust for all lawful legal heirs."
        ),
        "followups": [
            "What if there is no nominee registered on the account?",
            "How do legal heirs claim funds if nominee refuses to distribute?",
            "What documents are needed to prove legal heirship?"
        ]
    },
    {
        "keywords": ["sbi", "bank", "deposit", "savings", "bank account", "udgam"],
        "topic": "Procedure for Claiming Deceased Bank Accounts at SBI and Other Banks:",
        "answer": (
            "For claiming dormant bank deposits and savings accounts across Indian scheduled commercial banks: "
            "1. Where a Nominee is registered: The nominee can submit the Bank Deceased Claim Form along with the original death certificate, nominee identity proof (like Aadhaar or PAN), and account passbook or deposit receipt. Settlement is usually processed within fifteen business days without demanding a succession certificate. "
            "2. Where No Nominee is registered: For balances up to five lakh rupees, banks allow settlement through a simplified procedure with a Letter of Indemnity, No Objection Certificates from all legal heirs, and two third party guarantors. For balances exceeding five lakh rupees, a formal Succession Certificate issued by a competent civil court is typically required."
        ),
        "followups": [
            "How to check dormant accounts on RBI UDGAM portal?",
            "What is an Indemnity Bond with surety?",
            "Can a legal heir claim if the passbook is lost?"
        ]
    },
    {
        "keywords": ["lic", "insurance", "policy", "maturity", "death claim", "endowment"],
        "topic": "Claiming Unclaimed Life Insurance Policies at LIC:",
        "answer": (
            "To settle death claims on matured or active Life Insurance Corporation of India policies: "
            "1. Mandatory Forms: Submit Claim Form A (Intimation of Death) and Claim Form 3783 if the policy was in force. "
            "2. Core Documents: Provide the original policy bond document, original municipal death certificate, claimant photo identity proof, and canceled bank cheque with claimant name printed for direct NEFT payout. "
            "3. Early Death Claims: If death occurred within three years of policy issuance or revival, Form B (Medical Attendant Certificate) and Form C (Employer Certificate if applicable) must be enclosed for verification. "
            "4. Lost Policy Bond: If the original bond is lost, an Indemnity Bond on non judicial stamp paper is executed."
        ),
        "followups": [
            "How to claim if the original policy bond is lost?",
            "What if the nominee passed away before the policyholder?",
            "How long does LIC take to disburse settlement funds?"
        ]
    },
    {
        "keywords": ["mutual fund", "folio", "transmission", "amfi", "equity", "cams", "kfintech", "shares"],
        "topic": "Mutual Fund Folio Transmission Guidelines (AMFI):",
        "answer": (
            "Under Association of Mutual Funds in India guidelines, transferring units of a deceased investor is termed Transmission: "
            "1. Transmission to Nominee: Submit Form T2, attested death certificate, nominee KYC compliance proof, and bank mandate. "
            "2. Transmission to Legal Heirs (No Nominee): Submit Form T3 along with Indemnity Bond Annexure A, NOC from other legal heirs (Annexure B), and for portfolio values exceeding five lakh rupees, a Succession Certificate or Legal Heir Certificate. "
            "3. Joint Holding with Survivor Clause: If units were held with Anyone or Survivor clause, surviving holders submit Form T1 along with death certificate to delete deceased name and continue holding."
        ),
        "followups": [
            "What is Form T2 versus Form T3 in mutual fund transmission?",
            "Do legal heirs have to pay capital gains tax upon transmission?",
            "Can mutual fund units be directly redeemed during transmission?"
        ]
    },
    {
        "keywords": ["succession certificate", "legal heir certificate", "survivorship", "court", "tehsildar"],
        "topic": "Succession Certificate versus Legal Heir Certificate:",
        "answer": (
            "In Indian jurisprudence, there is a distinct difference between these two instruments: "
            "1. Legal Heir Certificate: Issued by the local Revenue Authority (like Tahsildar, Taluk Magistrate, or Revenue Divisional Officer). It establishes the living family tree of the deceased and is accepted for employment succession, pension transfer, and small bank balances. "
            "2. Succession Certificate: Issued exclusively by a Civil District Court under Section 370 of the Indian Succession Act 1925. It grants legal representation over movable debts, shares, and securities of the deceased. Banks and fund houses mandate a Succession Certificate whenever there is an internal family dispute or large unclaimed asset values."
        ),
        "followups": [
            "How much court fee is payable for a succession certificate?",
            "How long does a civil court take to issue a succession certificate?",
            "Is a succession certificate needed if a valid Will exists?"
        ]
    },
    {
        "keywords": ["no certificate", "without certificate", "lost", "missing", "delay", "municipal", "pending"],
        "topic": "Registering and Claiming Without Immediate Death Certificate:",
        "answer": (
            "Virasat Setu permits citizens to register deceased family profiles and explore potential assets even while civil death issuance is pending: "
            "1. Registration of Births and Deaths Act 1969: Deaths must be reported to the local registrar within twenty one days. If delayed, an order from the Executive Magistrate or Sub Divisional Magistrate is required. "
            "2. Prototype Exploration: On Virasat Setu, enter the deceased identity PAN and personal dates to queue matching. "
            "3. Payout Prerequisite: While discovery and matching can proceed, final financial disbursement by banks and insurers strictly requires submission of the official municipal death certificate."
        ),
        "followups": [
            "How to obtain a delayed death certificate from municipal authority?",
            "What is the procedure if death occurred in a hospital?",
            "Can an FIR be used in case of missing persons?"
        ]
    }
]


def query_gemini_api(prompt: str) -> str:
    """Queries Google Gemini API with candidate model failover."""
    if not settings.GEMINI_API_KEY:
        raise ValueError("Gemini API key is not configured.")

    last_error = None
    for model_name in CANDIDATE_GEMINI_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={settings.GEMINI_API_KEY}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{SYSTEM_INSTRUCTION}\n\nUser Question:\n{prompt}"}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 800
            }
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                candidates = res.get("candidates", [])
                if candidates and "content" in candidates[0]:
                    parts = candidates[0]["content"].get("parts", [])
                    if parts and "text" in parts[0]:
                        return parts[0]["text"].strip()
        except urllib.error.HTTPError as err:
            last_error = err
            continue
        except Exception as err:
            last_error = err
            continue

    if last_error:
        raise last_error
    raise ValueError("No text generated by Gemini models.")


def query_offline_knowledge_engine(prompt: str) -> Dict[str, Any]:
    """Matches user query against domain knowledge base."""
    p_lower = prompt.lower()
    best_match = None
    max_score = 0

    for entry in OFFLINE_KNOWLEDGE_BASE:
        score = sum(1 for kw in entry["keywords"] if kw in p_lower)
        if score > max_score:
            max_score = score
            best_match = entry

    if best_match and max_score > 0:
        return {
            "answer": f"{best_match['topic']}\n\n{best_match['answer']}",
            "source": "knowledge_engine",
            "followups": best_match["followups"]
        }

    return {
        "answer": (
            "General Legal Succession Guidance:\n\n"
            "Under Indian inheritance framework, legal heirs can discover and claim dormant assets by following three steps:\n"
            "1. Identification: Cross check civil identity records (like PAN and Aadhaar) against central financial databases.\n"
            "2. Establishing Legal Capacity: Determine whether a valid registered Will exists, or if intestate succession rules apply "
            "under the Hindu Succession Act (for Hindus, Buddhists, Jains, Sikhs) or the Indian Succession Act (for Christians and Parsis).\n"
            "3. Documentation: Obtain the civil death certificate, legal heir certificate or succession certificate, "
            "and indemnity bond before submitting claims to the respective institution desk."
        ),
        "source": "knowledge_engine",
        "followups": [
            "Nominee versus Legal Heir Rights",
            "Procedure for Claiming Deceased Bank Accounts at SBI",
            "National Pension System Deceased Claim Rules",
            "Public Provident Fund Account Deceased Claims",
            "Fixed Deposit and Joint Account Deceased Settlements"
        ]
    }


def generate_contextual_followups(query: str, answer_text: str) -> List[str]:
    """Generates intelligent contextual followups for the citizen."""
    combined = (query + " " + answer_text).lower()
    if "nps" in combined or "pran" in combined or "pfrda" in combined:
        return [
            "How does a nominee claim one hundred percent lump sum in NPS?",
            "What documents are submitted to Nodal Office or CRA?",
            "Difference between NPS Tier 1 and Tier 2 death withdrawal"
        ]
    if "ppf" in combined or "public provident" in combined:
        return [
            "Can a nominee continue the PPF account of the deceased?",
            "How is interest calculated after death in PPF?",
            "Documents required for Form 20 PPF claim"
        ]
    if "nsc" in combined or "post office" in combined or "small savings" in combined or "kvp" in combined:
        return [
            "Procedure for encashing NSC certificates at Post Office",
            "What is the claim limit without a succession certificate in post office?",
            "How to claim Senior Citizen Savings Scheme after death"
        ]
    if "fd" in combined or "fixed deposit" in combined or "term deposit" in combined:
        return [
            "Are there premature penalty charges on FDs after death?",
            "How does Either or Survivor mandate work for joint FDs?",
            "Bank claim process when balance exceeds five lakh rupees"
        ]
    if "pension" in combined or "eps" in combined or "epfo" in combined or "gratuity" in combined:
        return [
            "How to apply for EPS 95 monthly family pension with Form 10D?",
            "How to submit digital Life Certificate via Jeevan Pramaan?",
            "Who is eligible for Central Government Family Pension?"
        ]
    if "locker" in combined:
        return [
            "What happens if the locker key is lost by the deceased?",
            "Can a bank break open a locker if heirs do not cooperate?",
            "How is locker inventory prepared before witnesses?"
        ]
    if "property" in combined or "mutation" in combined or "patta" in combined or "khata" in combined:
        return [
            "What is the difference between property registration and property mutation?",
            "How to mutate inherited agricultural land in village records?",
            "Is a registered Will required for urban municipal flat transfer?"
        ]
    if "nominee" in combined or "heir" in combined:
        return [
            "What if there is no nominee registered on the account?",
            "How do legal heirs claim funds if nominee refuses to distribute?",
            "What documents are needed to prove legal heirship?"
        ]
    return [
        "What documents are needed for this claim?",
        "How long does the institutional review take?",
        "Can an administrator assist with civil verification?"
    ]


def query_groq_api(prompt: str) -> str:
    """Queries Groq Cloud API with OpenAI compatible interface."""
    if not settings.GROQ_API_KEY:
        raise ValueError("Groq API key is not configured.")

    candidate_models = ["openai/gpt-oss-120b", "qwen/qwen3.8-27b", "openai/gpt-oss-20b"]
    url = "https://api.groq.com/openai/v1/chat/completions"

    for model_name in candidate_models:
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": SYSTEM_INSTRUCTION},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 800,
            "temperature": 0.2
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            },
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=6) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                choices = res.get("choices", [])
                if choices and "message" in choices[0]:
                    text = choices[0]["message"].get("content", "").strip()
                    if text:
                        return text
        except Exception:
            continue

    raise ValueError("No text generated by Groq models.")


def get_ai_copilot_response(user_query: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Main entrypoint for Virasat AI Copilot.
    Attempts Gemini Cloud API first; falls back to Groq Cloud API;
    gracefully falls back to intelligent knowledge engine.
    """
    cleaned_query = (user_query or "").strip()
    if not cleaned_query:
        return {
            "answer": "Please enter a question regarding Indian succession laws, nominee rights, pensions, or claim procedures.",
            "source": "system",
            "followups": [
                "Nominee versus Legal Heir Rights",
                "SBI Deceased Account Claim Procedure",
                "National Pension System Deceased Claim Rules",
                "Public Provident Fund Account Deceased Claims"
            ]
        }

    # Tier 1: Attempt Gemini Cloud API first if configured
    try:
        gemini_text = query_gemini_api(cleaned_query)
        if gemini_text:
            return {
                "answer": gemini_text,
                "source": "gemini_api",
                "followups": generate_contextual_followups(cleaned_query, gemini_text)
            }
    except Exception:
        pass

    # Tier 2: Attempt Groq Cloud API as rapid fallback
    try:
        groq_text = query_groq_api(cleaned_query)
        if groq_text:
            return {
                "answer": groq_text,
                "source": "groq_api",
                "followups": generate_contextual_followups(cleaned_query, groq_text)
            }
    except Exception:
        pass

    # Tier 3: Seamless fallback to intelligent domain knowledge engine
    return query_offline_knowledge_engine(cleaned_query)
