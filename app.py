import streamlit as st
from services.hindsight_service import retain_incident, recall_incidents


st.set_page_config(
    page_title="RecallOps",
    page_icon="🧠",
    layout="wide"
)


st.title("🧠 RecallOps")
st.caption("The Self-Learning Incident Response Intelligence System")


st.markdown(
    """
RecallOps uses organizational incident memory to help engineers diagnose
production incidents using previous incidents, root causes, successful
resolutions, failed fixes, and outcomes.
"""
)


if "analysis" not in st.session_state:
    st.session_state.analysis = None

if "memory" not in st.session_state:
    st.session_state.memory = None


st.sidebar.header("Incident Details")

service = st.sidebar.text_input(
    "Service",
    value="Payment Gateway"
)

severity = st.sidebar.selectbox(
    "Severity",
    ["Low", "Medium", "High", "Critical"],
    index=2
)

incident_description = st.sidebar.text_area(
    "Incident Description",
    value="Payment API is returning 503 errors during peak traffic."
)

metrics = st.sidebar.text_area(
    "System Metrics",
    value="CPU=92%, Memory=78%, Latency=4.2s, Error Rate=18%"
)

logs = st.sidebar.text_area(
    "Relevant Logs",
    value="HTTP 503 responses increased after a sudden traffic spike. Payment requests are failing intermittently."
)

root_cause = st.sidebar.text_area(
    "Known Root Cause",
    value="Connection pool exhaustion due to sudden traffic increase."
)

resolution = st.sidebar.text_area(
    "Successful Resolution",
    value="Increased DB connection pool size and restarted payment service."
)

outcome = st.sidebar.text_area(
    "Outcome",
    value="Error rate reduced from 18% to 1% and latency returned to normal."
)

failed_fixes = st.sidebar.text_area(
    "Failed Fixes",
    value="Restarting the service alone did not resolve the issue."
)


def clean_text(value):
    if value is None:
        return ""

    return str(value).strip()


def get_memory_text(result):
    if result is None:
        return ""

    if isinstance(result, str):
        return result

    if isinstance(result, dict):
        for key in [
            "text",
            "content",
            "memory",
            "chunk",
            "description",
            "result"
        ]:
            if key in result and result[key]:
                return str(result[key])

        return str(result)

    return str(result)


def extract_memory(results):
    memories = []

    if results is None:
        return memories

    if isinstance(results, dict):
        possible_items = (
            results.get("results")
            or results.get("memories")
            or results.get("items")
            or results.get("data")
        )

        if possible_items:
            results = possible_items
        else:
            results = [results]

    if not isinstance(results, list):
        results = [results]

    for item in results:
        text = get_memory_text(item)

        if text:
            memories.append(text[:1500])

    return memories


def find_memory_value(memory, labels):
    memory_lower = memory.lower()

    for label in labels:
        label_lower = label.lower()

        if label_lower in memory_lower:
            start = memory_lower.find(label_lower)

            section = memory[start:]

            lines = section.splitlines()

            if lines:
                first_line = lines[0]

                if ":" in first_line:
                    value = first_line.split(":", 1)[1].strip()

                    if value:
                        return value

    return None


def build_incident_dna(
    service,
    severity,
    description,
    metrics,
    logs,
    memories
):
    historical_context = (
        "Historical incidents were retrieved from organizational memory."
        if memories
        else
        "No matching historical incidents were retrieved."
    )

    return {
        "Service": service,
        "Severity": severity,
        "Symptoms": description,
        "System Metrics": metrics,
        "Observed Logs": logs,
        "Historical Context": historical_context
    }


def build_differential_diagnosis(
    description,
    metrics,
    logs,
    memories
):
    candidates = []

    description_lower = description.lower()
    logs_lower = logs.lower()
    metrics_lower = metrics.lower()

    combined = (
        description_lower
        + " "
        + logs_lower
        + " "
        + metrics_lower
    )

    if "503" in combined:
        candidates.append(
            (
                "Connection pool exhaustion",
                "Strong match with the current HTTP 503 symptom."
            )
        )

    if "traffic spike" in combined or "peak traffic" in combined:
        candidates.append(
            (
                "Sudden traffic increase",
                "Traffic increase can create resource and connection pressure."
            )
        )

    if "latency" in combined:
        candidates.append(
            (
                "Backend resource saturation",
                "Elevated latency indicates possible backend pressure."
            )
        )

    if "error rate" in combined:
        candidates.append(
            (
                "Service overload",
                "The elevated error rate is consistent with service overload."
            )
        )

    historical_root_causes = []

    for memory in memories:
        root = find_memory_value(
            memory,
            [
                "Root Cause:",
                "root cause:",
                "Root cause"
            ]
        )

        if root:
            historical_root_causes.append(root)

    return candidates, historical_root_causes


def build_failed_fix_memory(
    failed_fixes,
    memories
):
    failures = []

    if failed_fixes:
        failures.append(
            {
                "Attempt": "Previously attempted fix",
                "Result": failed_fixes
            }
        )

    for memory in memories:
        memory_lower = memory.lower()

        if "failed fix" in memory_lower:
            value = find_memory_value(
                memory,
                [
                    "Failed Fixes:",
                    "Failed Fix:",
                    "failed fixes:"
                ]
            )

            if value:
                failures.append(
                    {
                        "Attempt": "Historical failed fix",
                        "Result": value
                    }
                )

    return failures


def build_timeline(
    description,
    logs,
    metrics,
    resolution,
    outcome
):
    timeline = [
        ("1. Initial condition", description),
        ("2. Trigger / signal", logs),
        ("3. System impact", metrics),
        ("4. Corrective action", resolution),
        ("5. Result", outcome)
    ]

    return timeline


def build_preventive_intelligence(
    service,
    metrics,
    logs,
    memories
):
    actions = []

    combined = (
        metrics.lower()
        + " "
        + logs.lower()
    )

    if "traffic" in combined:
        actions.append(
            "Monitor traffic growth and establish early-warning thresholds."
        )

    if "503" in combined:
        actions.append(
            "Monitor HTTP 5xx responses and trigger investigation when they increase."
        )

    if "latency" in combined:
        actions.append(
            "Track latency trends to detect degradation before widespread failures."
        )

    if "connection" in combined or "pool" in combined:
        actions.append(
            "Monitor database connection-pool utilization and exhaustion risk."
        )

    if not actions:
        actions.append(
            "Use historical incidents to identify recurring signals and preventive actions."
        )

    if memories:
        actions.append(
            "Compare future incidents against this organization's historical incident memory."
        )

    return actions


def build_runbook(
    service,
    description,
    metrics,
    logs,
    memories
):
    steps = [
        f"1. Confirm the {service} incident symptoms and affected API.",
        "2. Check HTTP 5xx/error-rate trends.",
        "3. Compare current latency, CPU, memory, and traffic with historical incidents.",
        "4. Inspect backend/database connection-pool utilization.",
        "5. Compare the incident with retrieved organizational memory.",
        "6. Avoid repeating previously failed fixes without checking their historical outcome.",
        "7. Apply the historically successful resolution when the current evidence matches.",
        "8. Verify error rate and latency after remediation.",
        "9. Record the final root cause, resolution, and outcome back into organizational memory."
    ]

    return steps


def render_section_title(title):
    st.markdown(f"### {title}")


def analyze_incident():
    query = f"""
Production incident investigation.

Service: {service}
Severity: {severity}

Incident:
{incident_description}

Metrics:
{metrics}

Logs:
{logs}

Find historical incidents, root causes, successful fixes,
failed fixes, and outcomes that are relevant to this incident.
"""

    with st.spinner("Recalling organizational memory..."):
        recalled = recall_incidents(query)

    memories = extract_memory(recalled)

    dna = build_incident_dna(
        service,
        severity,
        incident_description,
        metrics,
        logs,
        memories
    )

    candidates, historical_root_causes = build_differential_diagnosis(
        incident_description,
        metrics,
        logs,
        memories
    )

    failed_memory = build_failed_fix_memory(
        failed_fixes,
        memories
    )

    timeline = build_timeline(
        incident_description,
        logs,
        metrics,
        resolution,
        outcome
    )

    preventive = build_preventive_intelligence(
        service,
        metrics,
        logs,
        memories
    )

    runbook = build_runbook(
        service,
        incident_description,
        metrics,
        logs,
        memories
    )

    st.session_state.analysis = {
        "dna": dna,
        "candidates": candidates,
        "historical_root_causes": historical_root_causes,
        "failed_memory": failed_memory,
        "timeline": timeline,
        "preventive": preventive,
        "runbook": runbook
    }

    st.session_state.memory = memories


def store_incident():
    with st.spinner("Storing incident in organizational memory..."):
        result = retain_incident(
            service=service,
            description=incident_description,
            metrics=metrics,
            logs=logs,
            root_cause=root_cause,
            resolution=resolution,
            outcome=outcome,
            failed_fixes=failed_fixes
        )

    st.success("Incident successfully stored in Hindsight organizational memory.")

    return result


col1, col2 = st.columns(2)

with col1:
    analyze_button = st.button(
        "🔍 Analyze Incident",
        use_container_width=True
    )

with col2:
    store_button = st.button(
        "🧠 Store Incident Memory",
        use_container_width=True
    )


if analyze_button:
    try:
        analyze_incident()

    except Exception as e:
        st.error(
            f"Hindsight memory recall failed: {str(e)}"
        )


if store_button:
    try:
        store_incident()

    except Exception as e:
        st.error(
            f"Incident memory storage failed: {str(e)}"
        )


analysis = st.session_state.analysis
memories = st.session_state.memory


if analysis:

    st.divider()

    render_section_title("🧬 Incident DNA")

    dna = analysis["dna"]

    dna_col1, dna_col2 = st.columns(2)

    with dna_col1:
        st.write(f"**Service:** {dna['Service']}")
        st.write(f"**Severity:** {dna['Severity']}")
        st.write(f"**Symptoms:** {dna['Symptoms']}")

    with dna_col2:
        st.write(f"**System Metrics:** {dna['System Metrics']}")
        st.write(f"**Observed Logs:** {dna['Observed Logs']}")
        st.write(f"**Historical Context:** {dna['Historical Context']}")


    st.divider()

    render_section_title("🔎 Differential Diagnosis")

    candidates = analysis["candidates"]
    historical_root_causes = analysis["historical_root_causes"]

    if candidates:
        for name, reason in candidates:
            st.markdown(
                f"**Possible cause:** {name}"
            )
            st.write(reason)

    else:
        st.info(
            "No specific diagnostic pattern was identified from the current incident details."
        )

    if historical_root_causes:
        st.markdown("**Historical root-cause evidence:**")

        for root in historical_root_causes:
            st.write(f"- {root}")

    elif memories:
        st.info(
            "Historical incidents were retrieved, but a clearly labeled root cause was not found in the returned memory."
        )


    st.divider()

    render_section_title("🚫 Failed-Fix Memory")

    failed_memory = analysis["failed_memory"]

    if failed_memory:

        for item in failed_memory:

            st.markdown(
                f"**{item['Attempt']}**"
            )

            st.write(
                item["Result"]
            )

    else:
        st.info(
            "No failed fix was recorded for this incident."
        )


    st.divider()

    render_section_title("⏱️ Timeline Reconstruction")

    timeline = analysis["timeline"]

    for step, value in timeline:

        st.markdown(
            f"**{step}**"
        )

        st.write(value)


    st.divider()

    render_section_title("🛡️ Preventive Intelligence")

    preventive = analysis["preventive"]

    for action in preventive:

        st.markdown(
            f"- {action}"
        )


    st.divider()

    render_section_title("📖 Investigation Runbook")

    runbook = analysis["runbook"]

    for step in runbook:

        st.markdown(
            f"- {step}"
        )


    st.divider()

    render_section_title("🧠 Organizational Memory")

    if memories:

        st.success(
            f"{len(memories)} historical memory record(s) retrieved."
        )

        for index, memory in enumerate(memories, start=1):

            with st.expander(
                f"Historical Incident {index}"
            ):
                st.write(memory)

    else:

        st.warning(
            "No matching historical memory was retrieved from Hindsight."
        )


    st.divider()

    render_section_title("📊 Incident Summary")

    summary_col1, summary_col2, summary_col3 = st.columns(3)

    with summary_col1:
        st.metric(
            "Severity",
            severity
        )

    with summary_col2:
        st.metric(
            "Historical Memories",
            len(memories) if memories else 0
        )

    with summary_col3:
        st.metric(
            "Diagnostic Signals",
            len(analysis["candidates"])
        )


st.divider()

st.caption(
    "RecallOps — Every incident makes the next one easier."
)