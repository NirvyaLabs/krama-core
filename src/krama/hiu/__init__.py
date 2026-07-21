"""HIU Milestone 3 helpers."""

from krama.hiu.consent import ConsentManager
from krama.hiu.data_receive import DataReceiver
from krama.hiu.data_request import DataRequester
from krama.hiu.schemas import (
    ConsentRecord,
    ConsentRequest,
    ConsentState,
    DataRequest,
    DataRequestResult,
    EncryptedHealthData,
    ReceivedHealthData,
)


class HIUClient:
    """Facade for HIU Milestone 3 operations."""

    def __init__(self, http_client) -> None:
        self.consents = ConsentManager(http_client)
        self.data_requests = DataRequester(http_client)
        self.data_receiver = DataReceiver()


__all__ = [
    "ConsentManager",
    "ConsentRecord",
    "ConsentRequest",
    "ConsentState",
    "DataReceiver",
    "DataRequest",
    "DataRequester",
    "DataRequestResult",
    "EncryptedHealthData",
    "HIUClient",
    "ReceivedHealthData",
]
