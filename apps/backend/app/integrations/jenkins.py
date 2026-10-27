from .http import get_json
from .result import NotConfigured
from ..parsers import job_stats, normalize_builds, summarize_trivy

TREE = "builds[number,result,building,timestamp,duration,url,description]{0,15}"


def _auth(s):
    if not s.jenkins_url:
        raise NotConfigured("JENKINS_URL is not set")
    return (s.jenkins_user, s.jenkins_password) if s.jenkins_user else None


def job_builds(s, job):
    payload = get_json(f"{s.jenkins_url}/job/{job}/api/json", params={"tree": TREE}, auth=_auth(s))
    return normalize_builds(job, payload)


def all_jobs(s):
    """Return per-job builds+stats. A job that errors is reported with its error; all-failed raises."""
    _auth(s)
    jobs, errors = [], []
    for job in s.jenkins_jobs:
        try:
            builds = job_builds(s, job)
            jobs.append({"job": job, "builds": builds, **job_stats(builds), "error": None})
        except Exception as e:  # noqa: BLE001
            errors.append(f"{job}: {e}")
            jobs.append({"job": job, "builds": [], "success": 0, "failed": 0, "avg_duration_ms": None,
                         "latest_image": None, "error": str(e)[:200]})
    if errors and len(errors) == len(s.jenkins_jobs):
        raise RuntimeError("; ".join(errors)[:300])
    return jobs


def trivy_report(s, job, kind):
    """kind: 'fs' or 'image'. Reads the artifact archived by the pipeline from the last completed build."""
    url = f"{s.jenkins_url}/job/{job}/lastCompletedBuild/artifact/reports/trivy-{kind}.json"
    try:
        return summarize_trivy(get_json(url, auth=_auth(s)))
    except Exception as e:  # noqa: BLE001
        if "404" in str(e):
            return None  # no report yet for this job
        raise
