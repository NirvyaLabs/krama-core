"""General medicine clinical templates."""

from krama.templates.base import ClinicalTemplate, TemplateSection

TEMPLATES = [
    ClinicalTemplate(
        domain="allopathy",
        encounter_type="general_opd",
        name="General OPD Consultation",
        description="Standard SOAP note for outpatient allopathic consultation.",
        sections=[
            TemplateSection(
                id="chief_complaint",
                label="Chief Complaint",
                type="text",
                required=True,
                ai_assist=True,
            ),
            TemplateSection(
                id="subjective",
                label="Subjective",
                type="textarea",
                ai_assist=True,
            ),
            TemplateSection(
                id="objective",
                label="Objective",
                type="textarea",
                ai_assist=True,
            ),
            TemplateSection(
                id="assessment",
                label="Assessment",
                type="textarea",
                required=True,
                ai_assist=True,
                icd_coding=True,
            ),
            TemplateSection(
                id="plan",
                label="Plan",
                type="textarea",
                ai_assist=True,
                rx_link=True,
            ),
        ],
        vitals=["bp", "heart_rate", "temperature", "weight", "spo2", "respiratory_rate"],
        coding_system="icd10",
        prescription_type="standard",
    )
]
