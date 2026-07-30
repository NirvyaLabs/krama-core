"""Surgery clinical templates."""

from krama.templates.base import ClinicalTemplate, TemplateSection

TEMPLATES = [
    ClinicalTemplate(
        domain="surgery",
        encounter_type="pre_op_assessment",
        name="Pre-operative Assessment",
        description="Pre-op risk assessment, consent, and surgical readiness.",
        sections=[
            TemplateSection(
                id="planned_procedure",
                label="Planned Procedure",
                type="text",
                required=True,
                icd_coding=True,
            ),
            TemplateSection(
                id="indication",
                label="Indication for Surgery",
                type="textarea",
                required=True,
            ),
            TemplateSection(
                id="asa_class",
                label="ASA Physical Status",
                type="select",
                options=["I", "II", "III", "IV", "V", "VI"],
            ),
            TemplateSection(
                id="anesthesia_plan",
                label="Anesthesia Plan",
                type="textarea",
            ),
            TemplateSection(
                id="consent_checklist",
                label="Consent and Safety Checklist",
                type="checklist",
                items=[
                    "Procedure explained",
                    "Risks discussed",
                    "Blood consent reviewed",
                    "Site marked",
                    "NPO status confirmed",
                ],
            ),
        ],
        vitals=["bp", "heart_rate", "temperature", "weight", "spo2"],
        coding_system="icd10",
        prescription_type="standard",
    ),
    ClinicalTemplate(
        domain="surgery",
        encounter_type="operative_note",
        name="Operative Note",
        description="Intra-operative documentation and procedure details.",
        sections=[
            TemplateSection(
                id="procedure_performed",
                label="Procedure Performed",
                type="procedure_list",
                required=True,
            ),
            TemplateSection(
                id="operative_findings",
                label="Operative Findings",
                type="textarea",
                required=True,
            ),
            TemplateSection(
                id="anesthesia_used",
                label="Anesthesia Used",
                type="text",
            ),
            TemplateSection(
                id="blood_loss",
                label="Estimated Blood Loss",
                type="text",
            ),
            TemplateSection(
                id="complications",
                label="Complications",
                type="textarea",
            ),
            TemplateSection(
                id="post_op_orders",
                label="Post-operative Orders",
                type="textarea",
                rx_link=True,
            ),
        ],
        vitals=["bp", "heart_rate", "spo2"],
        coding_system="icd10",
        prescription_type="standard",
    ),
    ClinicalTemplate(
        domain="surgery",
        encounter_type="post_op_followup",
        name="Post-operative Follow-up",
        description="Wound review, recovery status, and post-op plan.",
        sections=[
            TemplateSection(
                id="post_op_day",
                label="Post-operative Day",
                type="number",
                required=True,
            ),
            TemplateSection(
                id="wound_assessment",
                label="Wound Assessment",
                type="textarea",
                required=True,
            ),
            TemplateSection(
                id="pain_score",
                label="Pain Score",
                type="number",
            ),
            TemplateSection(
                id="mobility",
                label="Mobility and Diet",
                type="textarea",
            ),
            TemplateSection(
                id="followup_plan",
                label="Follow-up Plan",
                type="textarea",
                rx_link=True,
            ),
        ],
        vitals=["bp", "heart_rate", "temperature", "spo2"],
        coding_system="icd10",
        prescription_type="standard",
    ),
]
