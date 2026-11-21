from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional, Tuple, Union

from app.models.rule import EligibilityRule, Requirement
from app.models.scholarship import Scholarship
from app.models.scheme import GovernmentScheme
from app.schemas.common import EligibilityEvaluationStatus
from app.schemas.eligibility import (
    CitizenEvaluationInput,
    RuleAssessmentItem,
    ScholarReadyEvaluationSummary,
    ScholarshipEvaluationResult,
    SchemeDiscoverySummary,
    SchemeEvaluationResult,
    SensitiveFieldExplanation,
    StudentEvaluationInput,
)

logger = logging.getLogger("rule_engine")


class DeterministicRuleEngine:
    """Pure Python deterministic rule evaluation engine for SchemeSathi AI.
    
    Guarantees:
    - Never uses an LLM to compute eligibility.
    - Deterministic execution of structured AST conditions.
    - Explicit handling of MISSING_INFORMATION vs DOES_NOT_MEET_REQUIREMENT vs NEEDS_REVIEW.
    - Full traceability linking each decision to official circulars and clauses.
    """

    # Sensitive fields catalog explaining legally mandated data collection
    SENSITIVE_FIELDS_EXPLANATIONS = [
        SensitiveFieldExplanation(
            field_name="is_income_tax_payer",
            display_name="Income Tax Payer Status",
            required_by_scheme_id="SCHEME-PM-KISAN",
            scheme_name="Pradhan Mantri Kisan Samman Nidhi (PM-KISAN) & Karnataka Gruha Lakshmi",
            official_clause="Clause 5(b)(vi) of PM-KISAN Operational Guidelines & Clause 4 of Karnataka GO-WCD-41-WES-2023",
            explanation="Both Central and State welfare rules strictly exclude individuals or families who paid income tax or filed GST returns in the preceding assessment year from direct income support benefits.",
        ),
        SensitiveFieldExplanation(
            field_name="landholding_hectares",
            display_name="Cultivable Landholding (Hectares)",
            required_by_scheme_id="SCHEME-PM-KISAN",
            scheme_name="Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
            official_clause="Clause 3.1 (Beneficiary Definition)",
            explanation="Agricultural income support under PM-KISAN is legally tied to verified land titles registered in state land revenue records (e.g. Bhoomi portal in Karnataka, Bhulekh in UP).",
        ),
        SensitiveFieldExplanation(
            field_name="bpl_card_holder",
            display_name="Ration Card / BPL Classification",
            required_by_scheme_id="SCHEME-KAR-GRUHA-LAKSHMI",
            scheme_name="Karnataka Gruha Lakshmi Scheme",
            official_clause="Clause 2 & 3 (Jurisdiction & Eligibility)",
            explanation="Gruha Lakshmi financial assistance is distributed exclusively to the recognized woman head of the household (Yajamani) specified on Antyodaya, BPL, or APL ration cards in Karnataka.",
        ),
    ]

    # Field aliases mapping common profile keys
    FIELD_ALIASES = {
        "income": "annual_family_income",
        "family_income": "annual_family_income",
        "parental_income": "annual_family_income",
        "annual_income": "annual_family_income",
        "marks": "marks_percentage",
        "percentage": "marks_percentage",
        "percentile": "marks_percentage",
        "state": "domicile_state",
        "domicile": "domicile_state",
        "caste": "category",
        "social_category": "category",
        "course": "course_level",
        "sex": "gender",
        "other_scholarship": "other_scholarship_recipient",
        "daughters_count": "eligible_daughters_count",
        "land": "landholding_hectares",
        "landholding": "landholding_hectares",
        "farmland": "landholding_hectares",
        "tax_payer": "is_income_tax_payer",
        "income_tax": "is_income_tax_payer",
        "it_payer": "is_income_tax_payer",
        "bpl": "bpl_card_holder",
        "ration_card": "bpl_card_holder",
        "residence_type": "area_type",
        "area": "area_type",
    }

    @classmethod
    def resolve_field_value(cls, profile_data: Dict[str, Any], field_name: str) -> Tuple[bool, Any]:
        """Resolves field value from profile dictionary considering aliases and extra_attributes.
        Returns: (exists: bool, value: Any)
        """
        # 1. Direct lookup
        if field_name in profile_data and profile_data[field_name] is not None:
            return True, profile_data[field_name]

        # 2. Alias lookup
        for alias, target in cls.FIELD_ALIASES.items():
            if target == field_name and alias in profile_data and profile_data[alias] is not None:
                return True, profile_data[alias]
            if alias == field_name and target in profile_data and profile_data[target] is not None:
                return True, profile_data[target]

        # 3. Extra attributes dictionary lookup
        extra = profile_data.get("extra_attributes") or {}
        if isinstance(extra, dict) and field_name in extra and extra[field_name] is not None:
            return True, extra[field_name]

        return False, None

    @classmethod
    def check_contradictory_value(cls, field_name: str, value: Any) -> Tuple[bool, Optional[str]]:
        """Identifies contradictory, impossible or malformed profile inputs requiring manual review."""
        if value is None:
            return False, None

        # Negative income
        if field_name in ("annual_family_income", "income") and isinstance(value, (int, float)):
            if value < 0:
                return True, f"Annual family income cannot be negative (provided: ₹{value:,})."

        # Negative or impossible landholding
        if field_name in ("landholding_hectares", "landholding", "farmland") and isinstance(value, (int, float)):
            if value < 0:
                return True, f"Cultivable landholding cannot be negative (provided: {value} hectares)."
            if value > 500:
                return True, f"Unusually large landholding ({value} hectares). Requires manual revenue record review."

        # Out-of-bounds percentage
        if field_name in ("marks_percentage", "marks", "percentage") and isinstance(value, (int, float)):
            if value < 0 or value > 100:
                return True, f"Academic marks percentage must be between 0 and 100% (provided: {value}%)."

        # Out-of-bounds age
        if field_name == "age" and isinstance(value, (int, float)):
            if value < 1 or value > 120:
                return True, f"Age '{value}' is outside realistic operational parameters (1 to 120 years)."

        return False, None

    @classmethod
    def evaluate_condition(
        cls,
        operator: str,
        user_value: Any,
        target_value: Any,
    ) -> bool:
        """Deterministic operator evaluation."""
        op = operator.upper().strip()

        # Numeric comparisons
        if op in ("LTE", "LE"):
            return float(user_value) <= float(target_value)
        if op in ("GTE", "GE"):
            return float(user_value) >= float(target_value)
        if op in ("LT", "<"):
            return float(user_value) < float(target_value)
        if op in ("GT", ">"):
            return float(user_value) > float(target_value)

        # Equality
        if op in ("EQ", "EQUALS", "=="):
            if isinstance(user_value, str) and isinstance(target_value, str):
                return user_value.strip().lower() == target_value.strip().lower()
            if isinstance(user_value, bool) and isinstance(target_value, bool):
                return user_value == target_value
            return user_value == target_value

        # Inequality
        if op in ("NEQ", "NOT_EQUALS", "!="):
            if isinstance(user_value, str) and isinstance(target_value, str):
                return user_value.strip().lower() != target_value.strip().lower()
            return user_value != target_value

        # Collection membership (IN / NOT_IN)
        if op in ("IN", "IN_LIST"):
            if isinstance(target_value, list):
                if isinstance(user_value, str):
                    normalized_targets = [str(x).strip().lower() for x in target_value]
                    return user_value.strip().lower() in normalized_targets
                return user_value in target_value
            return False

        if op in ("NOT_IN", "NOT_IN_LIST"):
            if isinstance(target_value, list):
                if isinstance(user_value, str):
                    normalized_targets = [str(x).strip().lower() for x in target_value]
                    return user_value.strip().lower() not in normalized_targets
                return user_value not in target_value
            return True

        # String / Text Substring (CONTAINS)
        if op in ("CONTAINS", "SUBSTRING"):
            if user_value is None or target_value is None:
                return False
            return str(target_value).strip().lower() in str(user_value).strip().lower()

        logger.warning(f"Unrecognized operator '{operator}'. Defaulting to False.")
        return False

    @classmethod
    def evaluate_rule(
        cls,
        rule: EligibilityRule,
        profile_data: Dict[str, Any],
    ) -> RuleAssessmentItem:
        """Evaluates a single structured rule against user profile data."""
        cond = rule.structured_condition or {}
        field = cond.get("field", "")
        operator = cond.get("operator", "EQ")
        target_value = cond.get("value")

        # Source metadata defaults
        source_title = rule.source.source_title if rule.source else "Official Government Order"
        circular_no = rule.source.circular_number if rule.source else "Gazette Notification"
        source_url = rule.source.official_url if rule.source else "https://scholarships.gov.in"

        # 1. Check if user provided the required field
        field_exists, user_val = cls.resolve_field_value(profile_data, field)

        if not field_exists:
            return RuleAssessmentItem(
                rule_id=rule.id,
                requirement_description=rule.requirement_description,
                rule_type=rule.rule_type,
                official_condition=cond,
                user_provided_value=None,
                status=EligibilityEvaluationStatus.MISSING_INFORMATION,
                is_mandatory=rule.is_mandatory,
                explanation=f"Missing input: '{field}' is required to evaluate: {rule.requirement_description}",
                official_source_title=source_title,
                circular_number=circular_no,
                clause_or_section=rule.clause_or_section,
                page_number=rule.page_number,
                official_source_url=source_url,
            )

        # 2. Check for contradictory or out-of-bounds user values
        is_contradictory, review_reason = cls.check_contradictory_value(field, user_val)
        if is_contradictory:
            return RuleAssessmentItem(
                rule_id=rule.id,
                requirement_description=rule.requirement_description,
                rule_type=rule.rule_type,
                official_condition=cond,
                user_provided_value=user_val,
                status=EligibilityEvaluationStatus.NEEDS_REVIEW,
                is_mandatory=rule.is_mandatory,
                explanation=f"Review required: {review_reason}",
                official_source_title=source_title,
                circular_number=circular_no,
                clause_or_section=rule.clause_or_section,
                page_number=rule.page_number,
                official_source_url=source_url,
            )

        # 3. Deterministic operator evaluation
        try:
            meets = cls.evaluate_condition(operator, user_val, target_value)
        except Exception as e:
            logger.error(f"Error evaluating condition {cond} with user_value '{user_val}': {e}")
            return RuleAssessmentItem(
                rule_id=rule.id,
                requirement_description=rule.requirement_description,
                rule_type=rule.rule_type,
                official_condition=cond,
                user_provided_value=user_val,
                status=EligibilityEvaluationStatus.NEEDS_REVIEW,
                is_mandatory=rule.is_mandatory,
                explanation=f"Could not compute comparison: {e}. Administrative review recommended.",
                official_source_title=source_title,
                circular_number=circular_no,
                clause_or_section=rule.clause_or_section,
                page_number=rule.page_number,
                official_source_url=source_url,
            )

        if meets:
            status = EligibilityEvaluationStatus.MEETS_REQUIREMENT
            explanation = (
                f"Meets Requirement: Applicant value '{user_val}' satisfies official condition "
                f"({field} {operator} {target_value}) under {rule.clause_or_section}."
            )
        else:
            status = EligibilityEvaluationStatus.DOES_NOT_MEET_REQUIREMENT
            guidance = f" Note: {rule.failure_guidance}" if rule.failure_guidance else ""
            explanation = (
                f"Does Not Meet: Applicant value '{user_val}' does not satisfy official condition "
                f"({field} {operator} {target_value}).{guidance}"
            )

        return RuleAssessmentItem(
            rule_id=rule.id,
            requirement_description=rule.requirement_description,
            rule_type=rule.rule_type,
            official_condition=cond,
            user_provided_value=user_val,
            status=status,
            is_mandatory=rule.is_mandatory,
            explanation=explanation,
            official_source_title=source_title,
            circular_number=circular_no,
            clause_or_section=rule.clause_or_section,
            page_number=rule.page_number,
            official_source_url=source_url,
        )

    @classmethod
    def evaluate_scholarship(
        cls,
        scholarship: Scholarship,
        profile_input: Union[StudentEvaluationInput, Dict[str, Any]],
    ) -> ScholarshipEvaluationResult:
        """Evaluates all rules of a scholarship against student profile inputs."""
        profile_data = (
            profile_input.model_dump(exclude_unset=False)
            if isinstance(profile_input, StudentEvaluationInput)
            else dict(profile_input)
        )

        rules = scholarship.eligibility_rules or []
        satisfied: List[RuleAssessmentItem] = []
        failed: List[RuleAssessmentItem] = []
        missing: List[RuleAssessmentItem] = []
        under_review: List[RuleAssessmentItem] = []

        for rule in rules:
            item = cls.evaluate_rule(rule, profile_data)
            if item.status == EligibilityEvaluationStatus.MEETS_REQUIREMENT:
                satisfied.append(item)
            elif item.status == EligibilityEvaluationStatus.DOES_NOT_MEET_REQUIREMENT:
                failed.append(item)
            elif item.status == EligibilityEvaluationStatus.MISSING_INFORMATION:
                missing.append(item)
            elif item.status == EligibilityEvaluationStatus.NEEDS_REVIEW:
                under_review.append(item)

        total_rules = len(rules)
        if total_rules > 0:
            match_score = round((len(satisfied) / total_rules) * 100.0, 1)
        else:
            match_score = 0.0

        # Overall Status Determination
        # If any mandatory rule failed -> DOES_NOT_MEET_REQUIREMENT
        # Else if any mandatory rule missing -> MISSING_INFORMATION
        # Else if any rule needs review -> NEEDS_REVIEW
        # Else -> MEETS_REQUIREMENT
        mandatory_failed = any(item.is_mandatory for item in failed)
        mandatory_missing = any(item.is_mandatory for item in missing)
        any_review = len(under_review) > 0

        if mandatory_failed:
            overall_status = EligibilityEvaluationStatus.DOES_NOT_MEET_REQUIREMENT
        elif mandatory_missing:
            overall_status = EligibilityEvaluationStatus.MISSING_INFORMATION
        elif any_review:
            overall_status = EligibilityEvaluationStatus.NEEDS_REVIEW
        else:
            overall_status = EligibilityEvaluationStatus.MEETS_REQUIREMENT

        # Synthesize actionable next steps
        suggested_actions = cls.generate_actionable_guidance(
            overall_status, satisfied, failed, missing, under_review, scholarship
        )

        # Formulate document requirement cards
        required_docs = [
            {
                "id": req.id,
                "document_type": req.document_type,
                "title": req.title,
                "description": req.description,
                "issuing_authority": req.issuing_authority,
                "is_mandatory": req.is_mandatory,
            }
            for req in (scholarship.requirements or [])
        ]

        return ScholarshipEvaluationResult(
            scholarship_id=scholarship.id,
            official_name=scholarship.official_name,
            government_department=scholarship.government_department,
            benefit_amount_annual=scholarship.benefit_amount_annual,
            official_source_url=scholarship.official_source_url,
            application_url=scholarship.application_url,
            application_deadline=scholarship.application_deadline,
            overall_status=overall_status,
            match_score=match_score,
            requirements_satisfied=satisfied,
            requirements_not_satisfied=failed,
            missing_information=missing,
            conditions_under_review=under_review,
            suggested_next_actions=suggested_actions,
            required_documents=required_docs,
        )

    @classmethod
    def generate_actionable_guidance(
        cls,
        overall_status: EligibilityEvaluationStatus,
        satisfied: List[RuleAssessmentItem],
        failed: List[RuleAssessmentItem],
        missing: List[RuleAssessmentItem],
        under_review: List[RuleAssessmentItem],
        scholarship: Scholarship,
    ) -> List[str]:
        """Generates clear, civic-focused instructions based on evaluation outcome."""
        actions: List[str] = []

        if overall_status == EligibilityEvaluationStatus.MEETS_REQUIREMENT:
            actions.append(
                f"You meet all evaluated conditions for '{scholarship.official_name}'. Prepare your application."
            )
            actions.append(
                f"Verify your bank account is seeded with Aadhaar and active on the NPCI Direct Benefit Transfer mapper."
            )
            if scholarship.application_url:
                actions.append(f"Submit your official application before deadline on {scholarship.application_url}")

        elif overall_status == EligibilityEvaluationStatus.MISSING_INFORMATION:
            missing_fields = [item.official_condition.get("field", "information") for item in missing]
            fields_str = ", ".join(f"'{f}'" for f in missing_fields)
            actions.append(
                f"Complete your profile: Missing {fields_str} required to complete eligibility assessment."
            )
            actions.append(
                "Once you provide these details, the system will instantly calculate your final readiness status."
            )

        elif overall_status == EligibilityEvaluationStatus.DOES_NOT_MEET_REQUIREMENT:
            for item in failed:
                actions.append(f"Disqualification reason: {item.explanation}")
            actions.append(
                "Explore other scholarships in ScholarReady catalog matching your category or income profile."
            )

        elif overall_status == EligibilityEvaluationStatus.NEEDS_REVIEW:
            for item in under_review:
                actions.append(f"Manual verification needed: {item.explanation}")
            actions.append("Check that your profile values reflect your official certificates.")

        return actions

    @staticmethod
    def _extract_profile_name(profile_input: Any) -> Optional[str]:
        """Safely extracts full_name from Pydantic models, dicts, or other objects without raising AttributeError."""
        if isinstance(profile_input, dict):
            raw_name = profile_input.get("full_name")
        else:
            raw_name = getattr(profile_input, "full_name", None)

        if isinstance(raw_name, str):
            clean_name = raw_name.strip()
            return clean_name if clean_name else None
        return None

    @classmethod
    def evaluate_all_scholarships(
        cls,
        scholarships: List[Scholarship],
        profile_input: Union[StudentEvaluationInput, Dict[str, Any]],
    ) -> ScholarReadyEvaluationSummary:
        """Evaluates student profile across a collection of scholarships and generates prioritized summary."""
        results: List[ScholarshipEvaluationResult] = []

        for sch in scholarships:
            res = cls.evaluate_scholarship(sch, profile_input)
            results.append(res)

        # Sort: MEETS_REQUIREMENT first, then MISSING_INFORMATION (highest match_score), then NEEDS_REVIEW, then DOES_NOT_MEET
        priority_order = {
            EligibilityEvaluationStatus.MEETS_REQUIREMENT: 0,
            EligibilityEvaluationStatus.MISSING_INFORMATION: 1,
            EligibilityEvaluationStatus.NEEDS_REVIEW: 2,
            EligibilityEvaluationStatus.DOES_NOT_MEET_REQUIREMENT: 3,
        }
        results.sort(key=lambda x: (priority_order.get(x.overall_status, 4), -x.match_score))

        eligible = sum(1 for r in results if r.overall_status == EligibilityEvaluationStatus.MEETS_REQUIREMENT)
        missing = sum(1 for r in results if r.overall_status == EligibilityEvaluationStatus.MISSING_INFORMATION)
        ineligible = sum(1 for r in results if r.overall_status == EligibilityEvaluationStatus.DOES_NOT_MEET_REQUIREMENT)
        review = sum(1 for r in results if r.overall_status == EligibilityEvaluationStatus.NEEDS_REVIEW)

        student_name = cls._extract_profile_name(profile_input)

        return ScholarReadyEvaluationSummary(
            student_name=student_name,
            total_scholarships_evaluated=len(scholarships),
            eligible_count=eligible,
            missing_info_count=missing,
            ineligible_count=ineligible,
            under_review_count=review,
            scholarships=results,
            evaluated_at=datetime.now(timezone.utc).isoformat(),
        )

    # ============================================================================
    # SchemeSathi Scheme Discovery & Citizen Evaluation
    # ============================================================================

    @classmethod
    def get_sensitive_fields_explanation(cls) -> List[SensitiveFieldExplanation]:
        """Returns the official rationale and citations for sensitive profile questions."""
        return cls.SENSITIVE_FIELDS_EXPLANATIONS

    @classmethod
    def evaluate_scheme(
        cls,
        scheme: GovernmentScheme,
        profile_input: Union[CitizenEvaluationInput, Dict[str, Any]],
    ) -> SchemeEvaluationResult:
        """Evaluates all rules of a government scheme against citizen profile inputs."""
        profile_data = (
            profile_input.model_dump(exclude_unset=False)
            if isinstance(profile_input, CitizenEvaluationInput)
            else dict(profile_input)
        )

        rules = scheme.eligibility_rules or []
        satisfied: List[RuleAssessmentItem] = []
        failed: List[RuleAssessmentItem] = []
        missing: List[RuleAssessmentItem] = []
        under_review: List[RuleAssessmentItem] = []

        for rule in rules:
            item = cls.evaluate_rule(rule, profile_data)
            if item.status == EligibilityEvaluationStatus.MEETS_REQUIREMENT:
                satisfied.append(item)
            elif item.status == EligibilityEvaluationStatus.DOES_NOT_MEET_REQUIREMENT:
                failed.append(item)
            elif item.status == EligibilityEvaluationStatus.MISSING_INFORMATION:
                missing.append(item)
            elif item.status == EligibilityEvaluationStatus.NEEDS_REVIEW:
                under_review.append(item)

        total_rules = len(rules)
        if total_rules > 0:
            match_score = round((len(satisfied) / total_rules) * 100.0, 1)
        else:
            match_score = 0.0

        # Overall Status Determination
        mandatory_failed = any(item.is_mandatory for item in failed)
        mandatory_missing = any(item.is_mandatory for item in missing)
        any_review = len(under_review) > 0

        if mandatory_failed:
            overall_status = EligibilityEvaluationStatus.DOES_NOT_MEET_REQUIREMENT
        elif mandatory_missing:
            overall_status = EligibilityEvaluationStatus.MISSING_INFORMATION
        elif any_review:
            overall_status = EligibilityEvaluationStatus.NEEDS_REVIEW
        else:
            overall_status = EligibilityEvaluationStatus.MEETS_REQUIREMENT

        # Guidance
        suggested_actions = cls.generate_scheme_actionable_guidance(
            overall_status, satisfied, failed, missing, under_review, scheme
        )

        # Important conditions summary
        important_conditions = [rule.requirement_description for rule in rules]

        # Formulate required documents
        required_docs = [
            {
                "id": req.id,
                "document_type": req.document_type,
                "title": req.title,
                "description": req.description,
                "issuing_authority": req.issuing_authority,
                "is_mandatory": req.is_mandatory,
            }
            for req in (scheme.requirements or [])
        ]

        source_title = scheme.official_source.source_title if scheme.official_source else None
        circular_no = scheme.official_source.circular_number if scheme.official_source else None

        return SchemeEvaluationResult(
            scheme_id=scheme.id,
            official_name=scheme.official_name,
            category=scheme.category,
            government_department=scheme.government_department,
            level=scheme.level,
            benefit_type=scheme.benefit_type,
            annual_benefit=scheme.annual_benefit,
            target_beneficiaries=scheme.target_beneficiaries,
            application_deadline=scheme.application_deadline,
            official_source_url=scheme.official_source_url,
            application_url=scheme.application_url,
            verification_date=scheme.verification_date.isoformat() if scheme.verification_date else "",
            policy_cycle=scheme.policy_cycle,
            information_status=scheme.information_status,
            overall_status=overall_status,
            match_score=match_score,
            requirements_satisfied=satisfied,
            requirements_not_satisfied=failed,
            missing_information=missing,
            conditions_under_review=under_review,
            suggested_next_actions=suggested_actions,
            important_conditions=important_conditions,
            required_documents=required_docs,
            official_source_title=source_title,
            circular_number=circular_no,
        )

    @classmethod
    def generate_scheme_actionable_guidance(
        cls,
        overall_status: EligibilityEvaluationStatus,
        satisfied: List[RuleAssessmentItem],
        failed: List[RuleAssessmentItem],
        missing: List[RuleAssessmentItem],
        under_review: List[RuleAssessmentItem],
        scheme: GovernmentScheme,
    ) -> List[str]:
        """Generates clear, civic-focused instructions for citizens based on evaluation outcome."""
        actions: List[str] = []

        if overall_status == EligibilityEvaluationStatus.MEETS_REQUIREMENT:
            actions.append(
                f"You meet all verified statutory eligibility conditions for '{scheme.official_name}'."
            )
            actions.append(
                "Ensure your bank account is active on the NPCI Aadhaar Direct Benefit Transfer (DBT) payment gateway."
            )
            if scheme.application_url:
                actions.append(
                    f"Proceed to submit your registration on the verified official portal: {scheme.application_url}"
                )

        elif overall_status == EligibilityEvaluationStatus.MISSING_INFORMATION:
            missing_fields = [item.official_condition.get("field", "information") for item in missing]
            fields_str = ", ".join(f"'{f}'" for f in missing_fields)
            actions.append(
                f"Incomplete profile: Missing {fields_str} needed to determine legal entitlement for this scheme."
            )
            actions.append(
                "Provide the missing details in your profile to complete automatic eligibility evaluation."
            )

        elif overall_status == EligibilityEvaluationStatus.DOES_NOT_MEET_REQUIREMENT:
            for item in failed:
                actions.append(f"Statutory Ineligibility: {item.explanation}")
            actions.append(
                "Check other categories in SchemeSathi matching your occupation or household profile."
            )

        elif overall_status == EligibilityEvaluationStatus.NEEDS_REVIEW:
            for item in under_review:
                actions.append(f"Administrative review required: {item.explanation}")
            actions.append(
                "Review your submitted profile entries against your official government certificates and revenue records."
            )

        return actions

    @classmethod
    def evaluate_all_schemes(
        cls,
        schemes: List[GovernmentScheme],
        profile_input: Union[CitizenEvaluationInput, Dict[str, Any]],
    ) -> SchemeDiscoverySummary:
        """Evaluates citizen profile across all provided government schemes and ranks matches."""
        results: List[SchemeEvaluationResult] = []

        for sch in schemes:
            res = cls.evaluate_scheme(sch, profile_input)
            results.append(res)

        # Priority ranking: MEETS_REQUIREMENT first, then MISSING_INFORMATION, then NEEDS_REVIEW, then DOES_NOT_MEET
        priority_order = {
            EligibilityEvaluationStatus.MEETS_REQUIREMENT: 0,
            EligibilityEvaluationStatus.MISSING_INFORMATION: 1,
            EligibilityEvaluationStatus.NEEDS_REVIEW: 2,
            EligibilityEvaluationStatus.DOES_NOT_MEET_REQUIREMENT: 3,
        }
        results.sort(key=lambda x: (priority_order.get(x.overall_status, 4), -x.match_score))

        eligible = sum(1 for r in results if r.overall_status == EligibilityEvaluationStatus.MEETS_REQUIREMENT)
        missing = sum(1 for r in results if r.overall_status == EligibilityEvaluationStatus.MISSING_INFORMATION)
        ineligible = sum(1 for r in results if r.overall_status == EligibilityEvaluationStatus.DOES_NOT_MEET_REQUIREMENT)
        review = sum(1 for r in results if r.overall_status == EligibilityEvaluationStatus.NEEDS_REVIEW)

        citizen_name = cls._extract_profile_name(profile_input)

        return SchemeDiscoverySummary(
            citizen_name=citizen_name,
            total_schemes_evaluated=len(schemes),
            eligible_count=eligible,
            missing_info_count=missing,
            ineligible_count=ineligible,
            under_review_count=review,
            schemes=results,
            evaluated_at=datetime.now(timezone.utc).isoformat(),
        )
