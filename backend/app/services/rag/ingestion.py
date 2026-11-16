import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except (ImportError, Exception):
    PYMUPDF_AVAILABLE = False

from app.services.rag.chunking import SectionAwareChunker
from app.services.rag.models import DocumentChunk

logger = logging.getLogger("rag_ingestion")


class OfficialDocumentIngestion:
    """Official knowledge base ingestion and normalization engine.
    
    Transforms verified government circulars, scholarship frameworks, welfare guidelines,
    and PDF notifications into structured, section-aware evidence chunks.
    """

    def __init__(self, chunker: Optional[SectionAwareChunker] = None):
        self.chunker = chunker or SectionAwareChunker()

    def ingest_seed_circulars(self, json_path: Path) -> List[DocumentChunk]:
        """Ingests verified policy circulars with exact clause texts and executive summaries."""
        if not json_path.exists():
            logger.warning(f"Seed file not found: {json_path}")
            return []

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        chunks: List[DocumentChunk] = []

        for item in data:
            doc_id = item.get("id", "POL")
            doc_title = item.get("title", "Official Policy Circular")
            department = item.get("issuing_department", "Government Department")
            gazette_url = item.get("official_gazette_url", "https://india.gov.in")
            cycle = item.get("applicable_cycle", "2024-25 / 2025-26")
            notification_no = item.get("notification_number", "")

            # 1. Executive Summary Chunk
            summary = item.get("executive_summary", "")
            if summary:
                chunks.extend(
                    self.chunker.chunk_section(
                        text=summary,
                        document_title=doc_title,
                        section_or_clause="Executive Summary",
                        official_source_url=gazette_url,
                        government_department=department,
                        page_number="1",
                        scheme_id=doc_id,
                        applicable_cycle=cycle,
                        base_chunk_id=f"CHK-{doc_id}-SUMM",
                        extra_metadata={"notification_number": notification_no, "type": "summary"},
                    )
                )

            # 2. Official Clauses
            clauses = item.get("official_clauses", [])
            for c_idx, clause in enumerate(clauses, start=1):
                c_num = clause.get("clause_number", f"Clause {c_idx}")
                c_title = clause.get("clause_title", "")
                c_text = clause.get("official_text", "")
                full_text = f"{c_title}: {c_text}" if c_title else c_text

                chunks.extend(
                    self.chunker.chunk_section(
                        text=full_text,
                        document_title=doc_title,
                        section_or_clause=c_num,
                        official_source_url=gazette_url,
                        government_department=department,
                        page_number="2",
                        scheme_id=doc_id,
                        applicable_cycle=cycle,
                        base_chunk_id=f"CHK-{doc_id}-CL{c_idx}",
                        extra_metadata={"notification_number": notification_no, "type": "official_clause"},
                    )
                )

            # 3. Citizen Simplified Points
            simplified = item.get("citizen_simplified_points", [])
            if simplified:
                sim_text = "Citizen Entitlement Rules:\n" + "\n".join(f"- {pt}" for pt in simplified)
                chunks.extend(
                    self.chunker.chunk_section(
                        text=sim_text,
                        document_title=doc_title,
                        section_or_clause="Citizen Entitlement Rights",
                        official_source_url=gazette_url,
                        government_department=department,
                        page_number="1",
                        scheme_id=doc_id,
                        applicable_cycle=cycle,
                        base_chunk_id=f"CHK-{doc_id}-CITIZEN",
                        extra_metadata={"notification_number": notification_no, "type": "rights_summary"},
                    )
                )

        return chunks

    def ingest_seed_schemes(self, json_path: Path) -> List[DocumentChunk]:
        """Ingests verified civic welfare schemes into evidence chunks."""
        if not json_path.exists():
            return []

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        chunks: List[DocumentChunk] = []

        for scheme in data:
            s_id = scheme.get("id", "SCHEME")
            title = scheme.get("official_name", "")
            dept = scheme.get("government_department", "")
            url = scheme.get("official_source_url", "")
            app_url = scheme.get("application_url", "")
            benefit = scheme.get("annual_benefit", "")
            benefit_type = scheme.get("benefit_type", "")
            desc = scheme.get("description", "")
            target = scheme.get("target_beneficiaries", "")
            cycle = scheme.get("policy_cycle", "Continuous")

            # Overview chunk
            overview = (
                f"{title} is a {scheme.get('level', 'Central')} welfare scheme administered by {dept}. "
                f"Purpose: {desc} Target Beneficiaries: {target}. "
                f"Entitlement: {benefit} disbursed via {benefit_type}. Official Portal: {app_url or url}"
            )

            chunks.extend(
                self.chunker.chunk_section(
                    text=overview,
                    document_title=f"Authoritative Guidelines: {title}",
                    section_or_clause="Operational Framework & Entitlements",
                    official_source_url=url,
                    government_department=dept,
                    page_number="1",
                    scheme_id=s_id,
                    applicable_cycle=cycle,
                    base_chunk_id=f"CHK-{s_id}-OVERVIEW",
                    extra_metadata={"category": scheme.get("category", "")},
                )
            )

        return chunks

    def ingest_seed_scholarships(self, json_path: Path) -> List[DocumentChunk]:
        """Ingests verified undergraduate scholarships into evidence chunks."""
        if not json_path.exists():
            return []

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        chunks: List[DocumentChunk] = []

        for sch in data:
            s_id = sch.get("id", "SCH")
            title = sch.get("official_name", "")
            dept = sch.get("government_department", "")
            url = sch.get("official_source_url", "")
            benefit = sch.get("benefit_amount_annual", "")
            desc = sch.get("description", "")
            cycle = sch.get("academic_cycle", "2024-25")
            income_cap = sch.get("max_annual_income", 0)

            overview = (
                f"{title} is governed by {dept}. {desc} "
                f"Financial assistance: {benefit}. Maximum parental income limit: ₹{income_cap:,.0f} per annum. "
                f"Course Level: {sch.get('course_level', '')}. Level: {sch.get('level', '')}. Source: {url}"
            )

            chunks.extend(
                self.chunker.chunk_section(
                    text=overview,
                    document_title=f"Scheme Operational Guidelines: {title}",
                    section_or_clause="Eligibility Framework & Financial Concessions",
                    official_source_url=url,
                    government_department=dept,
                    page_number="1",
                    scheme_id=s_id,
                    applicable_cycle=cycle,
                    base_chunk_id=f"CHK-{s_id}-OVERVIEW",
                    extra_metadata={"max_income": income_cap},
                )
            )

        return chunks

    def ingest_seed_rules(self, json_path: Path) -> List[DocumentChunk]:
        """Ingests detailed deterministic statutory rules with page and clause metadata."""
        if not json_path.exists():
            return []

        # Load official sources mapping if available
        sources_map: Dict[str, Dict[str, Any]] = {}
        sources_path = json_path.parent / "official_sources.json"
        if sources_path.exists():
            try:
                with open(sources_path, "r", encoding="utf-8") as sf:
                    sources_list = json.load(sf)
                    sources_map = {s.get("id"): s for s in sources_list if isinstance(s, dict) and s.get("id")}
            except Exception as e:
                logger.warning(f"Failed to load official sources for rule ingestion: {e}")

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        chunks: List[DocumentChunk] = []

        for rule in data:
            r_id = rule.get("id", "RULE")
            clause = rule.get("clause_or_section", "Statutory Rule")
            page = rule.get("page_number", "1")
            desc = rule.get("requirement_description", "")
            guidance = rule.get("failure_guidance", "")
            cycle = rule.get("applicable_cycle", "2024-25")
            scheme_id = rule.get("scholarship_id") or rule.get("scheme_id") or "GOV"
            source_id = rule.get("source_id", "")

            source_meta = sources_map.get(source_id, {})
            doc_title = source_meta.get("source_title") or f"Government Eligibility Rule: {scheme_id} - {clause}"
            official_url = source_meta.get("official_url") or ("https://scholarships.gov.in" if "SCH-" in scheme_id else "https://pmkisan.gov.in")
            dept = source_meta.get("issuing_authority") or "Government of India & Government of Karnataka"
            circular_no = source_meta.get("circular_number")

            rule_text = (
                f"Official Rule under {clause}: {desc} "
                f"{('Administrative guidance: ' + guidance) if guidance else ''}"
            )

            chunks.extend(
                self.chunker.chunk_section(
                    text=rule_text,
                    document_title=doc_title,
                    section_or_clause=clause,
                    official_source_url=official_url,
                    government_department=dept,
                    page_number=page,
                    scheme_id=scheme_id,
                    applicable_cycle=cycle,
                    base_chunk_id=f"CHK-{r_id}",
                    extra_metadata={
                        "rule_type": rule.get("rule_type", ""),
                        "source_id": source_id,
                        "circular_number": circular_no,
                    },
                )
            )

        return chunks

    def extract_text_from_pdf(self, pdf_path: Path) -> List[Dict[str, Any]]:
        """Extracts text page by page from an uploaded PDF using PyMuPDF (fitz)."""
        if not PYMUPDF_AVAILABLE:
            logger.warning("PyMuPDF (fitz) is not installed. PDF text extraction unavailable.")
            return []

        pages: List[Dict[str, Any]] = []
        try:
            doc = fitz.open(pdf_path)
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text")
                pages.append({
                    "page_number": str(page_num + 1),
                    "text": text,
                })
            doc.close()
        except Exception as e:
            logger.error(f"Error reading PDF {pdf_path}: {e}")

        return pages

    def ingest_pdf_document(
        self,
        pdf_path: Path,
        document_title: str,
        government_department: str,
        official_source_url: str,
        scheme_id: Optional[str] = None,
        applicable_cycle: str = "2024-25",
    ) -> List[DocumentChunk]:
        """Ingests an authoritative government PDF, extracting pages and chunking section-aware."""
        pages = self.extract_text_from_pdf(pdf_path)
        chunks: List[DocumentChunk] = []

        doc_base = Path(pdf_path).stem.upper().replace(" ", "_")[:12]

        for p in pages:
            page_text = p.get("text", "")
            page_no = p.get("page_number", "1")

            page_chunks = self.chunker.chunk_section(
                text=page_text,
                document_title=document_title,
                section_or_clause=f"Gazette Page {page_no}",
                official_source_url=official_source_url,
                government_department=government_department,
                page_number=page_no,
                scheme_id=scheme_id,
                applicable_cycle=applicable_cycle,
                base_chunk_id=f"CHK-PDF-{doc_base}-P{page_no}",
                extra_metadata={"source_file": pdf_path.name},
            )
            chunks.extend(page_chunks)

        return chunks

    def build_initial_knowledge_base(self, seeds_dir: Path) -> List[DocumentChunk]:
        """Ingests all official knowledge base seeds into a unified collection of evidence chunks."""
        all_chunks: List[DocumentChunk] = []

        # 1. Circulars
        circ_path = seeds_dir / "policy_circulars.json"
        all_chunks.extend(self.ingest_seed_circulars(circ_path))

        # 2. Government Schemes
        schemes_path = seeds_dir / "government_schemes.json"
        all_chunks.extend(self.ingest_seed_schemes(schemes_path))

        # 3. Scholarships
        sch_path = seeds_dir / "scholarships.json"
        all_chunks.extend(self.ingest_seed_scholarships(sch_path))

        # 4. Eligibility Rules
        rules_path = seeds_dir / "eligibility_rules.json"
        all_chunks.extend(self.ingest_seed_rules(rules_path))

        logger.info(f"Ingested {len(all_chunks)} verified evidence chunks into SchemeSathi knowledge base.")
        return all_chunks
