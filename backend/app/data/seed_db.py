import json
import logging
from pathlib import Path
from sqlalchemy.orm import Session

from app.database import SessionLocal, init_db
from app.schemas.rule import EligibilityRuleCreate, RequirementCreate
from app.schemas.scholarship import ScholarshipCreate
from app.schemas.scheme import GovernmentSchemeCreate
from app.schemas.source import OfficialSourceCreate
from app.services.opportunity_service import OpportunityService

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("seed_db")

SEEDS_DIR = Path(__file__).resolve().parent / "seeds"


def load_json(filename: str):
    file_path = SEEDS_DIR / filename
    if not file_path.exists():
        logger.warning(f"Seed file '{filename}' not found at {file_path}")
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def seed_database(db: Session = None):
    """Seed SQLite database with verified official sources, schemes, scholarships, rules, and requirements."""
    logger.info("Initializing database tables...")
    init_db()

    should_close = False
    if db is None:
        db = SessionLocal()
        should_close = True

    try:
        service = OpportunityService(db)

        # 1. Seed Official Sources
        sources_data = load_json("official_sources.json")
        logger.info(f"Loading {len(sources_data)} official sources...")
        for item in sources_data:
            existing = service.source_repo.get_by_id(item["id"])
            if not existing:
                service.create_source(OfficialSourceCreate(**item))
                logger.info(f"  + Added source: {item['id']} ({item['circular_number']})")
            else:
                logger.info(f"  = Source already exists: {item['id']}")

        # 2. Seed Scholarships
        scholarships_data = load_json("scholarships.json")
        logger.info(f"Loading {len(scholarships_data)} scholarships...")
        for item in scholarships_data:
            existing = service.scholarship_repo.get_by_id(item["id"])
            if not existing:
                service.create_scholarship(ScholarshipCreate(**item))
                logger.info(f"  + Added scholarship: {item['id']} ({item['official_name']})")
            else:
                logger.info(f"  = Scholarship already exists: {item['id']}")

        # 3. Seed Government Schemes
        schemes_data = load_json("government_schemes.json")
        logger.info(f"Loading {len(schemes_data)} government schemes...")
        for item in schemes_data:
            existing = service.scheme_repo.get_by_id(item["id"])
            if not existing:
                service.create_scheme(GovernmentSchemeCreate(**item))
                logger.info(f"  + Added scheme: {item['id']} ({item['official_name']})")
            else:
                logger.info(f"  = Scheme already exists: {item['id']}")

        # 4. Seed Eligibility Rules
        rules_data = load_json("eligibility_rules.json")
        logger.info(f"Loading {len(rules_data)} eligibility rules...")
        for item in rules_data:
            existing = service.rule_repo.get_by_id(item["id"])
            if not existing:
                service.create_rule(EligibilityRuleCreate(**item))
                logger.info(f"  + Added rule: {item['id']} ({item['rule_type']})")
            else:
                logger.info(f"  = Rule already exists: {item['id']}")

        # 5. Seed Requirements
        requirements_data = load_json("requirements.json")
        logger.info(f"Loading {len(requirements_data)} requirements...")
        for item in requirements_data:
            existing = service.requirement_repo.get_by_id(item["id"])
            if not existing:
                service.create_requirement(RequirementCreate(**item))
                logger.info(f"  + Added requirement: {item['id']} ({item['title']})")
            else:
                logger.info(f"  = Requirement already exists: {item['id']}")

        logger.info("Database seeding completed successfully.")
        return {
            "sources": len(sources_data),
            "scholarships": len(scholarships_data),
            "schemes": len(schemes_data),
            "rules": len(rules_data),
            "requirements": len(requirements_data),
        }

    finally:
        if should_close:
            db.close()


if __name__ == "__main__":
    seed_database()
