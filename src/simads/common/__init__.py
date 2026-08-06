"""Common automation primitives shared by simulator backends."""

from simads.common.commands import CommandPlan
from simads.common.jsonio import json_default, read_json_object, write_json

__all__ = ["CommandPlan", "json_default", "read_json_object", "write_json"]
