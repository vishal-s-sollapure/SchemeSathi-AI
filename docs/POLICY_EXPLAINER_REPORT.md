# Phase 10: Policy and Rights Explainer Engine Report

**SchemeSathi AI — AI-Powered Government Benefits & Scholarship Assistant**  
**Engineering Track**: Senior AI Engineer specializing in Document-Grounded Public Information Systems  
**Status**: Completed & Verified  

---

## 1. Executive Summary

Phase 10 implements the **SchemeSathi Policy and Rights Explainer**, an authoritative, document-grounded civic intelligence module designed to demystify complex government circulars, statutory orders, welfare schemes, and student entitlement rules.

The system translates dense administrative legalese into clear, plain-language civic knowledge across **English, Kannada (`kn`), and Hindi (`hi`)**, while adhering to strict legal and constitutional guardrails:
1. **Never provides unsupported legal conclusions**.
2. **Clearly distinguishes simplified civic summaries from authoritative legal/administrative interpretations**.
3. **If a government order does not contain explicit provisions answering an inquiry, it states so honestly and unambiguously** (zero hallucinated rights).
4. **Never invents citizen rights or statutory entitlements**.
5. **Grounded and tested against real, verified primary government notifications**.

---

## 2. Architecture & Data Design

### 2.1 Backend Architecture

- **`app.schemas.policy`**:
  - `PolicyDocumentSummary`: Metadata for verified circulars (ID, title, department, notification number, gazette URL, cycle, category).
  - `PolicyClauseItem`: Individual statutory clauses with clause numbers, titles, verbatim text, and simplified meanings.
  - `PolicyDeadlineItem`: Structured timelines with labels, timeframe strings, and statutory authority tracking.
  - `PolicyDocumentRequiredItem`: Documentary proof mandates with issuing authorities and formats.
  - `PolicySimplificationResult`: Standardized 6-element civic simplification model.
  - `PolicyExplanationRequest` & `PolicyExplanationResponse`: Section-aware query and citation model.
- **`app.services.policy_service.PolicyService`**:
  - `list_policy_documents(search_query)`: Dynamic search and discovery of verified government circulars.
  - `simplify_policy(document_id, language)`: Generates structured 6-pillar civic breakdown.
  - `explain_policy_query(request)`: Clause-level and natural-language Q&A engine with verbatim gazette excerpt retrieval.
  - `simplify_uploaded_pdf(pdf_path, ...)`: PyMuPDF-based optical parser for custom government circulars.
- **`app.api.v1.policy`**:
  - `GET /api/v1/policy/documents`: Discovers verified gazette orders.
  - `GET /api/v1/policy/documents/{document_id}`: Retrieves comprehensive clause records.
  - `GET /api/v1/policy/simplify/{document_id}`: Generates trilingual 6-part simplification.
  - `POST /api/v1/policy/explain`: Grounded clause/section explanation endpoint.
  - `POST /api/v1/policy/simplify-pdf`: Multipart upload for custom citizen PDFs.

### 2.2 Verified Knowledge Base Circulars

The knowledge base in `backend/app/data/seeds/policy_circulars.json` contains full structured records for:

1. **`POL-SSP-EATTEST-CIRCULAR`**:
   - *Title*: Standard Operating Procedure for e-Attestation & Student Entitlements under Karnataka Sakala Services Act.
   - *Authority*: Social Welfare Department & Centre for e-Governance, Karnataka (`SWD-SSP-2023-CIR-09`).
   - *Key Clauses*: Section 4.1 (Nadakacheri 15-digit RD integration), Section 7.3 (Mandatory 7-day Sakala statutory deadline).
2. **`POL-PMKISAN-EKYC-EXCLUSION`**:
   - *Title*: Mandatory e-KYC Verification, Land Record Seeding and Exclusion Enforcement Circular for PM-KISAN.
   - *Authority*: Ministry of Agriculture & Farmers Welfare, Govt of India (`F.No. 1-1/2023-Credit-II-PMKISAN`).
   - *Key Clauses*: Clause 2.2 (NPCI Aadhaar Payment Bridge mandate), Clause 5(b) (Statutory income tax and institutional landholder exclusion).
3. **`POL-NSP-OTR-GUIDELINE`**:
   - *Title*: Implementation of One-Time Registration (OTR) and Biometric Facial Authentication on National Scholarship Portal.
   - *Authority*: Department of Higher Education, Ministry of Education, Govt of India (`DBT/NSP/OTR/2024-01`).
   - *Key Clauses*: Para 3 (14-digit lifelong OTR creation via Aadhaar FaceRD), Para 6 (Institutional biometric verification mandate).
4. **`POL-AICTE-PRAGATI-GUIDELINES`**:
   - *Title*: Implementation Guidelines for AICTE Pragati Scholarship Scheme for Girl Students (Degree).
   - *Authority*: All India Council for Technical Education (`AICTE/RIFD/Pragati/2023-24`).
   - *Key Clauses*: Clause 3.1 (₹8.00 Lakh family income cap, max 2 girls per family), Clause 6.4 (Exclusivity of scholarship assistance).
5. **`POL-MOE-CSSS-GUIDELINES`**:
   - *Title*: Operational Guidelines for Central Sector Scheme of Scholarship for College and University Students (PM-USP).
   - *Authority*: Department of Higher Education, Ministry of Education, Govt of India (`F.No. 1-1/2022-NS.1`).
   - *Key Clauses*: Clause 2.1 (80th percentile board cutoff criterion), Clause 5.2 (50% annual marks renewal requirement).
6. **`POL-KAR-GRUHALAKSHMI-ORDER`**:
   - *Title*: Government Order for the Implementation of Gruha Lakshmi Scheme in Karnataka.
   - *Authority*: Department of Women and Child Development, Karnataka (`WCD-GL-2023-GO-102`).
   - *Key Clauses*: Clause 2.1 (Female household head / Yajamani recognition on ration cards), Clause 4(a) (Taxpayer and GST filer disqualification).

---

## 3. The 6-Point Civic Simplification Workflow

For any selected or uploaded circular, SchemeSathi synthesizes the text into 6 standardized civic pillars:

| Pillar | Civic Description | Implementation Detail |
|---|---|---|
| **1. Five-Line Summary** | Plain-language distillation in 5 distinct sentences. | Tailored in English, Kannada, or Hindi with zero jargon. |
| **2. Important Conditions** | Core eligibility and operational caps. | Highlights AISHE status, income caps, domicile, and academic criteria. |
| **3. Dates & Deadlines** | Statutory timelines, application cutoffs, review windows. | Badged as critical or standard with enforcing statutory authorities. |
| **4. Required Documents** | Mandatory evidentiary documents. | Catalogs document name, issuing department, and verified format. |
| **5. Application Steps** | Sequenced step-by-step action guide. | Ordered citizen compliance progression from login to DBT receipt. |
| **6. Important Warnings** | Disqualifications, penalties, and exclusion cautions. | Explicit alerts regarding income tax disqualification, recovery of excess receipts, and criminal prosecution for forgery. |

---

## 4. Interactive Clause & Section Q&A

Citizens can interrogate specific clauses or use canonical questions:
- *"Explain this notification in simple language."*
- *"What are the important conditions?"*
- *"Who can benefit from this policy?"*
- *"What documents are required?"*
- *"What are the application deadlines?"*
- *"What does this particular clause mean?"*

### Side-by-Side Verification Display:
- **Left Column**: Plain-language civic explanation in requested language (`en`, `kn`, `hi`), with voice audio synthesis support.
- **Right Column**: Verbatim official gazette text + validated official citations with exact circular numbers, page numbers, and direct gazette links.

### Unsupported Query Guardrail:
When an inquiry is out of scope or requests unsupported entitlements (e.g. *"Can students claim free cryptocurrency or luxury cars under Sakala?"*), the engine returns `sufficient_evidence=False` with the following honest clarification:
> *"The verified government document does not contain explicit provisions or evidence regarding this specific inquiry. SchemeSathi AI strictly adheres to verified official sources and will not fabricate citizen rights, entitlements, or legal interpretations."*

---

## 5. Verification & Test Results

### 5.1 Backend Pytest Suite
- **Policy Explainer Suite (`backend/tests/test_policy_explainer.py`)**: **9 tests passed** (100%).
  1. `test_list_policy_documents`: Verifies discovery and search filtering across gazette orders.
  2. `test_get_policy_document_detail`: Verifies structured clause retrieval.
  3. `test_simplify_policy_6_parts_english`: Verifies 6-part simplification workflow.
  4. `test_simplify_policy_kannada_and_hindi`: Verifies trilingual generation for Kannada & Hindi.
  5. `test_explain_specific_clause_section_7_3`: Verifies Sakala 7-day statutory limit clause explanation.
  6. `test_explain_specific_clause_pmkisan_clause_5b`: Verifies PM-KISAN Clause 5(b) tax exclusion.
  7. `test_explain_example_questions`: Verifies all 6 mandatory example questions.
  8. `test_out_of_scope_query_safety_guardrail`: Verifies non-fabrication safety fallback.
  9. `test_api_router_endpoints`: Verifies HTTP endpoints directly.
- **Total Backend Test Suite**: **91 of 91 tests passed** in 8.45s across the entire project.

### 5.2 Frontend Compilation
- Command: `cd frontend; npm run build`
- Output: `✓ 1662 modules transformed. ✓ built in 40.90s` with **0 errors**.
