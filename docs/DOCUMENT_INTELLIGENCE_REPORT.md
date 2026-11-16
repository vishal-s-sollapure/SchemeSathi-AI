# SchemeSathi AI — Phase 8: Document Intelligence & Dynamic Checklist Engine Report

**Project**: SchemeSathi AI — AI-Powered Government Benefits and Scholarship Readiness Assistant  
**Cycle**: NxtWave IDEA//FORGE Online Hackathon  
**Phase**: Phase 8 — Document Intelligence and Dynamic Checklist  
**Status**: Completed & Verified  

---

## 1. Executive Summary

Phase 8 introduces the **Document Intelligence and Dynamic Checklist Engine** for SchemeSathi AI. It bridges applicant documentation with deterministic statutory rules. Using PyMuPDF (`fitz`), the system extracts candidate information from Indian government certificates and marksheets, gives users an interactive review flow to edit and confirm evidence, securely isolates confirmed values from unconfirmed raw text, recalculates eligibility rules in real-time, and updates dynamic application checklists.

### Fundamental Safety Principles
1. **Never Guarantee Authenticity Solely from Text Extraction**: Extracted text is strictly an applicant convenience feature. The system never claims that an uploaded document is authentic, valid, or tamper-proof.
2. **Never Auto-Grant Eligibility on Upload**: Uploading a document does not guarantee eligibility. The system will never mark an entire application ready while required statutory conditions remain unresolved.
3. **Strict Separation of Raw and Confirmed State**: Raw text streams are preserved for auditability; only user-confirmed values update candidate profiles and trigger deterministic recalculations.

---

## 2. Document Processing Pipeline (PyMuPDF)

The document ingestion and parsing pipeline is implemented in `backend/app/services/document_intelligence/parser.py`:

- **File Header & Magic Byte Validation**: Inspects the first 1024 bytes of the uploaded file to ensure it starts with `%PDF-`. Files with disguised extensions or corrupted headers are rejected with an explicit HTTP 400 error.
- **File Size Limits**: Enforces a strict 15MB limit (`MAX_UPLOAD_SIZE_BYTES = 15 * 1024 * 1024`).
- **Page-by-Page Stream Extraction**: Opens the document via `fitz.open(stream=...)`, tracks page counts, and iterates page-by-page preserving page numbers.
- **Scanned Page Detection (OCR Fallback Flag)**: For each page, if character density is below 20 characters, the page is flagged as scanned (`ocr_applied = True`), ensuring the system handles image-only certificates gracefully.
- **Secure File Storage**: Generates a cryptographically secure UUID-based filename (`uuid4().hex + ".pdf"`), preventing directory traversal attacks.

---

## 3. Candidate Entity Intelligence & Regex Extraction

Implemented in `backend/app/services/document_intelligence/extractor.py`:

The extractor targets key Indian welfare and scholarship certificate parameters without assuming every document contains all fields:

| Candidate Field | Target Data | Regex / Pattern Strategy | Confidence Scoring |
|---|---|---|---|
| `student_name` / `citizen_name` | Name of applicant | Matches prefixes (`Kum.`, `Sri`, `Smt.`, `Mr.`, `Ms.`) and name patterns | 0.85 – 0.95 |
| `annual_income` | Family annual income | Matches currency variants (`₹`, `Rs.`, `INR`, `·`) and Indian numbering formats | 0.90 – 0.97 |
| `marks_percentage` | Percentage / CGPA / Aggregate | Matches percentage values, distinction marks, aggregate scores (0–100%) | 0.88 – 0.94 |
| `course` | Course admitted / studying | Matches degrees (`B.E.`, `B.Tech`, `B.Sc`, `Diploma`, `M.Tech`, etc.) | 0.85 – 0.92 |
| `academic_year` | Cycle of study | Matches formats like `2024-25`, `2024-2025`, `1st Year`, `3rd Year` | 0.88 – 0.95 |
| `institution` | College / University name | Matches institutional suffixes (`Institute`, `College`, `University`, `Polytechnic`) | 0.85 – 0.92 |
| `issue_date` | Certificate issue date | Matches dates (`DD/MM/YYYY`, `YYYY-MM-DD`, `DD Month YYYY`) | 0.90 – 0.95 |
| `certificate_type` | Document classification | Classifies income, caste, bonafide, marksheet, domicile certificates | 0.85 – 0.95 |
| `certificate_number` | RD / Circular / Registration ID | Matches RD numbers, application numbers, circular references | 0.88 – 0.96 |

Every extracted candidate includes:
- `raw_text_snippet`: The exact text line from which the entity was extracted.
- `page_number`: The specific page where the text appears.
- `confidence_score`: A normalized value between 0.0 and 1.0.
- `verification_disclaimer`: Specific statutory cautionary notice.

---

## 4. Evidence Confirmation Flow & State Separation

Implemented in `backend/app/services/document_service.py` and `DynamicChecklistEngine`:

```
┌─────────────────────────────────┐
│     Uploaded PDF Document       │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│  PyMuPDF Parser & Extractor     │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│ ExtractedEvidence (Raw)         │
│ • extracted_value               │
│ • is_confirmed = False          │
│ • confidence_score              │
│ • page_number                   │
└────────────────┬────────────────┘
                 │
                 ▼ User Reviews & Edits
┌─────────────────────────────────┐
│ User Confirmation Endpoint      │
│ POST /documents/{id}/confirm    │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│ ExtractedEvidence (Confirmed)   │
│ • confirmed_value               │
│ • is_confirmed = True           │
│ • confirmed_at = timestamp      │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│ Deterministic Rule Engine       │
│ & Dynamic Checklist Sync        │
└─────────────────────────────────┘
```

1. **Raw State Preserved**: `extracted_value` is never overwritten, maintaining complete administrative auditability.
2. **Confirmed State Isolated**: `confirmed_value` is populated only when the user explicitly reviews, optionally modifies, and accepts the evidence.
3. **Database Integrity**: Extracted evidence records track confirmation timestamps and user verification.

---

## 5. Dynamic Checklist Engine

Implemented in `backend/app/services/document_intelligence/checklist_engine.py`:

### Status Lifecycle
Each checklist item adheres to a deterministic 6-state lifecycle:
- `NOT_STARTED`: Requirement exists; no document uploaded.
- `REQUIRED`: Statutory mandatory item; pending submission.
- `UPLOADED`: Document uploaded; candidate text extracted but pending user confirmation.
- `CONFIRMED`: Evidence reviewed and confirmed by applicant.
- `NEEDS_REVIEW`: Ambiguous extraction or conflicting parameters flagged.
- `NOT_APPLICABLE`: Requirement waived based on applicant category (e.g., Caste Certificate waived for General category).

### Dynamic Recalculation
When evidence is confirmed:
1. `student_profile` or `citizen_profile` attributes are synchronized (e.g. `annual_family_income`, `marks_percentage`).
2. `DeterministicRuleEngine` re-evaluates all statutory requirements.
3. Checklist readiness score is computed:
   $$\text{Readiness Score} = \left( \frac{\text{Confirmed Items} + \text{Waived Items}}{\text{Total Statutory Requirements}} \right) \times 100$$
4. Submission readiness rule:
   - `is_ready_for_submission = True` ONLY when `unresolved_mandatory_count == 0` AND all mandatory conditions evaluate to `MEETS_REQUIREMENT`.

---

## 6. Secure Document Deletion Lifecycle

Implemented in `backend/app/services/document_service.py`:
- Deletes physical file from `UPLOAD_DIR` using safe path operations to prevent path traversal.
- Cascades deletion of all associated `ExtractedEvidence` records.
- Automatically rolls back any linked `ApplicationChecklist` items back to `REQUIRED` or `NOT_STARTED`.
- Recalculates checklist readiness score and overall submission readiness.

---

## 7. Verification & Test Suite Results

The Phase 8 test suite (`backend/tests/test_document_intelligence.py`) covers 17 dedicated unit and integration tests:

1. `test_pdf_upload_and_extraction`: Validates PyMuPDF extraction on synthetic test PDFs.
2. `test_invalid_pdf_rejected`: Ensures corrupt/non-PDF files return HTTP 400.
3. `test_file_size_limit_enforced`: Rejects files exceeding 15MB.
4. `test_income_certificate_extraction`: Tests multi-currency income regex extraction (`₹`, `Rs.`, `·`).
5. `test_marksheet_extraction`: Tests academic percentage extraction and page mapping.
6. `test_user_confirmation_flow`: Tests separation of `extracted_value` and `confirmed_value`.
7. `test_dynamic_checklist_generation`: Validates statutory checklist item creation.
8. `test_general_category_waiver`: Confirms waiver of caste certificate for General category.
9. `test_checklist_update_on_confirmation`: Validates state transition from `REQUIRED` to `CONFIRMED`.
10. `test_dynamic_eligibility_recalculation`: Validates recalculation of rule engine conditions upon confirmation.
11. `test_unresolved_conditions_block_readiness`: Verifies submission readiness stays `False` while conditions are unresolved.
12. `test_document_deletion_and_rollback`: Tests physical file cleanup and checklist rollback.
13. `test_scanned_pdf_ocr_flag`: Validates scanned page detection.
14. `test_non_authenticity_disclaimer_present`: Ensures statutory legal disclaimers are returned.
15. `test_api_upload_document`: Tests HTTP `POST /api/v1/documents/upload`.
16. `test_api_confirm_evidence`: Tests HTTP `POST /api/v1/documents/{id}/confirm-evidence`.
17. `test_api_generate_checklist`: Tests HTTP `POST /api/v1/checklists/generate`.

### Summary Test Metrics
- **Phase 8 Tests**: 17 of 17 Passed (100%)
- **Total Backend Tests**: 75 of 75 Passed (100%)
- **Frontend Build**: Zero TypeScript errors (`tsc && vite build` passed)
