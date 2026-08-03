"""Cross-backend automation workflows."""

from .sparam_compare import SParamTrace, compare_traces, load_sparam_trace
from .backend_summary import build_backend_summary, write_backend_summary
from .verdict_summary import build_verdict_summary, write_verdict_summary

__all__ = [
    "SParamTrace",
    "build_backend_summary",
    "build_verdict_summary",
    "compare_traces",
    "load_sparam_trace",
    "write_backend_summary",
    "write_verdict_summary",
]
