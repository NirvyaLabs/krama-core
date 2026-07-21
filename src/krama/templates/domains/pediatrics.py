"""Pediatrics clinical templates."""

from krama.templates.base import ClinicalTemplate, TemplateSection


TEMPLATES = [
    ClinicalTemplate(
        domain="pediatrics",
        encounter_type="pediatric_opd",
        name="Pediatric OPD Consultation",
        description="Growth-adjusted SOAP note with immunization and dosing checks.",
        sections=[
            TemplateSection(
                id="chief_complaint",
                label="Chief Complaint",
                type="text",
                required=True,
                ai_assist=True,
            ),
            TemplateSection(
                id="growth_parameters",
                label="Growth Parameters",
                type="vital_group",
                required=True,
            ),
            TemplateSection(
                id="developmental_history",
                label="Developmental History",
                type="textarea",
            ),
            TemplateSection(
                id="immunization_status",
                label="Immunization Schedule Review",
                type="checklist",
                items=[
                    "BCG",
                    "OPV/IPV",
                    "DPT/Pentavalent",
                    "Rotavirus",
                    "MR/MMR",
                    "Vitamin A",
                    "Age-appropriate boosters",
                ],
            ),
            TemplateSection(
                id="assessment",
                label="Assessment",
                type="textarea",
                required=True,
                icd_coding=True,
            ),
            TemplateSection(
                id="weight_based_dosing",
                label="Weight-based Dosing Required",
                type="select",
                options=["yes", "no"],
                rx_link=True,
            ),
        ],
        vitals=["temperature", "heart_rate", "respiratory_rate", "weight", "height", "head_circumference", "spo2"],
        coding_system="icd10",
        prescription_type="standard",
    )
]
