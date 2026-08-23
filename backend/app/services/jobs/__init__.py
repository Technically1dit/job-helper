"""Composable job-search providers and shared result processing."""

from .orchestrator import JobSearchUnavailable, search_jobs

__all__ = ["JobSearchUnavailable", "search_jobs"]
