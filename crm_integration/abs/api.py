from abc import ABC, abstractmethod


class CRMInterface(ABC):

    @classmethod
    @abstractmethod
    def handle_order_creation(cls, order, domain: str):
        pass

    @classmethod
    @abstractmethod
    def handle_incoming_webhook(cls, data: dict):
        pass
    
    @classmethod
    @abstractmethod
    def handle_outgoing_webhook(cls, data: dict):
        pass
