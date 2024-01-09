from .celery_config import app as celery_app

__all__ = ("celery_app",)

__version__ = "1.0.1"
"""
major.minor.maintenance
major - крупные изменения, либо изменения несовместимые с предыдущей версией;
minor - добавление функционала без нарушения совместимости;
maintenance - исправления.
"""
