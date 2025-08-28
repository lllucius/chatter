from enum import Enum


class DocumentType(str, Enum):
    CSV = "csv"
    DOC = "doc"
    DOCX = "docx"
    HTML = "html"
    JSON = "json"
    MARKDOWN = "markdown"
    ODT = "odt"
    OTHER = "other"
    PDF = "pdf"
    RTF = "rtf"
    TEXT = "text"
    XML = "xml"

    def __str__(self) -> str:
        return str(self.value)
