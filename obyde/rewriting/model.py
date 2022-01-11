from abc import ABC, abstractmethod
from io import StringIO
from typing import Callable, List, Optional, Tuple

from ..parsing import ContentBlock, PreformattedContentBlock


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


class RewritingEngine(object):
    def __init__(self, transformer: RewritingTransformer):
        self.transformer = transformer

    def rewrite(self, metadata, content_blocks: List[ContentBlock]) -> Tuple[str, str]:
        metadata = self.transformer.transform_metadata_section(
            metadata) or metadata
        rewritten_content = StringIO()
        for block in content_blocks:
            if isinstance(block, PreformattedContentBlock):
                transformed = self.transformer.transform_preformatted_block(
                    block.content)
                transformed = transformed or block.content
                ticks = "`" * block.wrapping_tick_count
                rewritten_content.write(ticks)
                rewritten_content.write(transformed)
                rewritten_content.write(ticks)
            elif isinstance(block, ContentBlock):
                transformed = self.transformer.transform_normal_block(
                    block.content)
                transformed = transformed or block.content
                rewritten_content.write(transformed)
            else:
                raise ValueError(
                    f"Unexpected object {repr(block)} encountered while rewriting content.")

        return (metadata, rewritten_content.getvalue())
