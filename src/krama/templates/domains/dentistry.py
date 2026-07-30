"""Dentistry clinical templates."""

from krama.templates.base import ClinicalTemplate, TemplateSection

TEMPLATES = [
    ClinicalTemplate(
        domain="dentistry",
        encounter_type="dental_exam",
        name="Dental Examination",
        description="Comprehensive dental exam with FDI tooth notation.",
        sections=[
            TemplateSection(
                id="chief_complaint",
                label="Chief Complaint",
                type="text",
                required=True,
            ),
            TemplateSection(
                id="fdi_tooth_chart",
                label="Dental Chart (FDI Notation)",
                type="dental_chart",
                required=True,
            ),
            TemplateSection(
                id="extraoral_exam",
                label="Extraoral Examination",
                type="textarea",
            ),
            TemplateSection(
                id="intraoral_exam",
                label="Intraoral Examination",
                type="textarea",
            ),
            TemplateSection(
                id="periodontal_status",
                label="Periodontal Status",
                type="textarea",
            ),
            TemplateSection(
                id="radiograph_findings",
                label="Radiograph Findings",
                type="textarea",
            ),
            TemplateSection(
                id="diagnosis",
                label="Dental Diagnosis",
                type="textarea",
                icd_coding=True,
            ),
            TemplateSection(
                id="procedures",
                label="Procedures Performed",
                type="procedure_list",
                rx_link=True,
            ),
        ],
        vitals=["bp"],
        coding_system="dental_ada",
        prescription_type="dental",
    )
]
