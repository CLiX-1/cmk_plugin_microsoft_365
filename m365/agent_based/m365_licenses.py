#!/usr/bin/env python3
# -*- coding: utf-8; py-indent-offset: 4; max-line-length: 100 -*-

# Copyright (C) 2024, 2025  Christopher Pommer <cp.software@outlook.de>

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


####################################################################################################
# Checkmk check plugin for monitoring the licenses from Microsoft 365.
# The plugin works with data from the Microsoft 365 special agent (m365).

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


import json
from collections.abc import Mapping
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
class License:
    lic_sku_id: str
    lic_sku_name: str
    lic_state: str
    lic_units_consumed: int
    lic_units_enabled: int
    lic_units_lockedout: int
    lic_units_suspended: int
    lic_units_warning: int


Section = Mapping[str, License]


def parse_m365_licenses(string_table: StringTable) -> Section:
    parsed = {}
    for item in json.loads("".join(string_table[0])):
        parsed[item["lic_sku_name"]] = License(**item)
    return parsed


def discover_m365_licenses(section: Section) -> DiscoveryResult:
    for group in section:
        yield Service(item=group)


def check_m365_licenses(item: str, params: Mapping[str, Any], section: Section) -> CheckResult:
    license = section.get(item)
    if license is None:
        return

    # Total available licenses are the sum of enabled and warning.
    # Warning are licenses in a grace period.
    lic_units_total = license.lic_units_enabled + license.lic_units_warning

    lic_units_consumed_pct = round(license.lic_units_consumed / lic_units_total * 100, 2)

    # The count of the remaining available licenses will be negative if more licenses are assigned
    # than total available.
    lic_units_available_raw = lic_units_total - license.lic_units_consumed
    # To display the correct remaining available value, the minimum will be 0, if the count is
    # negative.
    lic_units_available = max(0, lic_units_available_raw)

    params_levels_available_lower = params["lic_unit_available_lower"]

    result_level = ""
    result_state = State.OK
    levels_consumed_abs = (None, None)
    levels_consumed_pct = (None, None)

    # If the parameter "Only critical if over-licensed" is configured, then only the
    # over-assignment of licenses is checked.
    # Otherwise it will be checked if thresholds are configured.
    if params_levels_available_lower[0] == "lic_overlicensed":
        if lic_units_available_raw < 0:
            result_state = State.CRIT
    elif params_levels_available_lower[1][1]:
        # Extract the threshold values from the configured parameters.
        warning_level, critical_level = params_levels_available_lower[1][1]

        # Decide whether to configure the thresholds as absolute or percentage values.
        if params_levels_available_lower[0] == "lic_unit_available_lower_pct":
            # This value is used to display the thresholds on the graphs.
            levels_consumed_pct = (100 - warning_level, 100 - critical_level)

            available_pct = lic_units_available_raw / lic_units_total * 100

            if available_pct < critical_level:
                result_state = State.CRIT
            elif available_pct < warning_level:
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

            if license.lic_units_consumed > levels_consumed_abs[1]:
                result_state = State.CRIT
            elif license.lic_units_consumed > levels_consumed_abs[0]:
                result_state = State.WARN

            result_level = f" (warn/crit below {warning_level}/{critical_level} available)"

    # This content will be used as the check result summary.
    result_summary = (
        f"Consumed: {render.percent(lic_units_consumed_pct)} - "
        f"{license.lic_units_consumed} of {lic_units_total}"
        f", Available: {lic_units_available}{result_level}"
        f"{', Warning: ' + str(license.lic_units_warning) if license.lic_units_warning > 0 else ''}"
        f", License state: {license.lic_state}"
    )

    # Build a list of license details to be displayed in the check result details.
    result_details = "\n".join(
        [
            f"License ID: {license.lic_sku_id}",
            f"Enabled (Active): {license.lic_units_enabled}",
            f"Consumed (Used): {license.lic_units_consumed}",
            f"LockedOut (Canceled): {license.lic_units_lockedout}",
            f"Suspended (Inactive): {license.lic_units_suspended}",
            f"Warning (In grace period): {license.lic_units_warning}",
        ]
    )

    yield Result(
        state=result_state,
        summary=result_summary,
        details=result_details,
    )

    yield Metric(name="m365_licenses_total", value=lic_units_total)
    yield Metric(name="m365_licenses_enabled", value=license.lic_units_enabled)
    yield Metric(
        name="m365_licenses_consumed",
        value=license.lic_units_consumed,
        levels=levels_consumed_abs,
    )
    yield Metric(
        name="m365_licenses_consumed_pct",
        value=lic_units_consumed_pct,
        levels=levels_consumed_pct,
    )
    yield Metric(name="m365_licenses_available", value=lic_units_available)
    yield Metric(name="m365_licenses_warning", value=license.lic_units_warning)


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
