"""Medication safety checks."""

from __future__ import annotations

from pydantic import BaseModel, Field

from krama.ai.clinical_nlp import SAFETY_DISCLAIMER


class InteractionResult(BaseModel):
    """Drug interaction and allergy check result."""

    passed: bool
    warnings: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    disclaimer: str = SAFETY_DISCLAIMER


class DrugChecker:
    """Conservative rule-based medication checks."""

    _INTERACTION_WARNINGS = {
        frozenset({"warfarin", "aspirin"}): "Warfarin with aspirin may increase bleeding risk.",
        frozenset({"methotrexate", "trimethoprim"}): (
            "Methotrexate with trimethoprim may increase marrow toxicity risk."
        ),
        frozenset({"ace inhibitor", "spironolactone"}): (
            "ACE inhibitor with spironolactone may increase hyperkalemia risk."
        ),
    }

    def check_interactions(
        self,
        medications: list[str],
        patient_allergies: list[str],
    ) -> InteractionResult:
        normalized_meds = [_normalize(value) for value in medications]
        normalized_allergies = [_normalize(value) for value in patient_allergies]
        blockers: list[str] = []
        warnings: list[str] = []

        for med in normalized_meds:
            for allergy in normalized_allergies:
                if allergy and allergy in med:
                    blockers.append(f"{medications[normalized_meds.index(med)]} matches allergy {allergy}.")

        if len(set(normalized_meds)) != len(normalized_meds):
            warnings.append("Duplicate medication detected.")

        med_set = set(normalized_meds)
        for pair, message in self._INTERACTION_WARNINGS.items():
            if pair <= med_set:
                warnings.append(message)

        return InteractionResult(
            passed=not blockers,
            warnings=warnings,
            blockers=blockers,
        )


def _normalize(value: str) -> str:
    return value.strip().lower()
