"""Convenience facade for FHIR builder entry points."""

from __future__ import annotations

from krama.fhir.bundles import (
    create_discharge_summary_bundle,
    create_op_consult_bundle,
    create_prescription_bundle,
)
from krama.fhir.compositions import OPConsultBuilder, PrescriptionBuilder


class FHIRFacade:
    """Small SDK facade for fluent FHIR document builders."""

    def op_consult(self) -> OPConsultBuilder:
        return OPConsultBuilder()

    def prescription(self) -> PrescriptionBuilder:
        return PrescriptionBuilder()

    create_op_consult_bundle = staticmethod(create_op_consult_bundle)
    create_prescription_bundle = staticmethod(create_prescription_bundle)
    create_discharge_summary_bundle = staticmethod(create_discharge_summary_bundle)


__all__ = ["FHIRFacade"]
