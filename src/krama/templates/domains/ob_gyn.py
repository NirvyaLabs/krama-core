"""Obstetrics and gynecology clinical templates."""

from krama.templates.base import ClinicalTemplate, TemplateSection

TEMPLATES = [
    ClinicalTemplate(
        domain="ob_gyn",
        encounter_type="antenatal_visit",
        name="Antenatal Visit",
        description="Antenatal documentation with LMP, EDD, gravida/para, and fetal monitoring.",
        sections=[
            TemplateSection(
                id="gravida_para",
                label="Gravida/Para",
                type="text",
                required=True,
            ),
            TemplateSection(
                id="lmp",
                label="Last Menstrual Period (LMP)",
                type="date",
                required=True,
            ),
            TemplateSection(
                id="edd",
                label="Estimated Date of Delivery (EDD)",
                type="date",
                required=True,
            ),
            TemplateSection(
                id="gestational_age",
                label="Gestational Age",
                type="text",
            ),
            TemplateSection(
                id="fetal_monitoring",
                label="Fetal Monitoring",
                type="textarea",
            ),
            TemplateSection(
                id="antenatal_risk",
                label="Antenatal Risk Assessment",
                type="textarea",
                icd_coding=True,
            ),
            TemplateSection(
                id="plan",
                label="Plan and Supplements",
                type="textarea",
                rx_link=True,
            ),
        ],
        vitals=["bp", "weight", "fundal_height", "fetal_heart_rate"],
        coding_system="icd10",
        prescription_type="standard",
    ),
    ClinicalTemplate(
        domain="ob_gyn",
        encounter_type="postnatal_visit",
        name="Postnatal Visit",
        description="Postnatal review for mother and newborn after delivery.",
        sections=[
            TemplateSection(
                id="delivery_summary",
                label="Delivery Summary",
                type="textarea",
                required=True,
            ),
            TemplateSection(
                id="maternal_recovery",
                label="Maternal Recovery",
                type="textarea",
                required=True,
            ),
            TemplateSection(
                id="lactation",
                label="Lactation and Breastfeeding",
                type="textarea",
            ),
            TemplateSection(
                id="newborn_status",
                label="Newborn Status",
                type="textarea",
            ),
            TemplateSection(
                id="postnatal_plan",
                label="Postnatal Plan",
                type="textarea",
                rx_link=True,
            ),
        ],
        vitals=["bp", "temperature", "weight"],
        coding_system="icd10",
        prescription_type="standard",
    ),
]
