import logging

_LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


# Configure a shared log format for the service.
def configure_logging() -> None:
	logging.basicConfig(level=logging.INFO, format=_LOG_FORMAT)


# Returns a module-scoped logger with the shared configuration.
def get_logger(name: str) -> logging.Logger:
	configure_logging()
	return logging.getLogger(name)
