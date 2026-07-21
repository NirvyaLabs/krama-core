import pytest

from krama import ClinicalTemplate, KramaClient, TemplateRegistry, TemplateSection
from krama.exceptions import TemplateNotFoundError, ValidationError
from krama.templates.domains import BUILTIN_TEMPLATE_MODULES
from krama.templates.validators import TemplateValidator


EXPECTED_DOMAINS = {
    "allopathy",
    "dentistry",
    "ayurveda",
    "homeopathy",
    "surgery",
    "pediatrics",
    "ophthalmology",
    "ob_gyn",
    "psychiatry",
    "dermatology",
    "orthopedics",
    "ent",
}


def test_registry_loads_all_builtin_templates():
    registry = TemplateRegistry()
    templates = registry.list_templates()

    assert len(templates) == 15
    assert all(template.sections for template in templates)
    assert all(any(section.required for section in template.sections) for template in templates)


def test_list_domains_returns_all_twelve_domains():
    registry = TemplateRegistry()

    assert set(registry.list_domains()) == EXPECTED_DOMAINS


def test_builtin_domain_modules_export_templates():
    assert len(BUILTIN_TEMPLATE_MODULES) == 12
    assert all(module.TEMPLATES for module in BUILTIN_TEMPLATE_MODULES)


def test_get_by_domain_returns_expected_template():
    registry = TemplateRegistry()

    ayurveda = registry.get("ayurveda", "prakriti_assessment")
    homeopathy = registry.get("homeopathy", "case_taking")
    dentistry = registry.get("dentistry", "dental_exam")

    assert ayurveda.name == "Ayurvedic Consultation"
    assert any(section.id == "nadi_pariksha" for section in ayurveda.sections)
    assert any(section.id == "pathya_apathya" for section in ayurveda.sections)
    assert any(section.id == "miasmatic_analysis" for section in homeopathy.sections)
    assert any(section.id == "repertorisation" for section in homeopathy.sections)
    assert any(section.id == "fdi_tooth_chart" for section in dentistry.sections)


def test_surgery_and_ob_gyn_template_counts():
    registry = TemplateRegistry()

    assert [template.encounter_type for template in registry.list_templates("surgery")] == [
        "operative_note",
        "post_op_followup",
        "pre_op_assessment",
    ]
    assert [template.encounter_type for template in registry.list_templates("ob_gyn")] == [
        "antenatal_visit",
        "postnatal_visit",
    ]


def test_register_custom_template_and_get_it_back():
    registry = TemplateRegistry(templates=[])
    custom = ClinicalTemplate(
        domain="allopathy",
        encounter_type="followup",
        name="Follow-up Visit",
        description="Focused follow-up encounter",
        sections=[
            TemplateSection(
                id="interval_history",
                label="Interval History",
                type="textarea",
                required=True,
            )
        ],
        vitals=["bp", "weight"],
        coding_system="icd10",
        prescription_type="standard",
    )

    registry.register(custom)

    assert registry.get("ALLOPATHY", "FOLLOWUP") == custom
    assert registry.list_domains() == ["allopathy"]
    assert registry.list_templates("allopathy") == [custom]


def test_missing_template_raises_template_not_found():
    registry = TemplateRegistry()

    with pytest.raises(TemplateNotFoundError, match="unknown:missing"):
        registry.get("unknown", "missing")


def test_section_model_validates_select_and_checklist_structure():
    with pytest.raises(ValueError, match="options"):
        TemplateSection(id="bad_select", label="Bad Select", type="select")

    with pytest.raises(ValueError, match="items"):
        TemplateSection(id="bad_checklist", label="Bad Checklist", type="checklist")

    with pytest.raises(ValueError, match="section type"):
        TemplateSection(id="bad_type", label="Bad Type", type="unsupported")


def test_template_model_rejects_duplicate_section_ids():
    with pytest.raises(ValueError, match="unique"):
        ClinicalTemplate(
            domain="allopathy",
            encounter_type="duplicate",
            name="Duplicate",
            description="Duplicate sections",
            sections=[
                TemplateSection(id="same", label="One", type="text", required=True),
                TemplateSection(id="same", label="Two", type="text"),
            ],
            coding_system="icd10",
            prescription_type="standard",
        )


def test_template_validator_requires_required_section():
    template = ClinicalTemplate(
        domain="allopathy",
        encounter_type="optional_only",
        name="Optional Only",
        description="Invalid registry template",
        sections=[TemplateSection(id="notes", label="Notes", type="textarea")],
        coding_system="icd10",
        prescription_type="standard",
    )

    with pytest.raises(ValidationError, match="required section"):
        TemplateValidator.validate(template)


def test_krama_client_exposes_template_registry():
    client = KramaClient(
        client_id="client",
        client_secret="secret",
        base_url="https://abdm.example",
    )

    try:
        assert isinstance(client.templates, TemplateRegistry)
        assert client.templates.get("psychiatry", "mental_status_exam").domain == "psychiatry"
    finally:
        import asyncio

        asyncio.run(client.close())
