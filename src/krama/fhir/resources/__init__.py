"""FHIR R4 resource builders."""

from krama.fhir.resources.allergy_intolerance import FHIRAllergyIntolerance
from krama.fhir.resources.composition import FHIRComposition
from krama.fhir.resources.condition import FHIRCondition
from krama.fhir.resources.diagnostic_report import FHIRDiagnosticReport
from krama.fhir.resources.encounter import FHIREncounter
from krama.fhir.resources.medication_request import FHIRMedicationRequest
from krama.fhir.resources.observation import FHIRObservation
from krama.fhir.resources.organization import FHIROrganization
from krama.fhir.resources.patient import FHIRPatient
from krama.fhir.resources.practitioner import FHIRPractitioner
from krama.fhir.resources.procedure import FHIRProcedure

__all__ = [
    "FHIRAllergyIntolerance",
    "FHIRComposition",
    "FHIRCondition",
    "FHIRDiagnosticReport",
    "FHIREncounter",
    "FHIRMedicationRequest",
    "FHIRObservation",
    "FHIROrganization",
    "FHIRPatient",
    "FHIRPractitioner",
    "FHIRProcedure",
]
