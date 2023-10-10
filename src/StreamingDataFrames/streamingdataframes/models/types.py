from typing import Union, List, Tuple, Optional, Mapping, Any
from typing_extensions import Protocol, Self

MessageKey = Union[str, bytes]
MessageValue = Union[str, bytes]
MessageHeadersTuples = List[Tuple[str, bytes]]
MessageHeadersMapping = Mapping[str, Union[str, bytes, None]]


class ConfluentKafkaMessageProto(Protocol):
    """
    An interface of `confluent_kafka.Message`.

    Use it to not depend on exact implementation and simplify testing.

    Instances of `confluent_kafka.Message` cannot be directly created from Python,
    see https://github.com/confluentinc/confluent-kafka-python/issues/1535.

    """

    def headers(self, *args, **kwargs) -> Optional[List[Tuple[str, bytes]]]:
        ...

    def key(self, *args, **kwargs) -> Optional[Union[str, bytes]]:
        ...

    def offset(self, *args, **kwargs) -> int:
        ...

    def partition(self, *args, **kwargs) -> int:
        ...

    def timestamp(self, *args, **kwargs) -> (int, int):
        ...

    def topic(self, *args, **kwargs) -> str:
        ...

    def value(self, *args, **kwargs) -> Optional[Union[str, bytes]]:
        ...

    def latency(self, *args, **kwargs) -> Optional[float]:
        ...

    def leader_epoch(self, *args, **kwargs) -> Optional[int]:
        ...

    def __len__(self) -> int:
        ...


# TODO: replace with dataclass in Python>=3.10
class SlottedClass:
    """
    Mostly here as a placeholder for DataClasses and doing "equals" comparisons.
    """

    __slots__ = ()

    def __eq__(self, other: Self) -> bool:
        for p in self.__slots__:
            if self.eq_get_attr(p) != other.eq_get_attr(p):
                return False
        return True

    def eq_get_attr(self, item: str) -> Any:
        """
        This is for when a slot is defined, but was never assigned a value.
        Don't want it to fail an equality check via exception, so we just return None.
        """
        try:
            return self.__getattribute__(item)
        except AttributeError:
            return None
