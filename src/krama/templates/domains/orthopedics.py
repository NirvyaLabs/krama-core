"""Orthopedics clinical templates."""

from krama.templates.base import ClinicalTemplate, TemplateSection


TEMPLATES = [
    ClinicalTemplate(
        domain="orthopedics",
        encounter_type="msk_exam",
        name="Orthopedic MSK Examination",
        description="Musculoskeletal exam with ROM, special tests, and imaging review.",
        sections=[
            TemplateSection(
                id="chief_complaint",
                label="Chief Complaint",
                type="text",
                required=True,
            ),
            TemplateSection(
                id="injury_mechanism",
                label="Mechanism of Injury",
                type="textarea",
            ),
            TemplateSection(
                id="inspection_palpation",
                label="Inspection and Palpation",
                type="textarea",
            ),
            TemplateSection(
                id="range_of_motion",
                label="Range of Motion (ROM)",
                type="textarea",
                required=True,
            ),
            TemplateSection(
                id="special_tests",
                label="Special Tests",
                type="checklist",
                items=[
                    "Lachman",
                    "McMurray",
                    "Anterior drawer",
                    "Straight leg raise",
                    "FABER",
                    "Neer",
                    "Hawkins",
                ],
            ),
            TemplateSection(
                id="imaging_review",
                label="Imaging Review",
                type="imaging_review",
            ),
            TemplateSection(
                id="diagnosis_plan",
                label="Diagnosis and Plan",
                type="textarea",
                icd_coding=True,
                rx_link=True,
            ),
        ],
        vitals=["bp", "weight"],
        coding_system="icd10",
        prescription_type="standard",
    )
]
