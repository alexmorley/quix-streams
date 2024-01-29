from quixstreams.exceptions import QuixException


class TopicNotFoundError(QuixException):
    ...


class TopicConfigurationMismatch(QuixException):
    ...


class CreateTopicTimeout(QuixException):
    ...


class CreateTopicFailure(QuixException):
    ...


class TopicNameLengthExceeded(QuixException):
    ...


class CreateTopicTimeout(Exception):
    ...


class CreateTopicFailure(Exception):
    ...
