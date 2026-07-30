"""Built-in clinical template domains."""

from krama.templates.domains import (
    ayurveda,
    dentistry,
    dermatology,
    ent,
    general_medicine,
    homeopathy,
    ob_gyn,
    ophthalmology,
    orthopedics,
    pediatrics,
    psychiatry,
    surgery,
)

BUILTIN_TEMPLATE_MODULES = [
    general_medicine,
    dentistry,
    ayurveda,
    homeopathy,
    surgery,
    pediatrics,
    ophthalmology,
    ob_gyn,
    psychiatry,
    dermatology,
    orthopedics,
    ent,
]

__all__ = ["BUILTIN_TEMPLATE_MODULES"]
