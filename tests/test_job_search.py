import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from backend.app.models.job import Job
from backend.app.schemas.job import JobResponse
from backend.app.services.jobs.contacts import recruitment_role_supported, verified_email_from_source
from backend.app.services.jobs.deduplicator import deduplicate
from backend.app.services.jobs.normalizer import normalize_job
from backend.app.services.jobs.orchestrator import search_jobs
from backend.app.services.jobs.providers.workopia import WorkopiaProvider
from backend.app.services.jobs.ranking import filter_by_location
from backend.app.services.serpapi import build_job_search_params


class JobSearchTests(unittest.IsolatedAsyncioTestCase):
    def test_normalizes_and_deduplicates_canonical_url(self):
        first = normalize_job({"title": "Python Developer", "company_name": "Acme", "location": "Ahmedabad", "share_link": "https://jobs.acme.test/opening/?tracking=x"}, "serpapi")
        second = normalize_job({"title": "Python developer", "company": "Acme", "location": "Ahmedabad", "apply_url": "https://jobs.acme.test/opening"}, "apify")
        self.assertEqual(len(deduplicate([first, second])), 1)

    def test_provider_ids_prevent_google_job_link_collapse(self):
        jobs = [
            normalize_job({"title": "Engineer A", "company": "Acme", "location": "India", "job_id": "one", "share_link": "https://google.test/search?htidocid=one&source=test"}, "serpapi"),
            normalize_job({"title": "Engineer B", "company": "Beta", "location": "India", "job_id": "two", "share_link": "https://google.test/search?htidocid=two&source=test"}, "serpapi"),
        ]
        self.assertEqual(len(deduplicate(jobs)), 2)

    def test_location_filter_excludes_bengaluru_for_ahmedabad(self):
        jobs = [{"location": "Ahmedabad, Gujarat", "remote": False}, {"location": "Bengaluru, Karnataka", "remote": False}, {"location": "Remote, India", "remote": True}]
        self.assertEqual(len(filter_by_location(jobs, "Ahmedabad")), 2)

    def test_serpapi_query_is_location_first(self):
        params = build_job_search_params("Machine Learning Engineer", "Ahmedabad")
        self.assertEqual(params["q"], "Machine Learning Engineer jobs in Ahmedabad")
        self.assertEqual(params["gl"], "in")

    def test_workopia_mcp_response_parser(self):
        payload = {"result": {"content": [{"json": {"jobs": [{"title": "Data Engineer"}]}}]}}
        self.assertEqual(WorkopiaProvider.parse_response(payload), [{"title": "Data Engineer"}])

    def test_verified_contact_never_accepts_guessed_email(self):
        evidence = "Careers team: careers@acme.com\n"
        self.assertEqual(verified_email_from_source("careers@acme.com", evidence), "careers@acme.com")
        self.assertIsNone(verified_email_from_source("hr@acme.com", evidence))
        self.assertTrue(recruitment_role_supported("careers@acme.com", evidence))

    def test_extended_response_schema_reads_raw_provider_data(self):
        job = Job(id=1, title="Engineer", company="Acme", location="Ahmedabad", source="serpapi", source_url="https://source.test", fingerprint="x", created_at=datetime.now(timezone.utc), raw_data={"external_id": "abc", "apply_url": "https://apply.test", "remote": False, "skills": ["Python"]})
        result = JobResponse.model_validate(job)
        self.assertEqual(result.apply_url, "https://apply.test")
        self.assertEqual(result.skills, ["Python"])

    async def test_fallback_uses_serpapi_when_primary_is_disabled(self):
        class FakeSerp:
            enabled = True
            name = "serpapi"
            async def search(self, query, location, limit):
                return [{"title": "Python Developer", "company_name": "Acme", "location": "Ahmedabad", "source": "serpapi", "remote": False}]
        with patch("backend.app.services.jobs.orchestrator.SerpApiProvider", return_value=FakeSerp()), patch("backend.app.services.jobs.orchestrator.WorkopiaProvider") as workopia, patch("backend.app.services.jobs.orchestrator.JobSpyProvider") as jobspy, patch("backend.app.services.jobs.orchestrator.ApifyProvider") as apify:
            workopia.return_value.enabled = False
            jobspy.return_value.enabled = False
            apify.return_value.enabled = False
            outcome = await search_jobs("Python Developer", "Ahmedabad")
        self.assertEqual(outcome.sources, {"serpapi": 1})
        self.assertEqual(len(outcome.jobs), 1)


if __name__ == "__main__":
    unittest.main()
