"""Generate a sample OPConsult FHIR bundle."""

import json

from krama.fhir import create_op_consult_bundle
from krama.fhir.bundles import (
    DiagnosisInfo,
    MedicationInfo,
    OrganizationInfo,
    PatientInfo,
    PractitionerInfo,
)


def main():
    patient = PatientInfo(
        name="Ravi Kumar",
        abha_address="ravi.kumar@abdm",
        gender="male",
        date_of_birth="1990-05-15",
    )

    doctor = PractitionerInfo(
        name="Dr. Priya Sharma",
        identifier="DOC-AP-12345",
    )

    hospital = OrganizationInfo(
        name="District Hospital Guntur",
        hfr_id="IN0410000123",
    )

    diagnosis = DiagnosisInfo(
        description="Essential hypertension",
        snomed_code="59621000",
        clinical_notes="Patient presents with elevated BP 150/95. "
        "No signs of end-organ damage. Advising lifestyle changes "
        "and initiating pharmacotherapy.",
    )

    medications = [
        MedicationInfo(
            name="Amlodipine",
            dosage="5mg once daily in the morning",
            snomed_code="386864001",
        ),
    ]

    bundle = create_op_consult_bundle(
        patient=patient,
        practitioner=doctor,
        organization=hospital,
        diagnosis=diagnosis,
        encounter_date="2026-05-06",
        medications=medications,
    )

    print("=" * 60)
    print("Krama Core — OPConsult FHIR R4 Bundle")
    print("=" * 60)
    print()
    print(json.dumps(bundle, indent=2))
    print()
    print(f"Bundle contains {len(bundle['entry'])} FHIR resources:")
    for entry in bundle["entry"]:
        rt = entry["resource"]["resourceType"]
        print(f"  - {rt}")


if __name__ == "__main__":
    main()
