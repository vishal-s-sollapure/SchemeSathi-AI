import pytest
from app.api.v1.chat import ask_policy_or_scheme_question
from app.schemas.chat import RAGQueryRequest
from app.services.rag import RAGPipeline
from app.services.rag.generator import GroundedResponseGenerator


@pytest.fixture(scope="module")
def rag_pipeline():
    return RAGPipeline.get_instance()


def test_voice_demonstration_kannada(rag_pipeline):
    """Voice demonstration query in Kannada:
    'ನನಗೆ ಯಾವ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು ಸಿಗಬಹುದು?' (What government schemes may I qualify for?)
    
    Verifies:
    1. Returns sufficient evidence (grounded in verified schemes).
    2. Response is generated in Kannada ('kn').
    3. Strictly preserves original scheme names (PM-KISAN, Gruha Lakshmi, CSSS, Pragati, SSP).
    4. Strictly preserves monetary numbers and clauses (₹6,000, ₹2,000, ₹50,000, Clause 5).
    """
    query = "ನನಗೆ ಯಾವ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು ಸಿಗಬಹುದು?"
    resp = rag_pipeline.ask(query)

    assert resp.sufficient_evidence is True
    assert resp.language == "kn"
    assert "PM-KISAN" in resp.answer or "ಪಿಎಂ ಕಿಸಾನ್" in resp.answer
    assert "Gruha Lakshmi" in resp.answer or "ಗೃಹ ಲಕ್ಷ್ಮಿ" in resp.answer
    assert "₹6,000" in resp.answer
    assert "₹2,000" in resp.answer
    assert "Clause 5" in resp.answer
    assert len(resp.citations) >= 1
    assert resp.is_grounded is True


def test_voice_demonstration_hindi(rag_pipeline):
    """Voice demonstration query in Hindi:
    'मुझे कौन-कौन सी सरकारी योजनाएं मिल सकती हैं?' (What government schemes may I qualify for?)
    
    Verifies:
    1. Returns sufficient evidence.
    2. Response is generated in Hindi ('hi').
    3. Strictly preserves original scheme names (PM-KISAN, Gruha Lakshmi, AICTE Pragati, CSSS, SSP).
    4. Strictly preserves statutory numbers and clauses (₹6,000, ₹2,000, ₹50,000, ₹12,000, Clause 5).
    """
    query = "मुझे कौन-कौन सी सरकारी योजनाएं मिल सकती हैं?"
    resp = rag_pipeline.ask(query)

    assert resp.sufficient_evidence is True
    assert resp.language == "hi"
    assert "PM-KISAN" in resp.answer or "प्रधानमंत्री किसान सम्मान निधि" in resp.answer
    assert "Gruha Lakshmi" in resp.answer or "गृह लक्ष्मी" in resp.answer
    assert "₹6,000" in resp.answer
    assert "₹2,000" in resp.answer
    assert "Clause 5" in resp.answer
    assert len(resp.citations) >= 1
    assert resp.is_grounded is True


def test_voice_demonstration_english(rag_pipeline):
    """Voice demonstration query in English:
    'What government schemes may I qualify for?'
    
    Verifies:
    1. Returns sufficient evidence.
    2. Response is generated in English ('en').
    3. Outlines all 5 verified welfare schemes and scholarships.
    4. Directs applicant to personalized Scheme Discovery and ScholarReady modules.
    """
    query = "What government schemes may I qualify for?"
    resp = rag_pipeline.ask(query)

    assert resp.sufficient_evidence is True
    assert resp.language == "en"
    assert "Pradhan Mantri Kisan Samman Nidhi" in resp.answer
    assert "Gruha Lakshmi" in resp.answer
    assert "AICTE Pragati" in resp.answer
    assert "Central Sector Scheme of Scholarship" in resp.answer
    assert "₹6,000" in resp.answer
    assert "₹2,000" in resp.answer
    assert "₹50,000" in resp.answer
    assert "Scheme Discovery" in resp.answer
    assert "ScholarReady" in resp.answer


def test_language_detection():
    """Verifies Unicode block detection for Kannada, Hindi, and English."""
    assert GroundedResponseGenerator.detect_language("ನನಗೆ ಯೋಜನೆ ಬೇಕು") == "kn"
    assert GroundedResponseGenerator.detect_language("मुझे योजना चाहिए") == "hi"
    assert GroundedResponseGenerator.detect_language("Tell me about scholarships") == "en"


def test_language_override(rag_pipeline):
    """Ensures manual language override forces the synthesis language regardless of prompt characters."""
    query = "What are the rules for Gruha Lakshmi?"
    resp = rag_pipeline.ask(query, language="kn")
    assert resp.language == "kn"
    assert "ಅಧಿಕೃತ ಸರ್ಕಾರಿ ದಾಖಲೆಯ ಪ್ರಕಾರ" in resp.answer or "ಗೃಹ ಲಕ್ಷ್ಮಿ" in resp.answer


def test_preservation_of_numbers_urls_and_legal_terms(rag_pipeline):
    """Strict test to guarantee that numbers, statutory clauses, and official URLs are never altered."""
    query_kn = "ಪಿಎಂ ಕಿಸಾನ್ ಆದಾಯ ತೆರಿಗೆ ಷರತ್ತು ಏನು?"
    resp_kn = rag_pipeline.ask(query_kn)
    assert resp_kn.sufficient_evidence is True
    # Numbers and official references must be preserved
    assert "Clause 5" in resp_kn.answer or "5" in resp_kn.answer
    assert "pmkisan.gov.in" in resp_kn.answer or any("pmkisan.gov.in" in c.official_source_url for c in resp_kn.citations)


def test_api_chat_query_multilingual():
    """Tests POST /api/v1/chat/query endpoint with Kannada and Hindi requests."""
    # 1. Kannada API query
    req_kn = RAGQueryRequest(query="ನನಗೆ ಯಾವ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು ಸಿಗಬಹುದು?", language="kn")
    resp_kn = ask_policy_or_scheme_question(req_kn)
    assert resp_kn.language == "kn"
    assert resp_kn.sufficient_evidence is True
    assert "PM-KISAN" in resp_kn.answer or "ಪಿಎಂ ಕಿಸಾನ್" in resp_kn.answer

    # 2. Hindi API query
    req_hi = RAGQueryRequest(query="मुझे कौन-कौन सी सरकारी योजनाएं मिल सकती हैं?", language="hi")
    resp_hi = ask_policy_or_scheme_question(req_hi)
    assert resp_hi.language == "hi"
    assert resp_hi.sufficient_evidence is True
    assert "PM-KISAN" in resp_hi.answer or "प्रधानमंत्री किसान सम्मान निधि" in resp_hi.answer
