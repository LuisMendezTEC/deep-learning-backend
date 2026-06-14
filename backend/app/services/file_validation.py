import logging

logger = logging.getLogger(__name__)


def detect_mime(data: bytes) -> str | None:
    try:
        import magic

        return str(magic.from_buffer(data, mime=True))
    except Exception as exc:  # noqa: BLE001 - MIME detection is useful but should not be a hard runtime dependency.
        logger.debug("python-magic MIME detection unavailable: %s", exc)
        return None

