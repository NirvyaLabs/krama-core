"""Built-in clinical template domains."""

from krama.templates.domains import ayurveda
from krama.templates.domains import dentistry
from krama.templates.domains import dermatology
from krama.templates.domains import ent
from krama.templates.domains import general_medicine
from krama.templates.domains import homeopathy
from krama.templates.domains import ob_gyn
from krama.templates.domains import ophthalmology
from krama.templates.domains import orthopedics
from krama.templates.domains import pediatrics
from krama.templates.domains import psychiatry
from krama.templates.domains import surgery

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
