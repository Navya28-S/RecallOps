import os

from hindsight_client import Hindsight


HINDSIGHT_URL = os.getenv(
    "HINDSIGHT_URL",
    "http://localhost:8888"
)

BANK_ID = os.getenv(
    "HINDSIGHT_BANK_ID",
    "recallops"
)


client = Hindsight(
    base_url=HINDSIGHT_URL
)


def retain_incident(
    service,
    description,
    metrics,
    logs,
    root_cause,
    resolution,
    outcome,
    failed_fixes=None
):
    content = f"""
Production Incident

Service: {service}

Incident Description:
{description}

System Metrics:
{metrics}

Relevant Logs:
{logs}

Root Cause:
{root_cause}

Resolution:
{resolution}

Outcome:
{outcome}

Failed Fixes:
{failed_fixes if failed_fixes else "None"}
"""

    return client.retain(
        bank_id=BANK_ID,
        content=content,
        context="RecallOps production incident memory",
        metadata={
            "service": service,
            "type": "production_incident"
        },
        tags=[
            "incident",
            service
        ]
    )


def recall_incidents(query):
    return client.recall(
        bank_id=BANK_ID,
        query=query,
        max_tokens=500,
        budget="low",
        include_entities=False,
        include_chunks=False
    )


def reflect_on_incident(query):
    return client.reflect(
        bank_id=BANK_ID,
        query=query,
        budget="low",
        max_tokens=300,
        include_facts=False
    )