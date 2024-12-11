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
from collections.abc import Sequence
from dataclasses import dataclass

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    State,
    StringTable,
)


@dataclass(frozen=True)
class GroupInfo:
    group_id: str
    group_name: str


Section = Sequence[GroupInfo]

# Example data from special agent:
# <<<m365_group_based_licensing:sep(0)>>>
# [
#     {
#         "group_id": "00000000-0000-0000-0000-000000000000",
#         "group_name": "Group name 1",
#     },
#     {
#         "group_id": "00000000-0000-0000-0000-000000000000",
#         "group_name": "Group name 2",
#     },
#     ...
# ]


def parse_m365_group_based_licensing(string_table: StringTable) -> Section:
    parsed = json.loads(string_table[0][0])
    return parsed


def discover_m365_group_based_licensing(section: Section) -> DiscoveryResult:
    yield Service()


def check_m365_group_based_licensing(section: Section) -> CheckResult:
    groups = section
    if not groups:
        yield Result(
            state=State.OK,
            summary="No groups with errors",
        )

        return

    result_summary = f"Groups with errors: {len(groups)}"

    result_details_list = []
    for group in groups:
        group_details = f"Group name: {group["group_name"]}\n - ID: {group["group_id"]}"
        result_details_list.append(group_details)

    result_details = "\n\n".join(result_details_list)

    yield Result(
        state=State.CRIT,
        summary=result_summary,
        details=result_details,
    )


agent_section_m365_group_based_licensing = AgentSection(
    name="m365_group_based_licensing",
    parse_function=parse_m365_group_based_licensing,
)


check_plugin_m365_group_based_licensing = CheckPlugin(
    name="m365_group_based_licensing",
    service_name="M365 group-based licensing",
    discovery_function=discover_m365_group_based_licensing,
    check_function=check_m365_group_based_licensing,
)
