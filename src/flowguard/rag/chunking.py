import re

from pydantic import BaseModel, ConfigDict

from flowguard.domain.evidence import EvidenceItem

SECTION_HEADING = re.compile(r"^## (.+)$", re.MULTILINE)
KEEP_WHOLE = {"runbook", "historical_incident"}
FULL_DOCUMENT = "Full document"


class Chunk(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    chunk_id: str
    document_id: str
    document_type: str
    title: str
    system: str
    service: str
    version: str
    effective_date: str
    section: str
    source_path: str
    is_current: bool
    text: str


def split_sections(text: str) -> list[tuple[str, str]]:
    headings = list(SECTION_HEADING.finditer(text))
    if not headings:
        return [(FULL_DOCUMENT, text)]

    sections = []
    overview = text[: headings[0].start()].strip()
    if overview:
        sections.append(("Overview", overview))

    ends = [heading.start() for heading in headings[1:]] + [len(text)]
    for heading, end in zip(headings, ends):
        sections.append((heading.group(1), text[heading.start() : end].strip()))
    return sections


def slug(section: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", section.lower()).strip("-")


def chunk_document(item: EvidenceItem) -> list[Chunk]:
    if item.source_type == "api_spec":
        sections = split_sections(item.content)
    elif item.source_type in KEEP_WHOLE:
        sections = [(FULL_DOCUMENT, item.content)]
    else:
        raise ValueError(f"{item.evidence_id} is not a knowledge document")

    return [
        Chunk(
            chunk_id=f"{item.evidence_id}#{slug(section)}",
            document_id=item.evidence_id,
            document_type=item.source_type,
            title=item.title,
            system=item.metadata["system"],
            service=item.source_name,
            version=item.metadata["version"],
            effective_date=item.metadata["effective_date"],
            section=section,
            source_path=item.metadata["source_path"],
            is_current=item.metadata["is_current"],
            text=text,
        )
        for section, text in sections
    ]
