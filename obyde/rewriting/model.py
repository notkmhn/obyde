from abc import ABC, abstractmethod
from typing import Callable, List, Optional


class RewritingTransformer(ABC):
    @abstractmethod
    def transform_normal_block(self, block: str) -> Optional[str]:
        pass

    @abstractmethod
    def transform_preformatted_block(self, block: str) -> Optional[str]:
        pass

    @abstractmethod
    def transform_metadata_section(self, metadata: str) -> Optional[str]:
        pass


class RewritingPipeline(RewritingTransformer):
    def __init__(self, phases: List[RewritingTransformer]):
        self.phases = phases

    def transform_normal_block(self, block: str) -> Optional[str]:
        return self.__process_str_transform_iterated(lambda x, y: x.transform_normal_block(y), block)

    def transform_preformatted_block(self, block: str) -> Optional[str]:
        return self.__process_str_transform_iterated(lambda x, y: x.transform_preformatted_block(y), block)

    def transform_metadata_section(self, metadata: str) -> Optional[str]:
        return self.__process_str_transform_iterated(lambda x, y: x.transform_metadata_section(y), metadata)

    def __process_str_transform_iterated(self, transformation_function: Callable[[RewritingTransformer, str], Optional[str]], block: str):
        current_block = block
        for phase in self.phases:
            transformed = transformation_function(phase, block)
            if transformed is not None:
                current_block = transformed
        return current_block
