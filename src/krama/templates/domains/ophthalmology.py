"""Ophthalmology clinical templates."""

from krama.templates.base import ClinicalTemplate, TemplateSection


TEMPLATES = [
    ClinicalTemplate(
        domain="ophthalmology",
        encounter_type="eye_exam",
        name="Ophthalmology Eye Examination",
        description="Eye exam with visual acuity, IOP, fundus, refraction, and slit lamp.",
        sections=[
            TemplateSection(
                id="chief_complaint",
                label="Chief Complaint",
                type="text",
                required=True,
            ),
            TemplateSection(
                id="visual_acuity",
                label="Visual Acuity",
                type="textarea",
                required=True,
            ),
            TemplateSection(
                id="refraction",
                label="Refraction",
                type="textarea",
            ),
            TemplateSection(
                id="iop",
                label="Intraocular Pressure (IOP)",
                type="textarea",
            ),
            TemplateSection(
                id="slit_lamp",
                label="Slit Lamp Examination",
                type="textarea",
            ),
            TemplateSection(
                id="fundus_exam",
                label="Fundus Examination",
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
        vitals=["bp"],
        coding_system="icd10",
        prescription_type="standard",
    )
]
