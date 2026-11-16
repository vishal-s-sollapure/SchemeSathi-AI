import logging
import re
from typing import Any, Dict, List, Optional, Tuple

from app.services.document_intelligence.models import (
    ExtractedFieldCandidate,
    ProcessedDocumentResult,
)

logger = logging.getLogger("document_extractor")


class DocumentIntelligenceExtractor:
    """Extracts candidate facts from government circulars, certificates, and student marks cards.
    
    Guarantees:
    - Zero false claims of document authenticity.
    - Gracefully handles partial or missing fields.
    - Records confidence scores, raw text evidence snippets, and source page numbers.
    """

    DISCLAIMER = (
        "Extracted for data entry assistance only; text extraction does not verify document authenticity. "
        "Official validation requires departmental database cross-matching via RD number or e-KYC."
    )

    # Document type detection patterns
    DOC_TYPE_PATTERNS = [
        (r"(?:annual\s+)?income\s+certificate|ಆದಾಯ\s+ಪ್ರಮಾಣ\s+ಪತ್ರ|आय\s+प्रमाण\s+पत्र", "INCOME_CERTIFICATE"),
        (r"caste\s+certificate|community\s+certificate|scheduled\s+caste|ಜಾತಿ\s+ಪ್ರಮಾಣ\s+ಪತ್ರ|जाति\s+प्रमाण\s+पत्र", "CASTE_CERTIFICATE"),
        (r"marks\s+card|statement\s+of\s+marks|grade\s+sheet|marksheet|ಅಂಕಪಟ್ಟಿ|अंकतालिका|class\s+xii|higher\s+secondary", "MARKS_CARD"),
        (r"bonafide\s+certificate|study\s+certificate|enrollment\s+certificate|ಅಧ್ಯಯನ\s+ಪ್ರಮಾಣ\s+ಪತ್ರ", "BONAFIDE_CERTIFICATE"),
        (r"domicile\s+certificate|residence\s+certificate|ವಾಸಸ್ಥಳ\s+ಪ್ರಮಾಣ\s+ಪತ್ರ|मूल\s+निवास", "DOMICILE_CERTIFICATE"),
        (r"ration\s+card|antyodaya|bpl\s+card|ahara|ಪಡಿತರ\s+ಚೀಟಿ|राशन\s+कार्ड", "RATION_CARD"),
        (r"record\s+of\s+rights|rtc|pahani|bhoomi|farmland|revenue\s+khat|ಭೂಮಿ\s+ಪಹಣಿ|खतौनी", "LAND_RECORD_ROR"),
        (r"bank\s+passbook|npci|aadhaar\s+payment\s+bridge|dbt\s+bank", "AADHAAR_DBT_PASSBOOK"),
    ]

    @classmethod
    def detect_document_type(cls, full_text: str) -> str:
        """Heuristic detection of government document type based on statutory headings."""
        full_lower = full_text.lower()
        for pattern, doc_type in cls.DOC_TYPE_PATTERNS:
            if re.search(pattern, full_lower):
                return doc_type
        return "GENERAL_DOCUMENT"

    @classmethod
    def extract_candidates_from_pages(
        cls, pages_text: List[Dict[str, Any]]
    ) -> List[ExtractedFieldCandidate]:
        """Extracts candidate fields across all document pages preserving page numbers."""
        candidates: List[ExtractedFieldCandidate] = []
        seen_keys: set = set()

        for page_info in pages_text:
            page_num = page_info.get("page_number", 1)
            text = page_info.get("text", "")
            if not text:
                continue

            # 1. Certificate / RD Number
            rd_match = re.search(r"\b(RD\d{13,15})\b", text, re.IGNORECASE)
            if rd_match and "rd_number" not in seen_keys:
                candidates.append(ExtractedFieldCandidate(
                    field_key="certificate_number",
                    evidence_type="CERT_NUMBER",
                    extracted_value=rd_match.group(1).upper(),
                    confidence_score=0.98,
                    page_number=page_num,
                    raw_text_snippet=cls._get_snippet(text, rd_match.start(), rd_match.end()),
                ))
                seen_keys.add("rd_number")
            else:
                cert_no_match = re.search(
                    r"(?:certificate\s+no|cert\s+no|roll\s+no|registration\s+no)\s*[:\-]\s*([A-Za-z0-9\-/]+)",
                    text,
                    re.IGNORECASE,
                )
                if cert_no_match and "certificate_number" not in seen_keys:
                    val = cert_no_match.group(1).strip()
                    if len(val) >= 4:
                        candidates.append(ExtractedFieldCandidate(
                            field_key="certificate_number",
                            evidence_type="CERT_NUMBER",
                            extracted_value=val,
                            confidence_score=0.92,
                            page_number=page_num,
                            raw_text_snippet=cls._get_snippet(text, cert_no_match.start(), cert_no_match.end()),
                        ))
                        seen_keys.add("certificate_number")

            # 2. Student / Beneficiary Name
            name_match = re.search(
                r"(?:student\s+name|candidate\s+name|beneficiary\s+name|applicant\s+name|name\s+of\s+student|name\s+of\s+applicant|name)\s*[:\-]\s*([A-Za-z\s\.\']{3,50})",
                text,
                re.IGNORECASE,
            )
            if name_match and "student_name" not in seen_keys:
                raw_name = name_match.group(1).strip()
                # Clean line breaks or extraneous trailing words
                raw_name = raw_name.split("\n")[0].split("  ")[0].strip()
                if len(raw_name) >= 3 and not re.search(r"certificate|board|income|marks", raw_name, re.IGNORECASE):
                    candidates.append(ExtractedFieldCandidate(
                        field_key="student_name",
                        evidence_type="BENEFICIARY_NAME",
                        extracted_value=raw_name,
                        confidence_score=0.90,
                        page_number=page_num,
                        raw_text_snippet=cls._get_snippet(text, name_match.start(), name_match.end()),
                    ))
                    seen_keys.add("student_name")

            # 3. Course / Degree
            course_match = re.search(
                r"(?:course|degree|program|class)\s*[:\-]\s*([A-Za-z0-9\.\s\+\-]{3,60})",
                text,
                re.IGNORECASE,
            )
            if not course_match:
                # Direct course name search
                direct_course = re.search(
                    r"\b(B\.Tech(?:nology)?|B\.E\.|Bachelor of Engineering|B\.Sc|B\.Com|B\.A\.|MBBS|BCA|BBA|Diploma in [A-Za-z\s]+|Class XII|12th Standard|PUC II|Higher Secondary)\b",
                    text,
                    re.IGNORECASE,
                )
                if direct_course and "course" not in seen_keys:
                    candidates.append(ExtractedFieldCandidate(
                        field_key="course",
                        evidence_type="COURSE",
                        extracted_value=direct_course.group(1).strip(),
                        confidence_score=0.88,
                        page_number=page_num,
                        raw_text_snippet=cls._get_snippet(text, direct_course.start(), direct_course.end()),
                    ))
                    seen_keys.add("course")
            elif "course" not in seen_keys:
                c_val = course_match.group(1).strip().split("\n")[0].strip()
                if len(c_val) >= 3:
                    candidates.append(ExtractedFieldCandidate(
                        field_key="course",
                        evidence_type="COURSE",
                        extracted_value=c_val,
                        confidence_score=0.86,
                        page_number=page_num,
                        raw_text_snippet=cls._get_snippet(text, course_match.start(), course_match.end()),
                    ))
                    seen_keys.add("course")

            # 4. Academic Year
            acad_match = re.search(
                r"(?:academic\s+year|session|year\s+of\s+study)\s*[:\-]\s*(\d{4}\s*[-–/]\s*\d{2,4}|(?:1st|2nd|3rd|4th|First|Second|Third|Final)\s*Year)",
                text,
                re.IGNORECASE,
            )
            if not acad_match:
                acad_match = re.search(r"\b(202[3-6]\s*[-–/]\s*202[4-7]|202[3-6]\s*[-–/]\s*[2-3][0-9])\b", text)

            if acad_match and "academic_year" not in seen_keys:
                year_val = acad_match.group(1).strip()
                candidates.append(ExtractedFieldCandidate(
                    field_key="academic_year",
                    evidence_type="ACADEMIC_YEAR",
                    extracted_value=year_val,
                    confidence_score=0.92,
                    page_number=page_num,
                    raw_text_snippet=cls._get_snippet(text, acad_match.start(), acad_match.end()),
                ))
                seen_keys.add("academic_year")

            # 5. Institution / College Name
            inst_match = re.search(
                r"(?:institution|college|school|university|name\s+of\s+institution|name\s+of\s+college)\s*[:\-]\s*([^\n\r,]{4,80})",
                text,
                re.IGNORECASE,
            )
            if inst_match and "institution" not in seen_keys:
                inst_val = inst_match.group(1).strip()
                if len(inst_val) >= 4 and not re.search(r"signature|date|place|code", inst_val, re.IGNORECASE):
                    candidates.append(ExtractedFieldCandidate(
                        field_key="institution",
                        evidence_type="INSTITUTION",
                        extracted_value=inst_val,
                        confidence_score=0.85,
                        page_number=page_num,
                        raw_text_snippet=cls._get_snippet(text, inst_match.start(), inst_match.end()),
                    ))
                    seen_keys.add("institution")

            # 6. Marks or Percentage
            pct_match = re.search(
                r"(?:percentage|marks\s+percentage|aggregate|score|percentile)\s*[:\-]\s*([\d\.]+)%?",
                text,
                re.IGNORECASE,
            )
            if pct_match and "marks_percentage" not in seen_keys:
                try:
                    pct_val = float(pct_match.group(1).strip())
                    if 0.0 <= pct_val <= 100.0:
                        candidates.append(ExtractedFieldCandidate(
                            field_key="marks_percentage",
                            evidence_type="MARKS_PERCENTAGE",
                            extracted_value=f"{pct_val:.2f}%",
                            confidence_score=0.95,
                            page_number=page_num,
                            raw_text_snippet=cls._get_snippet(text, pct_match.start(), pct_match.end()),
                        ))
                        seen_keys.add("marks_percentage")
                except ValueError:
                    pass
            elif "marks_percentage" not in seen_keys:
                total_marks_match = re.search(
                    r"(?:total\s+marks|marks\s+obtained)\s*[:\-]\s*(\d{2,4})\s*/\s*(\d{2,4})",
                    text,
                    re.IGNORECASE,
                )
                if total_marks_match:
                    try:
                        obtained = float(total_marks_match.group(1))
                        maximum = float(total_marks_match.group(2))
                        if maximum > 0 and obtained <= maximum:
                            pct_val = (obtained / maximum) * 100.0
                            candidates.append(ExtractedFieldCandidate(
                                field_key="marks_percentage",
                                evidence_type="MARKS_PERCENTAGE",
                                extracted_value=f"{pct_val:.2f}%",
                                confidence_score=0.93,
                                page_number=page_num,
                                raw_text_snippet=cls._get_snippet(text, total_marks_match.start(), total_marks_match.end()),
                            ))
                            seen_keys.add("marks_percentage")
                    except ValueError:
                        pass

            # 7. Annual Family Income
            inc_match = re.search(
                r"(?:annual\s+family\s+income|annual\s+income|family\s+income|gross\s+income|income)\s*[:\-]\s*(?:Rs\.?|₹|INR)?\s*([\d,]{4,12})",
                text,
                re.IGNORECASE,
            )
            if inc_match and "annual_family_income" not in seen_keys:
                raw_inc_str = inc_match.group(1).replace(",", "").strip()
                try:
                    inc_val = float(raw_inc_str)
                    if 0.0 <= inc_val <= 5000000.0:
                        candidates.append(ExtractedFieldCandidate(
                            field_key="annual_family_income",
                            evidence_type="ANNUAL_INCOME",
                            extracted_value=f"₹{inc_val:,.0f}",
                            confidence_score=0.94,
                            page_number=page_num,
                            raw_text_snippet=cls._get_snippet(text, inc_match.start(), inc_match.end()),
                        ))
                        seen_keys.add("annual_family_income")
                except ValueError:
                    pass

            # 8. Certificate Dates (Issue Date / Valid Till)
            date_match = re.search(
                r"(?:date\s+of\s+issue|issued\s+on|date|dated|valid\s+till|valid\s+upto)\s*[:\-]\s*(\d{1,2}[/-]\d{1,2}[/-]\d{4})",
                text,
                re.IGNORECASE,
            )
            if date_match and "certificate_date" not in seen_keys:
                date_val = date_match.group(1).strip()
                candidates.append(ExtractedFieldCandidate(
                    field_key="issue_date",
                    evidence_type="ISSUE_DATE",
                    extracted_value=date_val,
                    confidence_score=0.90,
                    page_number=page_num,
                    raw_text_snippet=cls._get_snippet(text, date_match.start(), date_match.end()),
                ))
                seen_keys.add("certificate_date")

            # 9. Category (Caste / Community)
            cat_match = re.search(
                r"(?:category|caste|community)\s*[:\-]\s*([A-Za-z0-9\s\(\)\-]{2,40})",
                text,
                re.IGNORECASE,
            )
            if cat_match and "category" not in seen_keys:
                cat_val = cat_match.group(1).strip().split("\n")[0].strip()
                if len(cat_val) >= 2 and not re.search(r"certificate|valid|number", cat_val, re.IGNORECASE):
                    candidates.append(ExtractedFieldCandidate(
                        field_key="category",
                        evidence_type="CASTE_CATEGORY",
                        extracted_value=cat_val,
                        confidence_score=0.88,
                        page_number=page_num,
                        raw_text_snippet=cls._get_snippet(text, cat_match.start(), cat_match.end()),
                    ))
                    seen_keys.add("category")

        return candidates

    @classmethod
    def _get_snippet(cls, text: str, start: int, end: int, window: int = 50) -> str:
        """Extracts clean surrounding text snippet for human verification."""
        s = max(0, start - window)
        e = min(len(text), end + window)
        snippet = text[s:e].replace("\n", " ").strip()
        return f"...{snippet}..." if (s > 0 or e < len(text)) else snippet
