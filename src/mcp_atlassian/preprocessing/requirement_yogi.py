"""Requirements Yogi-specific text preprocessing module."""

import logging
import re

from .base import BasePreprocessor

logger = logging.getLogger("mcp-atlassian")


class RequirementYogiPreprocessor(BasePreprocessor):
    """Handles text preprocessing for Requirements Yogi content.

    Requirements Yogi stores requirement content as HTML in the storageData.data
    field. This preprocessor converts that HTML to clean Markdown for consumption
    by LLM tools.
    """

    def __init__(self, base_url: str = "") -> None:
        """
        Initialize the Requirements Yogi text preprocessor.

        Args:
            base_url: Base URL for Confluence instance
        """
        super().__init__(base_url=base_url)

    def process_requirement_content(self, html_content: str) -> str:
        """
        Process requirement HTML content to clean Markdown.

        This is a convenience method specifically for requirement storageData.data
        content. It handles the HTML→Markdown conversion and cleans up the result.

        Args:
            html_content: The HTML content from storageData.data

        Returns:
            Clean Markdown string
        """
        if not html_content:
            return ""

        try:
            # Use the base class HTML→Markdown conversion
            _, markdown = self.process_html_content(html_content)

            # Clean up the markdown
            markdown = self._clean_markdown(markdown)

            return markdown
        except Exception as e:
            logger.warning(f"Error processing requirement content: {e}")
            # Fall back to basic HTML stripping
            return self._strip_html_tags(html_content)

    def _clean_markdown(self, markdown: str) -> str:
        """
        Clean up generated Markdown content.

        Args:
            markdown: Raw Markdown from HTML conversion

        Returns:
            Cleaned Markdown string
        """
        if not markdown:
            return ""

        # Normalize line endings
        markdown = markdown.replace("\r\n", "\n")

        # Remove excessive blank lines (more than 2 consecutive)
        markdown = re.sub(r"\n{3,}", "\n\n", markdown)

        # Strip leading/trailing whitespace
        markdown = markdown.strip()

        return markdown

    @staticmethod
    def _strip_html_tags(html: str) -> str:
        """
        Fallback: strip all HTML tags to get plain text.

        Args:
            html: HTML content

        Returns:
            Plain text with HTML tags removed
        """
        if not html:
            return ""
        # Remove HTML tags
        text = re.sub(r"<[^>]+>", "", html)
        # Decode common HTML entities
        text = text.replace("&amp;", "&")
        text = text.replace("&lt;", "<")
        text = text.replace("&gt;", ">")
        text = text.replace("&quot;", '"')
        text = text.replace("&#39;", "'")
        text = text.replace("&nbsp;", " ")
        # Normalize whitespace
        text = re.sub(r"\s+", " ", text).strip()
        return text
