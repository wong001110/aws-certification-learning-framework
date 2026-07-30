from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Callable, Iterable
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG_PATH = ROOT / "sources" / "catalog.yaml"
DEFAULT_CACHE_DIR = ROOT / ".cache" / "aws-cert-docs"
OFFICIAL_HOST_SUFFIXES = ("aws.amazon.com", "docs.aws.amazon.com")
_TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9_.:/-]*", re.IGNORECASE)
_SPACE_RE = re.compile(r"\s+")


def is_official_aws_url(url: str) -> bool:
    try:
        host = (urlparse(url).hostname or "").lower()
    except (AttributeError, ValueError):
        return False
    return any(host == suffix or host.endswith(f".{suffix}") for suffix in OFFICIAL_HOST_SUFFIXES)


def load_source_catalog(path: Path | None = None) -> dict[str, Any]:
    catalog_path = path or DEFAULT_CATALOG_PATH
    value = yaml.safe_load(catalog_path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{catalog_path}: source catalog must be a YAML mapping")
    return value


def catalog_source_map(catalog: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {source["id"]: source for source in catalog.get("sources", [])}


def parse_date(value: str) -> date:
    return date.fromisoformat(value)


def freshness_report(
    catalog: dict[str, Any],
    *,
    as_of: date | None = None,
    certification_id: str | None = None,
) -> list[dict[str, Any]]:
    as_of = as_of or date.today()
    default_days = int(catalog.get("default_refresh_days", 180))
    report: list[dict[str, Any]] = []
    for source in catalog.get("sources", []):
        certifications = source.get("certification_ids", [])
        if certification_id and certifications and certification_id not in certifications:
            continue
        verified_at = parse_date(source["verified_at"])
        refresh_days = int(source.get("refresh_days", default_days))
        expires_at = verified_at + timedelta(days=refresh_days)
        if verified_at > as_of:
            status = "future"
        elif expires_at < as_of:
            status = "stale"
        else:
            status = "fresh"
        report.append(
            {
                "source_id": source["id"],
                "title": source["title"],
                "url": source["url"],
                "critical": bool(source.get("critical", False)),
                "verified_at": verified_at.isoformat(),
                "refresh_days": refresh_days,
                "expires_at": expires_at.isoformat(),
                "days_remaining": (expires_at - as_of).days,
                "status": status,
            }
        )
    return sorted(report, key=lambda item: (item["status"] != "stale", item["days_remaining"], item["source_id"]))


def normalize_text(value: str) -> str:
    return _SPACE_RE.sub(" ", value).strip()


class _ArticleTextParser(HTMLParser):
    """Extract useful headings and prose without committing copied docs to Git."""

    _SKIP_TAGS = {"script", "style", "svg", "noscript", "nav", "footer", "header", "form"}
    _BLOCK_TAGS = {
        "address",
        "article",
        "aside",
        "blockquote",
        "br",
        "dd",
        "div",
        "dl",
        "dt",
        "figcaption",
        "figure",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "li",
        "main",
        "ol",
        "p",
        "pre",
        "section",
        "table",
        "td",
        "th",
        "tr",
        "ul",
    }
    _HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._skip_depth = 0
        self._heading_tag: str | None = None
        self._heading_parts: list[str] = []
        self._current_heading = "Overview"
        self._text_parts: list[str] = []
        self.sections: list[dict[str, str]] = []

    def _flush(self) -> None:
        text = normalize_text(" ".join(self._text_parts))
        if len(text) >= 40:
            self.sections.append({"heading": self._current_heading, "text": text})
        self._text_parts = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in self._SKIP_TAGS:
            self._skip_depth += 1
            return
        if self._skip_depth:
            return
        if tag in self._HEADING_TAGS:
            self._flush()
            self._heading_tag = tag
            self._heading_parts = []
        elif tag in self._BLOCK_TAGS:
            self._text_parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in self._SKIP_TAGS and self._skip_depth:
            self._skip_depth -= 1
            return
        if self._skip_depth:
            return
        if self._heading_tag == tag:
            heading = normalize_text(" ".join(self._heading_parts))
            if heading:
                self._current_heading = heading
            self._heading_tag = None
            self._heading_parts = []
        elif tag in self._BLOCK_TAGS:
            self._text_parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        if self._heading_tag:
            self._heading_parts.append(data)
        else:
            self._text_parts.append(data)

    def close(self) -> None:
        super().close()
        self._flush()


def _split_words(text: str, *, max_chars: int, overlap_words: int) -> list[str]:
    words = text.split()
    if not words:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(words):
        end = start
        length = 0
        while end < len(words):
            addition = len(words[end]) + (1 if end > start else 0)
            if length + addition > max_chars and end > start:
                break
            length += addition
            end += 1
        chunks.append(" ".join(words[start:end]))
        if end >= len(words):
            break
        start = max(start + 1, end - max(0, overlap_words))
    return chunks


def html_to_chunks(
    html: str,
    *,
    source_id: str,
    max_chars: int = 1400,
    overlap_words: int = 35,
) -> list[dict[str, Any]]:
    parser = _ArticleTextParser()
    parser.feed(html)
    parser.close()
    chunks: list[dict[str, Any]] = []
    counter = 1
    for section in parser.sections:
        for text in _split_words(section["text"], max_chars=max_chars, overlap_words=overlap_words):
            chunks.append(
                {
                    "id": f"{source_id}-chunk-{counter:04d}",
                    "heading": section["heading"],
                    "text": text,
                    "character_count": len(text),
                }
            )
            counter += 1
    return chunks


def _response_bytes(response: Any, max_bytes: int) -> bytes:
    data = response.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise ValueError(f"source exceeds configured maximum of {max_bytes} bytes")
    return data


def sync_source(
    source: dict[str, Any],
    *,
    cache_dir: Path | None = None,
    opener: Callable[..., Any] = urlopen,
    timeout: float = 20.0,
    fetched_at: datetime | None = None,
    force: bool = False,
) -> Path:
    if not is_official_aws_url(source.get("url", "")):
        raise ValueError(f"{source.get('id')}: only official AWS URLs may be synchronized")
    retrieval = source.get("retrieval", {})
    if retrieval.get("enabled", True) is False:
        raise ValueError(f"{source.get('id')}: retrieval is disabled in the catalog")

    cache_dir = cache_dir or DEFAULT_CACHE_DIR
    cache_dir.mkdir(parents=True, exist_ok=True)
    output_path = cache_dir / f"{source['id']}.json"
    if output_path.exists() and not force:
        return output_path

    max_bytes = int(retrieval.get("max_bytes", 3_000_000))
    request = Request(
        source["url"],
        headers={
            "User-Agent": "aws-certification-learning-framework/0.4 (+https://github.com/wong001110/aws-certification-learning-framework)",
            "Accept": "text/html,application/xhtml+xml;q=0.9,text/plain;q=0.8",
        },
    )
    response = opener(request, timeout=timeout)
    raw = _response_bytes(response, max_bytes)
    content_type = ""
    if hasattr(response, "headers"):
        content_type = response.headers.get("Content-Type", "") or ""
    charset = "utf-8"
    if "charset=" in content_type:
        charset = content_type.split("charset=", 1)[1].split(";", 1)[0].strip()
    html = raw.decode(charset, errors="replace")
    chunks = html_to_chunks(
        html,
        source_id=source["id"],
        max_chars=int(retrieval.get("chunk_characters", 1400)),
        overlap_words=int(retrieval.get("overlap_words", 35)),
    )
    if not chunks:
        raise ValueError(f"{source['id']}: no useful text chunks were extracted")

    fetched_at = fetched_at or datetime.now(timezone.utc)
    document = {
        "schema_version": 1,
        "source_id": source["id"],
        "title": source["title"],
        "url": source["url"],
        "fetched_at": fetched_at.isoformat(),
        "content_type": content_type or "text/html",
        "content_sha256": hashlib.sha256(raw).hexdigest(),
        "chunk_count": len(chunks),
        "chunks": chunks,
    }
    temporary = output_path.with_suffix(".tmp")
    temporary.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(output_path)
    return output_path


def sync_catalog_sources(
    catalog: dict[str, Any],
    source_ids: Iterable[str],
    *,
    cache_dir: Path | None = None,
    force: bool = False,
) -> list[Path]:
    source_map = catalog_source_map(catalog)
    output: list[Path] = []
    for source_id in source_ids:
        source = source_map.get(source_id)
        if source is None:
            raise KeyError(f"unknown source id: {source_id}")
        output.append(sync_source(source, cache_dir=cache_dir, force=force))
    return output


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in _TOKEN_RE.findall(text)]


def _excerpt(text: str, query_tokens: set[str], limit: int = 320) -> str:
    lowered = text.lower()
    positions = [lowered.find(token) for token in query_tokens if lowered.find(token) >= 0]
    start = max(0, (min(positions) if positions else 0) - 80)
    snippet = text[start : start + limit]
    if start > 0:
        snippet = "…" + snippet
    if start + limit < len(text):
        snippet += "…"
    return snippet


def load_cached_documents(cache_dir: Path | None = None) -> list[dict[str, Any]]:
    cache_dir = cache_dir or DEFAULT_CACHE_DIR
    if not cache_dir.exists():
        return []
    documents: list[dict[str, Any]] = []
    for path in sorted(cache_dir.glob("*.json")):
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if isinstance(value, dict) and isinstance(value.get("chunks"), list):
            value["cache_path"] = str(path)
            documents.append(value)
    return documents


def search_cached_sources(
    query: str,
    *,
    catalog: dict[str, Any] | None = None,
    cache_dir: Path | None = None,
    certification_id: str | None = None,
    source_ids: set[str] | None = None,
    limit: int = 5,
) -> list[dict[str, Any]]:
    query_tokens = tokenize(query)
    if not query_tokens:
        return []
    query_set = set(query_tokens)
    catalog = catalog or load_source_catalog()
    source_map = catalog_source_map(catalog)

    chunks: list[dict[str, Any]] = []
    for document in load_cached_documents(cache_dir):
        source = source_map.get(document.get("source_id"))
        if source is None:
            continue
        if source_ids and source["id"] not in source_ids:
            continue
        certifications = source.get("certification_ids", [])
        if certification_id and certifications and certification_id not in certifications:
            continue
        for chunk in document.get("chunks", []):
            text = str(chunk.get("text", ""))
            tokens = tokenize(text)
            if not tokens:
                continue
            chunks.append(
                {
                    "source": source,
                    "document": document,
                    "chunk": chunk,
                    "tokens": tokens,
                    "frequencies": Counter(tokens),
                }
            )
    if not chunks:
        return []

    document_frequency: Counter[str] = Counter()
    for item in chunks:
        present = set(item["tokens"])
        for token in query_set & present:
            document_frequency[token] += 1
    average_length = sum(len(item["tokens"]) for item in chunks) / len(chunks)
    k1 = 1.5
    b = 0.75
    scored: list[tuple[float, dict[str, Any]]] = []
    total_chunks = len(chunks)
    for item in chunks:
        length = len(item["tokens"])
        score = 0.0
        heading_tokens = set(tokenize(str(item["chunk"].get("heading", ""))))
        title_tokens = set(tokenize(item["source"]["title"]))
        tag_tokens = set(tokenize(" ".join(item["source"].get("tags", []))))
        for token in query_set:
            frequency = item["frequencies"].get(token, 0)
            if frequency:
                frequency_docs = document_frequency.get(token, 0)
                inverse_frequency = math.log(
                    1 + (total_chunks - frequency_docs + 0.5) / (frequency_docs + 0.5)
                )
                denominator = frequency + k1 * (1 - b + b * length / max(1.0, average_length))
                score += inverse_frequency * frequency * (k1 + 1) / denominator
            if token in heading_tokens:
                score += 0.8
            if token in title_tokens:
                score += 1.0
            if token in tag_tokens:
                score += 0.35
        if score > 0:
            scored.append((score, item))

    scored.sort(key=lambda pair: (-pair[0], pair[1]["source"]["id"], pair[1]["chunk"]["id"]))
    results: list[dict[str, Any]] = []
    for score, item in scored[: max(1, limit)]:
        source = item["source"]
        document = item["document"]
        chunk = item["chunk"]
        results.append(
            {
                "source_id": source["id"],
                "source_title": source["title"],
                "url": source["url"],
                "verified_at": source["verified_at"],
                "fetched_at": document.get("fetched_at"),
                "chunk_id": chunk["id"],
                "heading": chunk.get("heading", "Overview"),
                "score": round(score, 6),
                "excerpt": _excerpt(str(chunk.get("text", "")), query_set),
                "cache_path": document.get("cache_path"),
            }
        )
    return results
