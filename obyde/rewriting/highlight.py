from typing import Optional

from .model import RewritingTransformer


class ObsidianHighlightRewritingTransformer(RewritingTransformer):
    def transform_normal_block(self, block: str) -> Optional[str]:
        return None

    def transform_preformatted_block(self, block: str) -> Optional[str]:
        # Does not modify preformatted blocks
        return None

    def transform_metadata_section(self, metadata: str) -> Optional[str]:
        # Does not modify metadata section
        return None
