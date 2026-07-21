"""Dermatology clinical templates."""

from krama.templates.base import ClinicalTemplate, TemplateSection


TEMPLATES = [
    ClinicalTemplate(
        domain="dermatology",
        encounter_type="skin_exam",
        name="Dermatology Skin Examination",
        description="Skin exam covering lesion morphology, distribution, and treatment plan.",
        sections=[
            TemplateSection(
                id="chief_complaint",
                label="Chief Complaint",
                type="text",
                required=True,
            ),
            TemplateSection(
                id="lesion_description",
                label="Lesion Description",
                type="textarea",
                required=True,
            ),
            TemplateSection(
                id="distribution",
                label="Distribution",
                type="textarea",
            ),
            TemplateSection(
                id="morphology",
                label="Morphology",
                type="checklist",
                items=[
                    "Macule",
                    "Papule",
                    "Plaque",
                    "Vesicle",
                    "Pustule",
                    "Scale",
                    "Crust",
                    "Ulcer",
                ],
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
        vitals=[],
        coding_system="icd10",
        prescription_type="standard",
    )
]
