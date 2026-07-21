"""Homeopathy clinical templates."""

from krama.templates.base import ClinicalTemplate, TemplateSection


TEMPLATES = [
    ClinicalTemplate(
        domain="homeopathy",
        encounter_type="case_taking",
        name="Homeopathic Case Taking",
        description="Detailed constitutional case taking with repertorisation.",
        sections=[
            TemplateSection(
                id="chief_complaint",
                label="Chief Complaint",
                type="text",
                required=True,
            ),
            TemplateSection(
                id="history_present_illness",
                label="History of Present Illness",
                type="textarea",
                ai_assist=True,
            ),
            TemplateSection(
                id="modalities",
                label="Modalities (Aggravating and Ameliorating Factors)",
                type="textarea",
            ),
            TemplateSection(
                id="concomitants",
                label="Concomitant Symptoms",
                type="textarea",
            ),
            TemplateSection(
                id="mental_generals",
                label="Mental Generals",
                type="textarea",
            ),
            TemplateSection(
                id="physical_generals",
                label="Physical Generals",
                type="textarea",
            ),
            TemplateSection(
                id="thermal_reaction",
                label="Thermal Reaction",
                type="select",
                options=["hot", "chilly", "ambithermal"],
            ),
            TemplateSection(
                id="miasmatic_analysis",
                label="Miasmatic Analysis",
                type="select",
                options=["psora", "sycosis", "syphilis", "tubercular"],
            ),
            TemplateSection(
                id="repertorisation",
                label="Repertorisation Summary",
                type="textarea",
                ai_assist=True,
            ),
            TemplateSection(
                id="selected_remedy",
                label="Selected Remedy",
                type="textarea",
                rx_link=True,
            ),
        ],
        vitals=["bp", "weight"],
        coding_system="icd10",
        prescription_type="homeopathic",
    )
]
