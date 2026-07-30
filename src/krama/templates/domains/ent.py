"""ENT clinical templates."""

from krama.templates.base import ClinicalTemplate, TemplateSection

TEMPLATES = [
    ClinicalTemplate(
        domain="ent",
        encounter_type="ent_exam",
        name="ENT Examination",
        description="Ear, nose, and throat exam with audiometry and endoscopy findings.",
        sections=[
            TemplateSection(
                id="chief_complaint",
                label="Chief Complaint",
                type="text",
                required=True,
            ),
            TemplateSection(
                id="ear_exam",
                label="Ear Examination",
                type="textarea",
            ),
            TemplateSection(
                id="nose_exam",
                label="Nose Examination",
                type="textarea",
            ),
            TemplateSection(
                id="throat_exam",
                label="Throat Examination",
                type="textarea",
            ),
            TemplateSection(
                id="audiometry",
                label="Audiometry Findings",
                type="textarea",
            ),
            TemplateSection(
                id="endoscopy_findings",
                label="Endoscopy Findings",
                type="textarea",
            ),
            TemplateSection(
                id="diagnosis_plan",
                label="Diagnosis and Plan",
                type="textarea",
                icd_coding=True,
                rx_link=True,
            ),
        ],
        vitals=["temperature"],
        coding_system="icd10",
        prescription_type="standard",
    )
]
