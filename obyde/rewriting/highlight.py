import re
from typing import Optional

from .model import RewritingTransformer


class ObsidianHighlightRewritingTransformer(RewritingTransformer):
    HIGHLIGHT_REGEX = re.compile(r"==(.*)==", flags=re.DOTALL)

    def transform_normal_block(self, block: str) -> Optional[str]:
        transformed, count = self.HIGHLIGHT_REGEX.subn(r"<mark>\1</mark>", block)
        return transformed if count != 0 else None

    def transform_preformatted_block(self, block: str) -> Optional[str]:
        # Does not modify preformatted blocks
        return None

    def transform_metadata_section(self, metadata: str) -> Optional[str]:
        # Does not modify metadata section
        return None
