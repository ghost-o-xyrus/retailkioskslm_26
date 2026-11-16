"""Which machine a run or benchmark ran on, so timings from different machines are never compared.

The label is the SLM_MACHINE environment variable if set (the Kaggle runner sets "kaggle-cpu" or "kaggle-gpu"),
else "local". Quality numbers do not depend on the machine; latency, RAM and tokens per second do.
"""

import os
import platform


def machine_info():
    return {"label": os.environ.get("SLM_MACHINE", "local"), "host": platform.node(), "os": platform.platform(),
            "cpu": platform.processor() or platform.machine(), "cores": os.cpu_count()}


def label(meta):
    """The machine label stored in a run_meta / summary dict; runs made before this field existed were local."""
    return ((meta or {}).get("machine") or {}).get("label", "local")
