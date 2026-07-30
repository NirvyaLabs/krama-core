"""Flask example app demonstrating Krama Core integration.

Note: This is an example application for demonstration purposes only.
It does not include production authentication, authorization, or deployment setup.
No database, real patient data, or real ABDM gateway calls are used.
"""

from flask import Flask, jsonify, request

from krama.compliance import ComplianceContext, ComplianceEngine
from krama.fhir import create_op_consult_bundle
from krama.fhir.bundles import (
    DiagnosisInfo,
    MedicationInfo,
    OrganizationInfo,
    PatientInfo,
    PractitionerInfo,
)

app = Flask(__name__)


@app.route("/")
def index():
    """Index endpoint providing API information."""
    return jsonify({
        "name": "Krama Core Flask Example",
        "description": "Demonstration of Krama Core SDK in a Flask web application",
        "endpoints": {
            "op_consult": "/api/op-consult",
            "compliance_check": "/api/compliance",
        },
        "note": "This is sample code for demonstration only, not for production deployment.",
    })


@app.route("/api/op-consult", methods=["GET"])
def get_op_consult_bundle():
    """Endpoint that creates a sample Outpatient Consultation FHIR bundle using synthetic data."""
    # Build synthetic patient, practitioner, hospital, diagnosis, and medication info
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
        clinical_notes="Patient presents with elevated BP 150/95. Prescribed medication.",
    )

    medications = [
        MedicationInfo(
            name="Amlodipine",
            dosage="5mg once daily",
            snomed_code="386864001",
        ),
    ]

    # Create the ABDM-compliant FHIR R4 OPConsult bundle
    bundle = create_op_consult_bundle(
        patient=patient,
        practitioner=doctor,
        organization=hospital,
        diagnosis=diagnosis,
        encounter_date="2026-07-30",
        medications=medications,
    )

    return jsonify({
        "status": "success",
        "resource_type": bundle.get("resourceType"),
        "total_resources": len(bundle.get("entry", [])),
        "bundle": bundle,
    })


@app.route("/api/compliance", methods=["GET", "POST"])
def check_compliance():
    """Endpoint that runs a compliance check using synthetic healthcare metadata."""
    data = request.get_json(silent=True) or {}

    # Extract fields with fallback synthetic defaults
    country = data.get("country", "IND")
    purpose = data.get("purpose", "Care management")
    patient_identifiers = data.get("patient_identifiers", ["india_abha_address"])
    consent_present = data.get("consent_present", True)
    encrypted = data.get("encrypted", True)
    data_residency_region = data.get("data_residency_region", "ap-south-1")
    requested_fields = data.get("requested_fields", ["diagnosis", "medications"])
    necessary_fields = data.get("necessary_fields", ["diagnosis", "medications"])

    context = ComplianceContext(
        country=country,
        purpose=purpose,
        patient_identifiers=patient_identifiers,
        consent_present=consent_present,
        encrypted=encrypted,
        data_residency_region=data_residency_region,
        requested_fields=requested_fields,
        necessary_fields=necessary_fields,
        actor_id="doctor-1",
        audit_event_id="audit-sample-123",
    )

    result = ComplianceEngine().evaluate(context)

    return jsonify({
        "status": "success",
        "passed": result.passed,
        "country": context.country,
        "frameworks": result.frameworks,
        "blockers": [
            {"code": b.code, "message": b.message, "severity": b.severity.value}
            for b in result.blockers
        ],
        "warnings": [
            {"code": w.code, "message": w.message, "severity": w.severity.value}
            for w in result.warnings
        ],
    })


if __name__ == "__main__":
    # Note: Running Flask development server for local demonstration only.
    # Do not use app.run() in production environments.
    app.run(host="127.0.0.1", port=5000, debug=True)
