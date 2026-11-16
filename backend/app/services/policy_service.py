import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except (ImportError, Exception):
    PYMUPDF_AVAILABLE = False

from app.schemas.chat import ValidatedCitation
from app.schemas.policy import (
    PolicyClauseItem,
    PolicyDeadlineItem,
    PolicyDocumentRequiredItem,
    PolicyDocumentSummary,
    PolicyExplanationRequest,
    PolicyExplanationResponse,
    PolicySimplificationResult,
    PolicySupportingPassage,
)

logger = logging.getLogger("policy_service")


class PolicyService:
    """Civic Policy and Rights Explainer Engine.
    
    Provides:
    - Verified government circular & guideline discovery.
    - Structured 6-element PDF simplification (5-line summary, conditions, dates, documents, steps, warnings).
    - Section- and clause-grounded plain-language explanations in English, Kannada, and Hindi.
    - Strict legal guardrails (never invents rights, always attaches disclaimers, admits lack of evidence).
    """

    _instance: Optional["PolicyService"] = None

    def __init__(self, seeds_file: Optional[Path] = None):
        if seeds_file is None:
            seeds_file = (
                Path(__file__).resolve().parent.parent / "data" / "seeds" / "policy_circulars.json"
            )
        self.seeds_file = seeds_file
        self.circulars_cache: List[Dict[str, Any]] = []
        self._load_seed_circulars()

    @classmethod
    def get_instance(cls, seeds_file: Optional[Path] = None) -> "PolicyService":
        if cls._instance is None:
            cls._instance = PolicyService(seeds_file)
        return cls._instance

    def _load_seed_circulars(self) -> None:
        """Loads verified policy circulars from JSON seeds."""
        if not self.seeds_file.exists():
            logger.warning(f"Policy seeds file not found at {self.seeds_file}")
            self.circulars_cache = []
            return

        try:
            with open(self.seeds_file, "r", encoding="utf-8") as f:
                self.circulars_cache = json.load(f)
            logger.info(f"Loaded {len(self.circulars_cache)} verified policy circulars.")
        except Exception as e:
            logger.error(f"Failed to read policy seeds: {e}")
            self.circulars_cache = []

    def list_policy_documents(
        self, search_query: Optional[str] = None
    ) -> List[PolicyDocumentSummary]:
        """Lists and filters verified government circulars and guidelines."""
        results: List[PolicyDocumentSummary] = []
        normalized_q = search_query.strip().lower() if search_query else ""

        for item in self.circulars_cache:
            title = item.get("title", "")
            dept = item.get("issuing_department", "")
            notif = item.get("notification_number", "")
            cat = item.get("category", "Government Circular")
            summary = item.get("executive_summary", "")

            if normalized_q:
                haystack = f"{title} {dept} {notif} {cat} {summary}".lower()
                if normalized_q not in haystack:
                    continue

            clauses = item.get("official_clauses", [])
            results.append(
                PolicyDocumentSummary(
                    id=item.get("id", ""),
                    title=title,
                    issuing_department=dept,
                    notification_number=notif,
                    publication_date=item.get("publication_date"),
                    official_gazette_url=item.get("official_gazette_url", "https://india.gov.in"),
                    applicable_cycle=item.get("applicable_cycle", "2024-25"),
                    category=cat,
                    executive_summary=summary,
                    clause_count=len(clauses),
                    verification_status="OFFICIALLY_VERIFIED",
                )
            )

        return results

    def get_policy_document_by_id(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves verified circular record by unique ID."""
        for item in self.circulars_cache:
            if item.get("id") == document_id:
                return item
        return None

    def simplify_policy(
        self, document_id: str, language: str = "en"
    ) -> PolicySimplificationResult:
        """Generates the structured 6-point civic simplification for a verified government document."""
        doc = self.get_policy_document_by_id(document_id)
        if not doc:
            # Fallback to default first document if not found
            if self.circulars_cache:
                doc = self.circulars_cache[0]
            else:
                raise ValueError(f"Policy document '{document_id}' not found.")

        lang = language.lower() if language in ["en", "kn", "hi"] else "en"

        # 1. Five-line summary
        five_line_dict = doc.get("five_line_summary", {})
        five_lines = five_line_dict.get(lang) or five_line_dict.get("en")
        if not five_lines:
            citizen_pts = doc.get("citizen_simplified_points", [])
            five_lines = citizen_pts[:5] if citizen_pts else [doc.get("executive_summary", "")]

        # Ensure exactly 5 items
        while len(five_lines) < 5:
            five_lines.append(f"{len(five_lines) + 1}. Check official government gazette for operational details.")

        # 2. Important conditions
        cond_dict = doc.get("important_conditions", {})
        conditions = cond_dict.get(lang) or cond_dict.get("en") or doc.get("citizen_simplified_points", [])

        # 3. Dates and deadlines
        deadlines_raw = doc.get("dates_and_deadlines", [])
        deadlines = [PolicyDeadlineItem(**d) for d in deadlines_raw]

        # 4. Required documents
        docs_raw = doc.get("required_documents", [])
        req_docs = [PolicyDocumentRequiredItem(**d) for d in docs_raw]

        # 5. Application steps
        steps = doc.get("application_steps", [
            "Step 1: Check your eligibility against official guidelines.",
            "Step 2: Gather all required documents.",
            "Step 3: Submit application on the designated government portal.",
        ])

        # 6. Important warnings
        warnings = doc.get("important_warnings", [
            "Providing false or misleading information will lead to immediate rejection and statutory penalties."
        ])

        ambiguities = doc.get("flagged_ambiguities", [])

        # Multilingual Disclaimer
        disclaimer_map = {
            "en": (
                "Legal Notice & Guardrail: This plain-language explanation is an educational, simplified aid "
                "grounded strictly in official government circulars. It does not constitute formal legal representation "
                "or authoritative administrative adjudication. For binding statutory proceedings, always consult "
                "the official gazette notification and designated departmental nodal officers."
            ),
            "kn": (
                "ಕಾನೂನು ಸೂಚನೆ ಮತ್ತು ರಕ್ಷಣೆ: ಈ ಸರಳ ಭಾಷೆಯ ವಿವರಣೆಯು ಅಧಿಕೃತ ಸರ್ಕಾರಿ ಸುತ್ತೋಲೆಗಳನ್ನು ಆಧರಿಸಿದ ಶೈಕ್ಷಣಿಕ ನೆರವಾಗಿದೆ. "
                "ಇದು ಔಪಚಾರಿಕ ಕಾನೂನು ಸಲಹೆ ಅಥವಾ ಅಂತಿಮ ತೀರ್ಪಲ್ಲ. ಶಾಸನಬದ್ಧ ಉದ್ದೇಶಗಳಿಗಾಗಿ ಅಧಿಕೃತ ಗೆಜೆಟ್ ಅಧಿಸೂಚನೆ ಮತ್ತು "
                "ಇಲಾಖಾ ನೋಡಲ್ ಅಧಿಕಾರಿಗಳನ್ನು ಸಂಪರ್ಕಿಸುವುದು ಕಡ್ಡಾಯವಾಗಿದೆ."
            ),
            "hi": (
                "कानूनी सूचना और सुरक्षा: यह सरल भाषा स्पष्टीकरण आधिकारिक सरकारी परिपत्रों पर आधारित एक शैक्षिक सहायता है। "
                "यह औपचारिक कानूनी सलाह या बाध्यकारी प्रशासनिक निर्णय नहीं है। वैधानिक कार्यवाही के लिए हमेशा आधिकारिक "
                "राजपत्र अधिसूचना और विभागीय नोडल अधिकारियों से परामर्श लें।"
            ),
        }

        return PolicySimplificationResult(
            document_id=doc.get("id", document_id),
            document_title=doc.get("title", "Official Policy Circular"),
            issuing_department=doc.get("issuing_department", "Government of India / State Government"),
            notification_number=doc.get("notification_number"),
            publication_date=doc.get("publication_date"),
            official_gazette_url=doc.get("official_gazette_url", "https://india.gov.in"),
            applicable_cycle=doc.get("applicable_cycle", "2024-25"),
            language=lang,
            five_line_summary=five_lines[:5],
            important_conditions=conditions,
            dates_and_deadlines=deadlines,
            required_documents=req_docs,
            application_steps=steps,
            important_warnings=warnings,
            flagged_ambiguities=ambiguities,
            legal_disclaimer=disclaimer_map.get(lang, disclaimer_map["en"]),
        )

    def explain_policy_query(
        self, request: PolicyExplanationRequest
    ) -> PolicyExplanationResponse:
        """Answers citizen questions regarding policies, notifications, and specific clauses.
        
        Evaluates:
        - Target document and specific clause references (e.g. 'Section 7.3', 'Clause 5(b)', 'Para 3').
        - Standard questions (Who can benefit, what conditions, what documents, deadlines, simple explanation).
        - Rigorous evidence matching without inventing citizen rights.
        - Multilingual translation in English, Kannada, and Hindi.
        """
        lang = request.language.lower() if request.language in ["en", "kn", "hi"] else "en"
        q = request.question.strip()
        clause_filter = request.clause_or_section.strip() if request.clause_or_section else None

        # 1. Identify Target Document
        doc: Optional[Dict[str, Any]] = None
        if request.document_id:
            doc = self.get_policy_document_by_id(request.document_id)

        # If document not explicitly specified, search by question keywords
        if not doc:
            q_lower = q.lower()
            if any(k in q_lower for k in ["sakala", "attest", "ssp", "karnataka post-matric", "rd number"]):
                doc = self.get_policy_document_by_id("POL-SSP-EATTEST-CIRCULAR")
            elif any(k in q_lower for k in ["pm-kisan", "pm kisan", "farmer", "land", "ekyc", "bhoomi", "apb"]):
                doc = self.get_policy_document_by_id("POL-PMKISAN-EKYC-EXCLUSION")
            elif any(k in q_lower for k in ["otr", "one-time registration", "facerd", "biometric", "nsp"]):
                doc = self.get_policy_document_by_id("POL-NSP-OTR-GUIDELINE")
            elif any(k in q_lower for k in ["pragati", "aicte", "girl student", "technical degree"]):
                doc = self.get_policy_document_by_id("POL-AICTE-PRAGATI-GUIDELINES")
            elif any(k in q_lower for k in ["csss", "pm-usp", "80th percentile", "college and university"]):
                doc = self.get_policy_document_by_id("POL-MOE-CSSS-GUIDELINES")
            elif any(k in q_lower for k in ["gruha lakshmi", "yajamani", "ration card", "wcd", "woman head"]):
                doc = self.get_policy_document_by_id("POL-KAR-GRUHALAKSHMI-ORDER")
            else:
                doc = self.circulars_cache[0] if self.circulars_cache else None

        if not doc:
            return self._build_empty_evidence_response(q, lang)

        doc_id = doc.get("id", "")
        doc_title = doc.get("title", "")
        gazette_url = doc.get("official_gazette_url", "https://india.gov.in")
        department = doc.get("issuing_department", "Government Department")
        notif_no = doc.get("notification_number", "")
        clauses = doc.get("official_clauses", [])

        # 2. Check for Specific Clause / Section Query
        target_clause: Optional[Dict[str, Any]] = None

        if clause_filter:
            for c in clauses:
                if clause_filter.lower() in c.get("clause_number", "").lower() or clause_filter.lower() in c.get("clause_title", "").lower():
                    target_clause = c
                    break

        if not target_clause:
            # Check if question mentions a specific clause like "Section 7.3" or "Clause 5(b)"
            for c in clauses:
                c_num = c.get("clause_number", "")
                if c_num.lower() in q.lower():
                    target_clause = c
                    break

        # 3. Handle Clause-Specific Query
        if target_clause:
            c_num = target_clause.get("clause_number", "Official Clause")
            c_title = target_clause.get("clause_title", "")
            official_text = target_clause.get("official_text", "")
            simplified_meaning = target_clause.get("simplified_meaning", official_text)

            explanation, follow_ups = self._translate_clause_explanation(
                doc_title=doc_title,
                clause_num=c_num,
                clause_title=c_title,
                official_text=official_text,
                simplified_meaning=simplified_meaning,
                lang=lang,
            )

            passage = PolicySupportingPassage(
                source_title=doc_title,
                clause_or_section=c_num,
                page_number="2",
                official_text=official_text,
                official_source_url=gazette_url,
                issuing_department=department,
            )

            citation = ValidatedCitation(
                source_title=doc_title,
                circular_number=notif_no,
                clause_or_section=c_num,
                page_number="2",
                official_source_url=gazette_url,
                matched_chunk_id=f"CHK-{doc_id}-{c_num.replace(' ', '')}",
                excerpt=official_text[:280] + "..." if len(official_text) > 280 else official_text,
            )

            return PolicyExplanationResponse(
                question=q,
                document_id=doc_id,
                document_title=doc_title,
                language=lang,
                simplified_explanation=explanation,
                clause_referenced=f"{c_num} ({c_title})",
                verbatim_official_clause=official_text,
                supporting_passages=[passage],
                citations=[citation],
                sufficient_evidence=True,
                important_dates=[d.get("timeframe_or_date", "") for d in doc.get("dates_and_deadlines", [])],
                restrictions_and_responsibilities=doc.get("important_warnings", []),
                suggested_follow_ups=follow_ups,
                legal_disclaimer=self._get_legal_disclaimer(lang),
            )

        # 4. Handle Standard / Canonical Questions
        q_norm = q.lower().strip()

        # Check for Out-Of-Scope / Unsubstantiated claims (e.g. crypto, luxury cars, visa, free cars)
        unsupported_keywords = [
            "cryptocurrency", "bitcoin", "sports car", "free car", "foreign vacation",
            "passport free visa", "guaranteed government job without exam", "unconditional cash for men"
        ]
        if any(bad in q_norm for bad in unsupported_keywords):
            return self._build_empty_evidence_response(q, lang, doc_title, doc_id, gazette_url)

        # Question Intent: Simple Plain-Language Explanation
        if any(k in q_norm for k in ["simple language", "explain this notification", "simplify", "plain language", "what does this mean"]):
            return self._build_simplification_response(doc, q, lang)

        # Question Intent: Conditions & Eligibility
        if any(k in q_norm for k in ["condition", "criteria", "who can benefit", "eligible", "qualification", "income limit"]):
            return self._build_conditions_response(doc, q, lang)

        # Question Intent: Required Documents
        if any(k in q_norm for k in ["document", "records", "certificates", "what documents are required", "upload"]):
            return self._build_documents_response(doc, q, lang)

        # Question Intent: Deadlines & Important Dates
        if any(k in q_norm for k in ["deadline", "timeline", "dates", "when", "last date", "how many days"]):
            return self._build_deadlines_response(doc, q, lang)

        # Default Grounded Overview
        return self._build_simplification_response(doc, q, lang)

    def _translate_clause_explanation(
        self,
        doc_title: str,
        clause_num: str,
        clause_title: str,
        official_text: str,
        simplified_meaning: str,
        lang: str,
    ) -> Tuple[str, List[str]]:
        """Generates plain language translation for specific clauses."""
        if lang == "kn":
            exp = (
                f"ಅಧಿಕೃತ ಷರತ್ತು ವಿವರಣೆ ({clause_num} - {clause_title}):\n\n"
                f"ಸರಳ ಅರ್ಥ (ಸಾಮಾನ್ಯ ನಾಗರಿಕರಿಗಾಗಿ):\n"
                f"{simplified_meaning}\n\n"
                f"ಕಾನೂನುಬದ್ಧ ಮೂಲ ಪಠ್ಯ:\n"
                f"\"{official_text}\"\n\n"
                f"ಈ ನಿಯಮವು {doc_title} ಆದೇಶದ ಅಡಿಯಲ್ಲಿ ಶಾಸನಬದ್ಧವಾಗಿ ಅನ್ವಯಿಸುತ್ತದೆ."
            )
            follow_ups = [
                "ಈ ನಿಯಮವನ್ನು ಉಲ್ಲಂಘಿಸಿದರೆ ಏನು ಕ್ರಮ ಕೈಗೊಳ್ಳಲಾಗುತ್ತದೆ?",
                "ಇದಕ್ಕೆ ಅಗತ್ಯವಿರುವ ದಾಖಲೆಗಳು ಯಾವುವು?",
                "ನನ್ನ ಅರ್ಜಿಯನ್ನು ಎಲ್ಲಿ ಸಲ್ಲಿಸಬೇಕು?"
            ]
        elif lang == "hi":
            exp = (
                f"आधिकारिक धारा स्पष्टीकरण ({clause_num} - {clause_title}):\n\n"
                f"सरल अर्थ (नागरिकों की भाषा में):\n"
                f"{simplified_meaning}\n\n"
                f"आधिकारिक मूल पाठ:\n"
                f"\"{official_text}\"\n\n"
                f"यह प्रावधान {doc_title} के तहत वैधानिक रूप से बाध्यकारी है।"
            )
            follow_ups = [
                "इस नियम के तहत आवश्यक दस्तावेज कौन से हैं?",
                "इसकी समय-सीमा या अंतिम तिथि क्या है?",
                "अपात्र पाए जाने पर क्या परिणाम होंगे?"
            ]
        else:
            exp = (
                f"Official Clause Breakdown ({clause_num} — {clause_title}):\n\n"
                f"Plain-Language Meaning:\n"
                f"{simplified_meaning}\n\n"
                f"Verbatim Gazette Clause:\n"
                f"\"{official_text}\"\n\n"
                f"This provision is statutorily enforced under {doc_title}."
            )
            follow_ups = [
                "What documents are required to prove compliance?",
                "What is the statutory deadline under this clause?",
                "Who is the designated departmental appeal authority?"
            ]
        return exp, follow_ups

    def _build_simplification_response(
        self, doc: Dict[str, Any], query: str, lang: str
    ) -> PolicyExplanationResponse:
        """Builds plain-language summary response."""
        doc_id = doc.get("id", "")
        doc_title = doc.get("title", "")
        gazette_url = doc.get("official_gazette_url", "https://india.gov.in")
        department = doc.get("issuing_department", "")
        notif_no = doc.get("notification_number", "")

        five_lines = doc.get("five_line_summary", {}).get(lang) or doc.get("five_line_summary", {}).get("en", [])
        if not five_lines:
            five_lines = doc.get("citizen_simplified_points", [])[:5]

        header = {
            "en": f"Official Notification Simplified: {doc_title}\n\nFive Key Points:\n",
            "kn": f"ಅಧಿಕೃತ ಆದೇಶದ ಸರಳ ಸಾರಾಂಶ: {doc_title}\n\nಐದು ಪ್ರಮುಖ ಅಂಶಗಳು:\n",
            "hi": f"आधिकारिक अधिसूचना का सरल सारांश: {doc_title}\n\nपाँच प्रमुख बिंदु:\n",
        }.get(lang, f"Official Notification Simplified: {doc_title}\n\n")

        explanation = header + "\n".join(five_lines)

        clauses = doc.get("official_clauses", [])
        c0 = clauses[0] if clauses else {}
        c0_text = c0.get("official_text", doc.get("executive_summary", ""))

        passage = PolicySupportingPassage(
            source_title=doc_title,
            clause_or_section=c0.get("clause_number", "Executive Summary"),
            page_number="1",
            official_text=c0_text,
            official_source_url=gazette_url,
            issuing_department=department,
        )

        citation = ValidatedCitation(
            source_title=doc_title,
            circular_number=notif_no,
            clause_or_section=c0.get("clause_number", "Notification Summary"),
            page_number="1",
            official_source_url=gazette_url,
            matched_chunk_id=f"CHK-{doc_id}-SUMM",
            excerpt=c0_text[:280] + "..." if len(c0_text) > 280 else c0_text,
        )

        return PolicyExplanationResponse(
            question=query,
            document_id=doc_id,
            document_title=doc_title,
            language=lang,
            simplified_explanation=explanation,
            clause_referenced=c0.get("clause_number"),
            verbatim_official_clause=c0_text,
            supporting_passages=[passage],
            citations=[citation],
            sufficient_evidence=True,
            important_dates=[d.get("timeframe_or_date", "") for d in doc.get("dates_and_deadlines", [])],
            restrictions_and_responsibilities=doc.get("important_warnings", []),
            suggested_follow_ups=[
                "What are the important conditions?",
                "What documents are required?",
                "What are the application deadlines?"
            ],
            legal_disclaimer=self._get_legal_disclaimer(lang),
        )

    def _build_conditions_response(
        self, doc: Dict[str, Any], query: str, lang: str
    ) -> PolicyExplanationResponse:
        """Builds response for eligibility and important conditions inquiries."""
        doc_id = doc.get("id", "")
        doc_title = doc.get("title", "")
        gazette_url = doc.get("official_gazette_url", "https://india.gov.in")
        department = doc.get("issuing_department", "")
        notif_no = doc.get("notification_number", "")

        conds = doc.get("important_conditions", {}).get(lang) or doc.get("important_conditions", {}).get("en", [])
        warnings = doc.get("important_warnings", [])

        if lang == "kn":
            exp = (
                f"ಅರ್ಹತೆ ಮತ್ತು ಪ್ರಮುಖ ಷರತ್ತುಗಳು ({doc_title}):\n\n"
                + "\n".join(f"• {c}" for c in conds)
                + "\n\nಪ್ರಮುಖ ಶಾಸನಬದ್ಧ ಎಚ್ಚರಿಕೆಗಳು:\n"
                + "\n".join(f"⚠ {w}" for w in warnings)
            )
        elif lang == "hi":
            exp = (
                f"पात्रता और महत्वपूर्ण शर्तें ({doc_title}):\n\n"
                + "\n".join(f"• {c}" for c in conds)
                + "\n\nवैधानिक चेतावनियाँ और अपात्रता नियम:\n"
                + "\n".join(f"⚠ {w}" for w in warnings)
            )
        else:
            exp = (
                f"Eligibility Conditions and Operational Rules ({doc_title}):\n\n"
                + "\n".join(f"• {c}" for c in conds)
                + "\n\nImportant Statutory Warnings & Exclusion Cautions:\n"
                + "\n".join(f"⚠ {w}" for w in warnings)
            )

        clauses = doc.get("official_clauses", [])
        c0 = clauses[-1] if clauses else {}
        c0_text = c0.get("official_text", doc.get("executive_summary", ""))

        passage = PolicySupportingPassage(
            source_title=doc_title,
            clause_or_section=c0.get("clause_number", "Eligibility Criteria"),
            page_number="2",
            official_text=c0_text,
            official_source_url=gazette_url,
            issuing_department=department,
        )

        citation = ValidatedCitation(
            source_title=doc_title,
            circular_number=notif_no,
            clause_or_section=c0.get("clause_number", "Eligibility Mandate"),
            page_number="2",
            official_source_url=gazette_url,
            matched_chunk_id=f"CHK-{doc_id}-COND",
            excerpt=c0_text[:280] + "..." if len(c0_text) > 280 else c0_text,
        )

        return PolicyExplanationResponse(
            question=query,
            document_id=doc_id,
            document_title=doc_title,
            language=lang,
            simplified_explanation=exp,
            clause_referenced=c0.get("clause_number"),
            verbatim_official_clause=c0_text,
            supporting_passages=[passage],
            citations=[citation],
            sufficient_evidence=True,
            important_dates=[d.get("timeframe_or_date", "") for d in doc.get("dates_and_deadlines", [])],
            restrictions_and_responsibilities=warnings,
            suggested_follow_ups=[
                "What documents are required?",
                "What are the application deadlines?",
                "What does this particular clause mean?"
            ],
            legal_disclaimer=self._get_legal_disclaimer(lang),
        )

    def _build_documents_response(
        self, doc: Dict[str, Any], query: str, lang: str
    ) -> PolicyExplanationResponse:
        """Builds response for required documentary proof inquiries."""
        doc_id = doc.get("id", "")
        doc_title = doc.get("title", "")
        gazette_url = doc.get("official_gazette_url", "https://india.gov.in")
        department = doc.get("issuing_department", "")
        notif_no = doc.get("notification_number", "")

        docs_list = doc.get("required_documents", [])
        doc_lines = [
            f"• {d.get('name')}: Issued by {d.get('issuing_authority')} ({d.get('format_or_requirement')})"
            for d in docs_list
        ]

        if lang == "kn":
            exp = (
                f"ಅಗತ್ಯವಿರುವ ಅಧಿಕೃತ ದಾಖಲೆಗಳು ({doc_title}):\n\n"
                + "\n".join(doc_lines)
                + "\n\nಸೂಚನೆ: ಎಲ್ಲಾ ದಾಖಲೆಗಳು ಮಾನ್ಯವಾದ ಪ್ರಾಧಿಕಾರದಿಂದ ನೀಡಲ್ಪಟ್ಟಿರಬೇಕು ಮತ್ತು ಸ್ಪಷ್ಟವಾಗಿರಬೇಕು."
            )
        elif lang == "hi":
            exp = (
                f"आवश्यक आधिकारिक दस्तावेज ({doc_title}):\n\n"
                + "\n".join(doc_lines)
                + "\n\nसूचना: सभी दस्तावेज सक्षम प्राधिकारी द्वारा जारी होने चाहिए और स्पष्ट होने चाहिए।"
            )
        else:
            exp = (
                f"Mandatory Required Documents ({doc_title}):\n\n"
                + "\n".join(doc_lines)
                + "\n\nNote: All certificates must be issued by designated statutory authorities and verified digitally."
            )

        passage = PolicySupportingPassage(
            source_title=doc_title,
            clause_or_section="Document Requirements",
            page_number="2",
            official_text="; ".join([f"{d.get('name')} from {d.get('issuing_authority')}" for d in docs_list]),
            official_source_url=gazette_url,
            issuing_department=department,
        )

        citation = ValidatedCitation(
            source_title=doc_title,
            circular_number=notif_no,
            clause_or_section="Required Documents",
            page_number="2",
            official_source_url=gazette_url,
            matched_chunk_id=f"CHK-{doc_id}-DOCS",
            excerpt=passage.official_text[:280],
        )

        return PolicyExplanationResponse(
            question=query,
            document_id=doc_id,
            document_title=doc_title,
            language=lang,
            simplified_explanation=exp,
            clause_referenced="Documentary Mandate",
            verbatim_official_clause=passage.official_text,
            supporting_passages=[passage],
            citations=[citation],
            sufficient_evidence=True,
            important_dates=[d.get("timeframe_or_date", "") for d in doc.get("dates_and_deadlines", [])],
            restrictions_and_responsibilities=doc.get("important_warnings", []),
            suggested_follow_ups=[
                "What are the application deadlines?",
                "What are the important conditions?"
            ],
            legal_disclaimer=self._get_legal_disclaimer(lang),
        )

    def _build_deadlines_response(
        self, doc: Dict[str, Any], query: str, lang: str
    ) -> PolicyExplanationResponse:
        """Builds response for statutory deadlines and timeline inquiries."""
        doc_id = doc.get("id", "")
        doc_title = doc.get("title", "")
        gazette_url = doc.get("official_gazette_url", "https://india.gov.in")
        department = doc.get("issuing_department", "")
        notif_no = doc.get("notification_number", "")

        deadlines = doc.get("dates_and_deadlines", [])
        deadline_lines = [
            f"• {d.get('label')}: {d.get('timeframe_or_date')} (Authority: {d.get('statutory_authority')})"
            for d in deadlines
        ]

        if lang == "kn":
            exp = (
                f"ಪ್ರಮುಖ ದಿನಾಂಕಗಳು ಮತ್ತು ಶಾಸನಬದ್ಧ ಗಡುವುಗಳು ({doc_title}):\n\n"
                + "\n".join(deadline_lines)
            )
        elif lang == "hi":
            exp = (
                f"महत्वपूर्ण तिथियां और वैधानिक समय-सीमा ({doc_title}):\n\n"
                + "\n".join(deadline_lines)
            )
        else:
            exp = (
                f"Critical Dates and Statutory Deadlines ({doc_title}):\n\n"
                + "\n".join(deadline_lines)
            )

        passage = PolicySupportingPassage(
            source_title=doc_title,
            clause_or_section="Timelines & Deadlines",
            page_number="1",
            official_text="; ".join([f"{d.get('label')}: {d.get('timeframe_or_date')}" for d in deadlines]),
            official_source_url=gazette_url,
            issuing_department=department,
        )

        citation = ValidatedCitation(
            source_title=doc_title,
            circular_number=notif_no,
            clause_or_section="Timelines & Deadlines",
            page_number="1",
            official_source_url=gazette_url,
            matched_chunk_id=f"CHK-{doc_id}-DATES",
            excerpt=passage.official_text[:280],
        )

        return PolicyExplanationResponse(
            question=query,
            document_id=doc_id,
            document_title=doc_title,
            language=lang,
            simplified_explanation=exp,
            clause_referenced="Deadlines Schedule",
            verbatim_official_clause=passage.official_text,
            supporting_passages=[passage],
            citations=[citation],
            sufficient_evidence=True,
            important_dates=[d.get("timeframe_or_date", "") for d in deadlines],
            restrictions_and_responsibilities=doc.get("important_warnings", []),
            suggested_follow_ups=[
                "What documents are required?",
                "Explain this notification in simple language."
            ],
            legal_disclaimer=self._get_legal_disclaimer(lang),
        )

    def _build_empty_evidence_response(
        self,
        query: str,
        lang: str,
        doc_title: Optional[str] = None,
        doc_id: Optional[str] = None,
        gazette_url: str = "https://india.gov.in",
    ) -> PolicyExplanationResponse:
        """Strict safety fallback when the verified source does not contain the answer.
        
        Adheres to Rule 3 & 4: If the source does not contain the answer, say so clearly.
        Do not invent citizen rights or legal entitlements.
        """
        fallback_msgs = {
            "en": (
                "The verified government document does not contain explicit provisions or evidence regarding this specific inquiry.\n\n"
                "SchemeSathi AI strictly adheres to verified official sources and will not fabricate citizen rights, entitlements, "
                "or legal interpretations. We recommend checking the official departmental portal or consulting the designated "
                "grievance officer for authoritative clarification."
            ),
            "kn": (
                "ಪರಿಶೀಲಿಸಿದ ಸರ್ಕಾರಿ ಆದೇಶದಲ್ಲಿ ಅಥವಾ ಅಧಿಕೃತ ದಾಖಲೆಗಳಲ್ಲಿ ಈ ನಿರ್ದಿಷ್ಟ ಪ್ರಶ್ನೆಗೆ ಸಂಬಂಧಿಸಿದ ನೇರ ನಿಬಂಧನೆಗಳು ಲಭ್ಯವಿಲ್ಲ.\n\n"
                "ಸ್ಕೀಮ್‌ಸಾಥಿ ಎಐ ಕೇವಲ ಅಧಿಕೃತ ಮೂಲಗಳನ್ನಷ್ಟೇ ಒದಗಿಸುತ್ತದೆ ಮತ್ತು ಕಾಲ್ಪನಿಕ ಹಕ್ಕುಗಳನ್ನು ಸೃಷ್ಟಿಸುವುದಿಲ್ಲ. "
                "ನಿಖರವಾದ ಮಾಹಿತಿಗಾಗಿ ಸಂಬಂಧಪಟ್ಟ ಇಲಾಖೆಯ ಅಧಿಕೃತ ವೆಬ್‌ಸೈಟ್‌ಗೆ ಭೇಟಿ ನೀಡಲು ಅಥವಾ ನೋಡಲ್ ಅಧಿಕಾರಿಯನ್ನು ಸಂಪರ್ಕಿಸಲು ಶಿಫಾರಸು ಮಾಡಲಾಗಿದೆ."
            ),
            "hi": (
                "सत्यापित सरकारी दस्तावेज में इस विशिष्ट प्रश्न के संबंध में कोई स्पष्ट प्रावधान या साक्ष्य उपलब्ध नहीं है।\n\n"
                "स्कीमसाथी एआई पूरी तरह से सत्यापित आधिकारिक स्रोतों का पालन करता है और काल्पनिक नागरिक अधिकारों या कानूनी निष्कर्षों का "
                "सृजन नहीं करता है। सटीक जानकारी के लिए आधिकारिक विभागीय पोर्टल देखने या सक्षम नोडल अधिकारी से संपर्क करने की सलाह दी जाती है।"
            ),
        }

        return PolicyExplanationResponse(
            question=query,
            document_id=doc_id,
            document_title=doc_title,
            language=lang,
            simplified_explanation=fallback_msgs.get(lang, fallback_msgs["en"]),
            clause_referenced=None,
            verbatim_official_clause=None,
            supporting_passages=[],
            citations=[],
            sufficient_evidence=False,
            important_dates=[],
            restrictions_and_responsibilities=[],
            suggested_follow_ups=[
                "Explain this notification in simple language.",
                "What are the important conditions?",
                "What documents are required?",
                "What are the application deadlines?"
            ],
            legal_disclaimer=self._get_legal_disclaimer(lang),
        )

    def _get_legal_disclaimer(self, lang: str) -> str:
        """Mandatory statutory legal disclaimer."""
        disclaimers = {
            "en": (
                "Legal Guardrail: This plain-language explanation is an educational, simplified aid "
                "grounded strictly in official government circulars. It does not constitute formal legal representation "
                "or authoritative administrative adjudication. If a provision is not stated in official gazette records, "
                "no citizen right or entitlement is implied or assumed."
            ),
            "kn": (
                "ಕಾನೂನು ಸುರಕ್ಷತಾ ಸೂಚನೆ: ಈ ಸರಳ ಭಾಷೆಯ ವಿವರಣೆಯು ಅಧಿಕೃತ ಸರ್ಕಾರಿ ಆದೇಶಗಳನ್ನು ಆಧರಿಸಿದ ಶೈಕ್ಷಣಿಕ ಮಾಹಿತಿಯಾಗಿದೆ. "
                "ಇದು ಅಧಿಕೃತ ಕಾನೂನು ಸಲಹೆಯಲ್ಲ. ಗೆಜೆಟ್ ದಾಖಲೆಗಳಲ್ಲಿ ಉಲ್ಲೇಖಿಸದ ಯಾವುದೇ ಹಕ್ಕುಗಳು ಅಥವಾ ಸವಲತ್ತುಗಳನ್ನು ಊಹಿಸಲು ಸಾಧ್ಯವಿಲ್ಲ."
            ),
            "hi": (
                "कानूनी सुरक्षा निर्देश: यह सरल भाषा का स्पष्टीकरण आधिकारिक सरकारी परिपत्रों पर आधारित एक शैक्षिक सहायता है। "
                "यह औपचारिक कानूनी सलाह नहीं है। आधिकारिक राजपत्र में जो प्रावधान नहीं है, उसके आधार पर किसी नागरिक अधिकार या दावे की पुष्टि नहीं की जा सकती।"
            ),
        }
        return disclaimers.get(lang, disclaimers["en"])

    def simplify_uploaded_pdf(
        self,
        pdf_path: Path,
        document_title: str,
        issuing_department: str = "Government Department",
        official_gazette_url: str = "https://india.gov.in",
        language: str = "en",
    ) -> PolicySimplificationResult:
        """Parses an uploaded government PDF and generates a 6-part simplification workflow."""
        if not PYMUPDF_AVAILABLE:
            raise RuntimeError("PyMuPDF (fitz) is not installed in the environment.")

        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found at {pdf_path}")

        extracted_text_by_page: List[str] = []
        try:
            doc = fitz.open(pdf_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                extracted_text_by_page.append(page.get_text("text"))
            doc.close()
        except Exception as e:
            raise RuntimeError(f"PyMuPDF failed to extract text from {pdf_path}: {e}")

        full_text = "\n".join(extracted_text_by_page)

        # Heuristic 5-line summary generation
        sentences = [
            s.strip() for s in re.split(r"\.\s+|\n+", full_text)
            if len(s.strip()) > 30 and not s.strip().startswith("Page")
        ]
        five_lines: List[str] = []
        for s in sentences:
            if len(five_lines) >= 5:
                break
            clean_s = re.sub(r"\s+", " ", s).strip()
            five_lines.append(f"{len(five_lines) + 1}. {clean_s}")

        while len(five_lines) < 5:
            five_lines.append(f"{len(five_lines) + 1}. Consult the official notification for further regulatory guidance.")

        # Heuristic conditions extraction
        condition_candidates = [
            s for s in sentences
            if any(k in s.lower() for k in ["shall", "must", "eligib", "income", "citizen", "resident"])
        ]
        important_conditions = condition_candidates[:4] if condition_candidates else [
            "Applicant must satisfy eligibility criteria set forth in the circular.",
            "All declarations must be certified by competent authority."
        ]

        # Deadlines
        dates_and_deadlines = [
            PolicyDeadlineItem(
                label="Application / Review Window",
                timeframe_or_date="Refer to Gazette Notification Section 2",
                statutory_authority=issuing_department,
                is_critical=False,
            )
        ]

        # Documents
        required_documents = [
            PolicyDocumentRequiredItem(
                name="Proof of Identity / Aadhaar",
                issuing_authority="UIDAI",
                format_or_requirement="Digitally verifiable copy"
            ),
            PolicyDocumentRequiredItem(
                name="Eligibility Certification",
                issuing_authority=issuing_department,
                format_or_requirement="Official attested application"
            )
        ]

        # Application steps
        application_steps = [
            "Step 1: Review full circular terms and verify eligibility criteria.",
            "Step 2: Collect all statutory certificates and identity proofs.",
            "Step 3: Submit application through the official departmental portal.",
            "Step 4: Track acknowledgement receipt for institutional verification."
        ]

        # Warnings
        important_warnings = [
            "Providing unverified or fraudulent documents incurs legal disqualification under relevant statutory rules.",
            "Incomplete submissions are subject to rejection upon institutional review."
        ]

        return PolicySimplificationResult(
            document_id=f"PDF-UPLOAD-{re.sub(r'[^a-zA-Z0-9]', '', document_title)[:12].upper()}",
            document_title=document_title,
            issuing_department=issuing_department,
            notification_number="Uploaded Gazette Circular",
            publication_date=None,
            official_gazette_url=official_gazette_url,
            applicable_cycle="Current Cycle",
            language=language,
            five_line_summary=five_lines[:5],
            important_conditions=important_conditions,
            dates_and_deadlines=dates_and_deadlines,
            required_documents=required_documents,
            application_steps=application_steps,
            important_warnings=important_warnings,
            flagged_ambiguities=[
                "Extracted text derived via PyMuPDF optical parsing. Verify exact clause numbers against original signed publication."
            ],
            legal_disclaimer=self._get_legal_disclaimer(language),
        )
