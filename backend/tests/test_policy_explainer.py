import pytest
from app.schemas.policy import (
    PolicyDocumentSummary,
    PolicyExplanationRequest,
    PolicyExplanationResponse,
    PolicySimplificationResult,
)
from app.services.policy_service import PolicyService
from app.api.v1.policy import (
    list_policy_documents,
    get_policy_document_detail,
    simplify_policy_document,
    explain_policy_or_clause,
)


@pytest.fixture
def policy_service():
    return PolicyService.get_instance()


class TestPolicyExplainerEngine:
    """Rigorous verification suite for Phase 10 Policy and Rights Explainer."""

    def test_list_policy_documents(self, policy_service):
        """Verifies discovery and retrieval of verified government documents."""
        docs = policy_service.list_policy_documents()
        assert len(docs) >= 3
        ids = [d.id for d in docs]
        assert "POL-SSP-EATTEST-CIRCULAR" in ids
        assert "POL-PMKISAN-EKYC-EXCLUSION" in ids
        assert "POL-NSP-OTR-GUIDELINE" in ids

        # Search filter
        sakala_docs = policy_service.list_policy_documents(search_query="Sakala")
        assert len(sakala_docs) >= 1
        assert "Sakala" in sakala_docs[0].title or "Sakala" in sakala_docs[0].executive_summary

    def test_get_policy_document_detail(self, policy_service):
        """Verifies fetching full document record with official clauses."""
        doc = policy_service.get_policy_document_by_id("POL-SSP-EATTEST-CIRCULAR")
        assert doc is not None
        assert doc["notification_number"] == "SWD-SSP-2023-CIR-09"
        assert len(doc["official_clauses"]) >= 2
        clauses = [c["clause_number"] for c in doc["official_clauses"]]
        assert "Section 7.3" in clauses
        assert "Section 4.1" in clauses

    def test_simplify_policy_6_parts_english(self, policy_service):
        """Verifies complete 6-part government PDF simplification workflow in English."""
        res = policy_service.simplify_policy("POL-SSP-EATTEST-CIRCULAR", language="en")
        assert isinstance(res, PolicySimplificationResult)

        # 1. Five-line summary
        assert len(res.five_line_summary) == 5
        assert any("7 working days" in line or "Sakala" in line for line in res.five_line_summary)

        # 2. Important conditions
        assert len(res.important_conditions) >= 2
        assert any("AISHE" in c or "Aadhaar" in c for c in res.important_conditions)

        # 3. Dates and deadlines
        assert len(res.dates_and_deadlines) >= 2
        assert any("7 Working Days" in d.timeframe_or_date for d in res.dates_and_deadlines)

        # 4. Required documents
        assert len(res.required_documents) >= 3
        req_names = [d.name for d in res.required_documents]
        assert any("Caste & Income" in name for name in req_names)

        # 5. Application steps
        assert len(res.application_steps) >= 3
        assert any("SSP" in s or "Step 1" in s for s in res.application_steps)

        # 6. Important warnings
        assert len(res.important_warnings) >= 1

        # Legal disclaimer & guardrail
        assert "Legal Notice & Guardrail" in res.legal_disclaimer
        assert "does not constitute formal legal representation" in res.legal_disclaimer

    def test_simplify_policy_kannada_and_hindi(self, policy_service):
        """Verifies trilingual translation of 5-line summary and disclaimers."""
        res_kn = policy_service.simplify_policy("POL-PMKISAN-EKYC-EXCLUSION", language="kn")
        assert res_kn.language == "kn"
        assert len(res_kn.five_line_summary) == 5
        assert any("ಇ-ಕೆವೈಸಿ" in line or "ಪಿಎಂ-ಕಿಸಾನ್" in line for line in res_kn.five_line_summary)
        assert "ಕಾನೂನು ಸೂಚನೆ" in res_kn.legal_disclaimer

        res_hi = policy_service.simplify_policy("POL-PMKISAN-EKYC-EXCLUSION", language="hi")
        assert res_hi.language == "hi"
        assert len(res_hi.five_line_summary) == 5
        assert any("ई-केवाईसी" in line or "पीएम-किसान" in line for line in res_hi.five_line_summary)
        assert "कानूनी सूचना" in res_hi.legal_disclaimer

    def test_explain_specific_clause_section_7_3(self, policy_service):
        """Verifies clause-grounded inquiry on Section 7.3 under Karnataka Sakala Act."""
        req = PolicyExplanationRequest(
            document_id="POL-SSP-EATTEST-CIRCULAR",
            clause_or_section="Section 7.3",
            question="What is the time limit for verification under Section 7.3?",
            language="en",
        )
        resp = policy_service.explain_policy_query(req)
        assert resp.sufficient_evidence is True
        assert resp.clause_referenced is not None
        assert "Section 7.3" in resp.clause_referenced
        assert "seven working days" in resp.verbatim_official_clause.lower()
        assert len(resp.citations) >= 1
        assert resp.citations[0].circular_number == "SWD-SSP-2023-CIR-09"
        assert "Legal Guardrail" in resp.legal_disclaimer

    def test_explain_specific_clause_pmkisan_clause_5b(self, policy_service):
        """Verifies statutory exclusion clause query under PM-KISAN Clause 5(b)."""
        req = PolicyExplanationRequest(
            document_id="POL-PMKISAN-EKYC-EXCLUSION",
            clause_or_section="Clause 5(b)",
            question="Who is excluded from PM-KISAN under Clause 5(b)?",
            language="en",
        )
        resp = policy_service.explain_policy_query(req)
        assert resp.sufficient_evidence is True
        assert "Income Tax" in resp.verbatim_official_clause
        assert "disqualified" in resp.verbatim_official_clause.lower()
        assert len(resp.supporting_passages) >= 1

    def test_explain_example_questions(self, policy_service):
        """Verifies all 6 mandatory example questions specified in Phase 10."""
        # 1. Explain notification in simple language
        resp1 = policy_service.explain_policy_query(
            PolicyExplanationRequest(
                document_id="POL-NSP-OTR-GUIDELINE",
                question="Explain this notification in simple language.",
                language="en",
            )
        )
        assert resp1.sufficient_evidence is True
        assert "OTR" in resp1.simplified_explanation

        # 2. What are the important conditions?
        resp2 = policy_service.explain_policy_query(
            PolicyExplanationRequest(
                document_id="POL-NSP-OTR-GUIDELINE",
                question="What are the important conditions?",
                language="en",
            )
        )
        assert resp2.sufficient_evidence is True
        assert len(resp2.restrictions_and_responsibilities) >= 1

        # 3. Who can benefit from this policy?
        resp3 = policy_service.explain_policy_query(
            PolicyExplanationRequest(
                document_id="POL-AICTE-PRAGATI-GUIDELINES",
                question="Who can benefit from this policy?",
                language="en",
            )
        )
        assert resp3.sufficient_evidence is True
        assert "female" in resp3.simplified_explanation.lower() or "girl" in resp3.simplified_explanation.lower()

        # 4. What documents are required?
        resp4 = policy_service.explain_policy_query(
            PolicyExplanationRequest(
                document_id="POL-SSP-EATTEST-CIRCULAR",
                question="What documents are required?",
                language="en",
            )
        )
        assert resp4.sufficient_evidence is True
        assert "Aadhaar" in resp4.simplified_explanation or "Nadakacheri" in resp4.simplified_explanation

        # 5. What are the application deadlines?
        resp5 = policy_service.explain_policy_query(
            PolicyExplanationRequest(
                document_id="POL-SSP-EATTEST-CIRCULAR",
                question="What are the application deadlines?",
                language="en",
            )
        )
        assert resp5.sufficient_evidence is True
        assert len(resp5.important_dates) >= 1

        # 6. What does this particular clause mean?
        resp6 = policy_service.explain_policy_query(
            PolicyExplanationRequest(
                document_id="POL-KAR-GRUHALAKSHMI-ORDER",
                clause_or_section="Clause 4(a)",
                question="What does this particular clause mean?",
                language="en",
            )
        )
        assert resp6.sufficient_evidence is True
        assert resp6.verbatim_official_clause is not None
        assert "income tax" in resp6.verbatim_official_clause.lower()

    def test_out_of_scope_query_safety_guardrail(self, policy_service):
        """Verifies strict safety rule: do not invent rights, and state lack of evidence clearly."""
        req = PolicyExplanationRequest(
            document_id="POL-SSP-EATTEST-CIRCULAR",
            question="Can students claim free cryptocurrency and sports cars under Sakala?",
            language="en",
        )
        resp = policy_service.explain_policy_query(req)
        assert resp.sufficient_evidence is False
        assert "does not contain explicit provisions" in resp.simplified_explanation
        assert len(resp.citations) == 0

    def test_api_router_endpoints(self):
        """Verifies API router functions directly."""
        docs = list_policy_documents(search=None)
        assert len(docs) >= 3

        doc = get_policy_document_detail("POL-SSP-EATTEST-CIRCULAR")
        assert doc["id"] == "POL-SSP-EATTEST-CIRCULAR"

        simplification = simplify_policy_document("POL-SSP-EATTEST-CIRCULAR", language="en")
        assert len(simplification.five_line_summary) == 5

        explanation = explain_policy_or_clause(
            PolicyExplanationRequest(
                document_id="POL-SSP-EATTEST-CIRCULAR",
                question="What is the Sakala verification deadline?",
                language="en",
            )
        )
        assert explanation.sufficient_evidence is True
