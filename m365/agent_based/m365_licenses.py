#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# Copyright (C) 2024  Christopher Pommer <cp.software@outlook.de>

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Metric,
    render,
    Result,
    Service,
    State,
    StringTable,
)


@dataclass(frozen=True)
class LicenseInfo:
    lic_sku_id: str
    lic_sku_name: str
    lic_state: str
    lic_units_consumed: int
    lic_units_enabled: int
    lic_units_lockedout: int
    lic_units_suspended: int
    lic_units_warning: int


Section = Mapping[str, Sequence[LicenseInfo]]

# Example data from special agent:
# <<<m365_licenses:sep(0)>>>
# [
#     {
#         "lic_sku_id": "c5928f49-12ba-48f7-ada3-0d743a3601d5",
#         "lic_sku_name": "VISIOCLIENT",
#         "lic_state": "Enabled"
#         "lic_units_consumed": 44,
#         "lic_units_enabled": 50,
#         "lic_units_lockedout": 0,
#         "lic_units_suspended": 0,
#         "lic_units_warning": 5
#     },
#     {
#         "lic_sku_id": "3dd6cf57-d688-4eed-ba52-9e40b5468c3e",
#         "lic_sku_name": "THREAT_INTELLIGENCE",
#         "lic_state": "Suspended"
#         "lic_units_consumed": 0,
#         "lic_units_enabled": 0,
#         "lic_units_lockedout": 0,
#         "lic_units_suspended": 200,
#         "lic_units_warning": 0
#     },
#     ...
# ]


def parse_m365_licenses(string_table: StringTable) -> Section:
    parsed = {}
    for item in json.loads("".join(string_table[0])):
        parsed[item["lic_sku_name"]] = item
    return parsed


def discover_m365_licenses(section: Section) -> DiscoveryResult:
    for group in section:
        yield Service(item=group)


def check_m365_licenses(item: str, params: Mapping[str, Any], section: Section) -> CheckResult:
    license = section.get(item)
    if not license:
        return

    lic_sku_id = license["lic_sku_id"]
    lic_state = license["lic_state"]
    lic_units_consumed = license["lic_units_consumed"]
    lic_units_enabled = license["lic_units_enabled"]
    lic_units_lockedout = license["lic_units_lockedout"]
    lic_units_suspended = license["lic_units_suspended"]
    lic_units_warning = license["lic_units_warning"]

    lic_units_total = lic_units_enabled + lic_units_warning

    lic_units_consumed_pct = round(lic_units_consumed / lic_units_total * 100, 2)
    lic_units_available = lic_units_total - lic_units_consumed

    result_level = ""
    result_state = State.OK
    levels_consumed_abs = (None, None)
    levels_consumed_pct = (None, None)
    params_levels_available = params["lic_unit_available_lower"]
    if params_levels_available[1][0] == "fixed":
        warning_level, critical_level = params_levels_available[1][1]

        if params_levels_available[0] == "lic_unit_available_lower_pct":
            levels_consumed_pct = (100 - warning_level, 100 - critical_level)
            available_percent = lic_units_available / lic_units_total * 100

            if available_percent < critical_level:
                result_state = State.CRIT
            elif available_percent < warning_level:
                result_state = State.WARN

            result_level = (
                f" (warn/crit below {render.percent(warning_level)}/"
                f"{render.percent(critical_level)} available)"
            )

        else:
            levels_consumed_abs = (
                lic_units_total - warning_level,
                lic_units_total - critical_level,
            )

            if lic_units_consumed > levels_consumed_abs[1]:
                result_state = State.CRIT
            elif lic_units_consumed > levels_consumed_abs[0]:
                result_state = State.WARN

            result_level = f" (warn/crit below {warning_level}/{critical_level} available)"

    result_summary = (
        f"Consumed: {render.percent(lic_units_consumed_pct)} - "
        f"{lic_units_consumed} of {lic_units_total}"
        f", Available: {lic_units_available}{result_level}"
        f"{', Warning: ' + str(lic_units_warning) if lic_units_warning > 0 else ''}"
        f", License state: {lic_state}"
    )

    result_details = (
        f"License ID: {lic_sku_id}"
        f"\n - Enabled (Active): {lic_units_enabled}"
        f"\n - Consumed (Used): {lic_units_consumed}"
        f"\n - LockedOut (Canceled): {lic_units_lockedout}"
        f"\n - Suspended (Inactive): {lic_units_suspended}"
        f"\n - Warning (In grace period): {lic_units_warning}"
    )

    yield Result(
        state=result_state,
        summary=result_summary,
        details=result_details,
    )

    yield Metric(name="m365_licenses_total", value=lic_units_total)
    yield Metric(name="m365_licenses_enabled", value=lic_units_enabled)
    yield Metric(
        name="m365_licenses_consumed", value=lic_units_consumed, levels=levels_consumed_abs
    )
    yield Metric(
        name="m365_licenses_consumed_pct", value=lic_units_consumed_pct, levels=levels_consumed_pct
    )
    yield Metric(name="m365_licenses_available", value=lic_units_available)
    yield Metric(name="m365_licenses_warning", value=lic_units_warning)


agent_section_m365_licenses = AgentSection(
    name="m365_licenses",
    parse_function=parse_m365_licenses,
)


check_plugin_m365_licenses = CheckPlugin(
    name="m365_licenses",
    service_name="M365 SKU %s",
    discovery_function=discover_m365_licenses,
    check_function=check_m365_licenses,
    check_ruleset_name="m365_licenses",
    check_default_parameters={
        "lic_unit_available_lower": ("lic_unit_available_lower_pct", ("fixed", (10.0, 5.0)))
    },
)
