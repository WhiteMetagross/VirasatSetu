"""
Virasat AI Copilot Service:
Provides generative and knowledge retrieval capabilities for Indian inheritance law,
statutory nominee rules, banking deceased claims, and succession procedures.
"""

import json
import urllib.request
import urllib.error
from typing import Dict, Any, List
from app.config import settings

SYSTEM_INSTRUCTION = (
    "You are Virasat AI Copilot, the official digital inheritance and legal succession advisor "
    "for the Indian platform Virasat Setu. You assist citizens and legal heirs navigating Indian succession law, "
    "including the Hindu Succession Act, Indian Succession Act, statutory nominee rights versus legal heir rights, "
    "Reserve Bank of India UDGAM portal guidelines, State Bank of India deceased depositor claims, "
    "LIC death claim settlements, and mutual fund transmission. Always be respectful, legally precise, and helpful. "
    "Structure your response with clear actionable bullet points or short paragraphs. Avoid hype and disclaimers."
)

OFFLINE_KNOWLEDGE_BASE: List[Dict[str, Any]] = [
    {
        "keywords": ["nominee", "legal heir", "rights", "difference", "who gets", "ownership"],
        "topic": "Nominee versus Legal Heir Rights Under Indian Law:",
        "answer": (
            "Under landmark judgments of the Supreme Court of India (including Ram Chander Talwar v. Devinder Kumar Talwar "
            "and Shakti Yezdani v. Jayanand Jayant Salgaonkar), a Nominee is merely a statutory trustee or custodian "
            "authorized to receive funds from a bank or insurer to give valid discharge to the financial institution. "
            "The nominee does not automatically become the absolute beneficial owner of the money. "
            "The beneficial ownership vests entirely in the legal heirs according to the applicable succession laws "
            "(such as the Hindu Succession Act 1956 or Indian Succession Act 1925), or according to a valid registered Will. "
            "If you are a nominee, you hold the proceeds on trust for all lawful legal heirs."
        ),
        "followups": [
            "What if there is no nominee registered on the account?",
            "How do legal heirs claim funds if nominee refuses to distribute?",
            "What documents are needed to prove legal heirship?"
        ]
    },
    {
        "keywords": ["sbi", "bank", "deposit", "savings", "fixed deposit", "bank account", "udgam"],
        "topic": "Procedure for Claiming Deceased Bank Accounts at SBI and Other Banks:",
        "answer": (
            "For claiming dormant bank deposits and savings accounts across Indian scheduled commercial banks: "
            "1. Where a Nominee is registered: The nominee can submit the Bank Deceased Claim Form along with the original "
            "death certificate, nominee identity proof (like Aadhaar or PAN), and account passbook or deposit receipt. "
            "Settlement is usually processed within fifteen business days without demanding a succession certificate. "
            "2. Where No Nominee is registered: For balances up to five lakh rupees, banks allow settlement through a simplified "
            "procedure with a Letter of Indemnity, No Objection Certificates (NOC) from all legal heirs, and two third party guarantors. "
            "For balances exceeding five lakh rupees, a formal Succession Certificate issued by a competent civil court is typically required."
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
            "2. Core Documents: Provide the original policy bond document, original municipal death certificate, "
            "claimant photo identity proof, and canceled bank cheque with claimant name printed for direct NEFT payout. "
            "3. Early Death Claims: If death occurred within three years of policy issuance or revival, Form B (Medical Attendant Certificate) "
            "and Form C (Employer Certificate if applicable) must be enclosed for verification. "
            "4. Lost Policy Bond: If the original bond is lost, an Indemnity Bond on non judicial stamp paper is executed."
        ),
        "followups": [
            "How to claim if the original policy bond is lost?",
            "What if the nominee passed away before the policyholder?",
            "How long does LIC take to disburse settlement funds?"
        ]
    },
    {
        "keywords": ["mutual fund", "folio", "transmission", "amfi", "equity", "cams", "kfintech"],
        "topic": "Mutual Fund Folio Transmission Guidelines (AMFI):",
        "answer": (
            "Under Association of Mutual Funds in India (AMFI) guidelines, transferring units of a deceased investor is termed Transmission: "
            "1. Transmission to Nominee: Submit Form T2, attested death certificate, nominee KYC compliance proof, and bank mandate. "
            "2. Transmission to Legal Heirs (No Nominee): Submit Form T3 along with Indemnity Bond Annexure A, NOC from other legal heirs (Annexure B), "
            "and for portfolio values exceeding five lakh rupees, a Succession Certificate or Legal Heir Certificate. "
            "3. Joint Holding with Survivor Clause: If units were held with Anyone or Survivor clause, surviving holders submit Form T1 "
            "along with death certificate to delete deceased name and continue holding."
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
            "1. Legal Heir Certificate: Issued by the local Revenue Authority (like Tahsildar, Taluk Magistrate, or Revenue Divisional Officer). "
            "It establishes the living family tree of the deceased and is accepted for employment succession, pension transfer, and small bank balances. "
            "2. Succession Certificate: Issued exclusively by a Civil District Court under Section 370 of the Indian Succession Act 1925. "
            "It grants legal representation over movable debts, shares, and securities of the deceased. "
            "Banks and fund houses mandate a Succession Certificate whenever there is an internal family dispute or large unclaimed asset values."
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
            "1. Registration of Births and Deaths Act 1969: Deaths must be reported to the local registrar within twenty one days. "
            "If delayed, an order from the Executive Magistrate or Sub Divisional Magistrate is required. "
            "2. Prototype Exploration: On Virasat Setu, enter the deceased identity PAN and personal dates to queue matching. "
            "3. Payout Prerequisite: While discovery and matching can proceed, final financial disbursement by banks and insurers "
            "strictly requires submission of the official municipal death certificate."
        ),
        "followups": [
            "How to obtain a delayed death certificate from municipal authority?",
            "What is the procedure if death occurred in a hospital?",
            "Can an FIR be used in case of missing persons?"
        ]
    }
]


def query_gemini_api(prompt: str) -> str:
    """Queries Google Gemini API with fallback."""
    if not settings.GEMINI_API_KEY:
        raise ValueError("Gemini API key is not configured.")

    model_name = "gemini-3.8-flash"
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
            "maxOutputTokens": 600
        }
    }
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    # Use short 2 second timeout to prevent any serverless latency
    with urllib.request.urlopen(req, timeout=2) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        candidates = res.get("candidates", [])
        if candidates and "content" in candidates[0]:
            parts = candidates[0]["content"].get("parts", [])
            if parts and "text" in parts[0]:
                return parts[0]["text"].strip()
    
    raise ValueError("No text generated by Gemini model.")


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

    # Default general guidance
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
            "Claiming Unclaimed Life Insurance Policies at LIC",
            "Mutual Fund Folio Transmission Guidelines"
        ]
    }


def get_ai_copilot_response(user_query: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Main entrypoint for Virasat AI Copilot.
    Attempts Gemini Cloud API first; gracefully falls back to intelligent knowledge engine.
    """
    cleaned_query = (user_query or "").strip()
    if not cleaned_query:
        return {
            "answer": "Please enter a question regarding Indian succession laws, nominee rights, or claim procedures.",
            "source": "system",
            "followups": [
                "Nominee versus Legal Heir Rights",
                "SBI Deceased Account Claim Procedure",
                "LIC Policy Claim Steps"
            ]
        }

    # Attempt Gemini API first if configured
    try:
        gemini_text = query_gemini_api(cleaned_query)
        if gemini_text:
            return {
                "answer": gemini_text,
                "source": "gemini_api",
                "followups": [
                    "What documents are needed for this claim?",
                    "How long does the institutional review take?",
                    "Can an administrator assist with civil verification?"
                ]
            }
    except Exception as err:
        # Graceful fallback without failing user request
        pass

    # Seamless fallback to intelligent knowledge engine
    return query_offline_knowledge_engine(cleaned_query)
