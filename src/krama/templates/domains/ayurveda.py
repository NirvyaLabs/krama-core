"""Ayurveda clinical templates."""

from krama.templates.base import ClinicalTemplate, TemplateSection


DOSHA_OPTIONS = [
    "vata",
    "pitta",
    "kapha",
    "vata_pitta",
    "pitta_kapha",
    "vata_kapha",
    "tridosha",
]


TEMPLATES = [
    ClinicalTemplate(
        domain="ayurveda",
        encounter_type="prakriti_assessment",
        name="Ayurvedic Consultation",
        description="Prakriti/Vikriti assessment with Nadi and Ashtavidha Pariksha.",
        sections=[
            TemplateSection(
                id="pradhana_vedana",
                label="Chief Complaint (Pradhana Vedana)",
                type="text",
                required=True,
            ),
            TemplateSection(
                id="prakriti",
                label="Prakriti Assessment",
                type="dosha_assessment",
                required=True,
                options=DOSHA_OPTIONS,
            ),
            TemplateSection(
                id="vikriti",
                label="Vikriti (Current Dosha Imbalance)",
                type="dosha_assessment",
                options=DOSHA_OPTIONS,
            ),
            TemplateSection(
                id="nadi_pariksha",
                label="Nadi Pariksha",
                type="textarea",
            ),
            TemplateSection(
                id="ashtavidha_pariksha",
                label="Ashtavidha Pariksha",
                type="checklist",
                items=[
                    "Nadi (Pulse)",
                    "Mutra (Urine)",
                    "Mala (Stool)",
                    "Jihva (Tongue)",
                    "Shabda (Voice)",
                    "Sparsha (Touch/Skin)",
                    "Druk (Eyes)",
                    "Akriti (Appearance)",
                ],
            ),
            TemplateSection(
                id="roga_nidana",
                label="Roga Nidana (Diagnosis)",
                type="textarea",
                ai_assist=True,
            ),
            TemplateSection(
                id="chikitsa",
                label="Chikitsa (Treatment Plan)",
                type="textarea",
                rx_link=True,
            ),
            TemplateSection(
                id="pathya_apathya",
                label="Pathya-Apathya (Diet and Lifestyle)",
                type="textarea",
            ),
        ],
        vitals=["nadi_rate", "bp", "weight"],
        coding_system="ayurveda_icd",
        prescription_type="ayurvedic",
    )
]
