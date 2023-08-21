import uuid
from copy import deepcopy
from functools import partial
from typing import Self, Optional, Callable, TypeAlias, Union, List, Mapping

from .column import Column, OpValue
from .pipeline import Pipeline, get_func_name
from ..models import Row, Topic
from ..rowconsumer import RowConsumerProto
from ..rowproducer import RowProducerProto

RowApplier: TypeAlias = Callable[[Row], Optional[Union[Row, list[Row]]]]

__all__ = ("StreamingDataFrame",)


def subset(keys: list[str], row: Row) -> Row:
    new_row = deepcopy(row)
    new_row.value = new_row[keys]
    return new_row


def setitem(k: str, v: Union[Column, OpValue], row: Row) -> Row:
    row[k] = v.eval(row) if isinstance(v, Column) else v
    return row


def column_filter(column: Column, row: Row) -> Optional[Row]:
    return row if column.eval(row) else None


# TODO: make a pipeline merge function to avoid accessing private methods
class StreamingDataFrame:
    def __init__(
        self, topics: List[Topic], name: str = None, _pipeline: Pipeline = None
    ):
        self.name = name or str(uuid.uuid4())
        self._pipeline = _pipeline or Pipeline(name=self.name)
        self._real_consumer: Optional[RowConsumerProto] = None
        self._real_producer: Optional[RowProducerProto] = None
        if not topics:
            raise ValueError("Topic list cannot be empty")
        self._topics = {t.name: t for t in topics}

    def apply(
        self, func: Callable[[Row], Optional[Union[Row, list[Row], None]]]
    ) -> Self:
        """
        Add a function to the StreamingDataframe execution list.
        The provided function should accept a Quixstreams Row as its input.
        The provided function should operate on and return the same input Row, or None
        if its intended to be a "filtering" function.

        :param func: callable that accepts and (usually) returns a QuixStreams Row
        :return: self (StreamingDataFrame)
        """
        return self._clone()._apply(func=func, func_name=f"apply:{get_func_name(func)}")

    def process(self, row: Row) -> Optional[Union[Row, list[Row]]]:
        """
        Execute the previously defined StreamingDataframe operations on a provided Row.
        :param row: a QuixStreams Row object
        :return: Row, list of Rows, or None (if filtered)
        """
        return self._pipeline.process(row)

    @property
    def topics(self) -> Mapping[str, Topic]:
        """
        Get a mapping with Topics for the StreamingDataFrame
        :return: dict of {<topic_name>: <Topic>}
        """
        return self._topics

    @property
    def consumer(self) -> RowConsumerProto:
        if self._real_consumer is None:
            raise RuntimeError("Consumer instance has not been provided")
        return self._real_consumer

    @consumer.setter
    def consumer(self, consumer: RowConsumerProto):
        self._real_consumer = consumer

    @property
    def producer(self) -> RowProducerProto:
        if self._real_producer is None:
            raise RuntimeError("Producer instance has not been provided")
        return self._real_producer

    @producer.setter
    def producer(self, producer: RowProducerProto):
        self._real_producer = producer

    def __setitem__(self, key: str, value: Union[Column, OpValue, str]):
        self._apply(partial(setitem, key, value))

    def __getitem__(
        self, item: Union[str, list[str], Column, Self]
    ) -> Union[Column, Self]:
        if isinstance(item, Column):
            return self._apply(partial(column_filter, item))
        elif isinstance(item, list):
            return self._apply(partial(subset, item))
        elif isinstance(item, StreamingDataFrame):
            # TODO: Implement filtering based on another SDF
            raise ValueError(
                "Filtering based on StreamingDataFrame is not supported yet."
            )
        else:
            return Column(col_name=item)

    def _clone(self) -> Self:
        return self.__class__(
            topics=list(self._topics.values()), _pipeline=self._pipeline.clone()
        )

    def _apply(self, func: RowApplier, func_name=None):
        self._pipeline.apply(func, func_name=func_name)
        return self
