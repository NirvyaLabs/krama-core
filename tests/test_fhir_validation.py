import pytest

from krama.exceptions import FHIRValidationError
from krama.fhir.validation import validate_fhir_bundle


def _bundle(*resources: dict, references: list[str] | None = None) -> dict:
    composition = {
        "resourceType": "Composition",
        "id": "composition-1",
        "subject": {"reference": "urn:uuid:patient-1"},
    }
    entries = [
        {"fullUrl": "urn:uuid:composition-1", "resource": composition},
        *[
            {
                "fullUrl": f"urn:uuid:{resource['id']}",
                "resource": resource,
            }
            for resource in resources
        ],
    ]
    if references is not None:
        composition["section"] = [
            {"entry": [{"reference": reference} for reference in references]}
        ]
    return {"resourceType": "Bundle", "type": "document", "entry": entries}


def test_accepts_document_bundle_with_local_uuid_references():
    validate_fhir_bundle(
        _bundle(
            {"resourceType": "Patient", "id": "patient-1"},
            references=["urn:uuid:patient-1"],
        )
    )


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda bundle: bundle.update(type="collection"), "Bundle.type"),
        (
            lambda bundle: bundle["entry"][0]["resource"].pop("resourceType"),
            "resourceType",
        ),
        (
            lambda bundle: bundle["entry"][1]["resource"].pop("id"),
            "resource.id",
        ),
        (
            lambda bundle: bundle["entry"][0]["resource"]["section"][0]["entry"].__setitem__(
                0, {"reference": "patient-1"}
            ),
            "urn:uuid",
        ),
    ],
)
def test_rejects_common_bundle_errors(mutate, message):
    bundle = _bundle(
        {"resourceType": "Patient", "id": "patient-1"},
        references=["urn:uuid:patient-1"],
    )
    mutate(bundle)
    with pytest.raises(FHIRValidationError, match=message):
        validate_fhir_bundle(bundle)


def test_rejects_missing_composition_first_entry():
    bundle = _bundle({"resourceType": "Patient", "id": "patient-1"})
    bundle["entry"][0], bundle["entry"][1] = bundle["entry"][1], bundle["entry"][0]
    with pytest.raises(FHIRValidationError, match="start with Composition"):
        validate_fhir_bundle(bundle)


def test_allows_external_references():
    validate_fhir_bundle(
        _bundle(
            {"resourceType": "Patient", "id": "patient-1"},
            references=["https://example.org/fhir/Patient/external"],
        )
    )

