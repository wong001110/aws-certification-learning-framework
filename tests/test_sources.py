from __future__ import annotations

import json
from datetime import date, datetime, timezone
from io import BytesIO

from validator.sources import freshness_report, search_cached_sources, sync_source


class Response:
    def __init__(self, content: bytes) -> None:
        self._stream = BytesIO(content)
        self.headers = {"Content-Type": "text/html; charset=utf-8"}

    def read(self, amount: int) -> bytes:
        return self._stream.read(amount)


def source() -> dict:
    return {
        "id": "rds-multi-az",
        "title": "Amazon RDS Multi-AZ deployments",
        "url": "https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZ.html",
        "source_type": "service_documentation",
        "certification_ids": ["SAA-C03"],
        "objective_ids": ["saa-resilient-data"],
        "verified_at": "2026-07-30",
        "refresh_days": 180,
        "critical": False,
        "status": "active",
        "tags": ["rds", "multi-az", "failover"],
        "retrieval": {"enabled": True, "max_bytes": 100000, "chunk_characters": 500, "overlap_words": 10},
    }


def test_freshness_reports_stale_sources() -> None:
    catalog = {"default_refresh_days": 90, "sources": [source()]}
    report = freshness_report(catalog, as_of=date(2027, 2, 1))
    assert report[0]["status"] == "stale"


def test_sync_and_search_official_source(tmp_path) -> None:
    html = b"""
    <html><body><main>
    <h1>Multi-AZ deployments</h1>
    <p>Amazon RDS can maintain a synchronous standby in another Availability Zone.</p>
    <h2>Failover</h2>
    <p>The service can perform automatic failover while applications continue using the database endpoint.</p>
    </main></body></html>
    """

    def opener(request, timeout=20):
        return Response(html)

    path = sync_source(
        source(),
        cache_dir=tmp_path,
        opener=opener,
        fetched_at=datetime(2026, 7, 30, tzinfo=timezone.utc),
    )
    cached = json.loads(path.read_text(encoding="utf-8"))
    assert cached["chunk_count"] >= 1
    assert cached["content_sha256"]

    catalog = {"sources": [source()]}
    results = search_cached_sources(
        "automatic failover database endpoint",
        catalog=catalog,
        cache_dir=tmp_path,
        certification_id="SAA-C03",
    )
    assert results
    assert results[0]["source_id"] == "rds-multi-az"
    assert "failover" in results[0]["excerpt"].lower()
