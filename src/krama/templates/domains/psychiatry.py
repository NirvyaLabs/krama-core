"""Psychiatry clinical templates."""

from krama.templates.base import ClinicalTemplate, TemplateSection

TEMPLATES = [
    ClinicalTemplate(
        domain="psychiatry",
        encounter_type="mental_status_exam",
        name="Psychiatry Mental Status Exam",
        description="Mental Status Exam with risk assessment and treatment planning.",
        sections=[
            TemplateSection(
                id="presenting_concern",
                label="Presenting Concern",
                type="text",
                required=True,
                ai_assist=True,
            ),
            TemplateSection(
                id="history_psychiatric",
                label="Psychiatric History",
                type="textarea",
            ),
            TemplateSection(
                id="mental_status_exam",
                label="Mental Status Examination (MSE)",
                type="checklist",
                required=True,
                items=[
                    "Appearance and behavior",
                    "Speech",
                    "Mood and affect",
                    "Thought form",
                    "Thought content",
                    "Perception",
                    "Cognition",
                    "Insight and judgment",
                ],
            ),
            TemplateSection(
                id="risk_assessment",
                label="Risk Assessment",
                type="textarea",
                required=True,
            ),
            TemplateSection(
                id="diagnosis",
                label="Diagnosis",
                type="textarea",
                icd_coding=True,
            ),
            TemplateSection(
                id="treatment_plan",
                label="Treatment Plan",
                type="textarea",
                rx_link=True,
            ),
        ],
        vitals=["bp", "heart_rate", "weight"],
        coding_system="icd10",
        prescription_type="standard",
    )
]
