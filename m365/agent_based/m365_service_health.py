#!/usr/bin/env python3
# -*- coding: utf-8; py-indent-offset: 4; max-line-length: 100 -*-

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


####################################################################################################
# Checkmk check plugin for monitoring the service health from Microsoft 365.
# The plugin works with data from the Microsoft 365 Special Agent (m365).

# Example data from special agent:
# <<<m365_service_health:sep(0)>>>
# [
#     {
#         "service_name": "Exchange Online",
#         "service_status": "serviceDegradation",
#         "service_issues": [
#             {
#                 "issue_title": "Some users may be unable to view group membership",
#                 "issue_start": "1970-00-00T01:00:00Z",
#                 "issue_feature": "OWA - poor customer experience",
#                 "issue_classification": "advisory",
#                 "issue_id": "EX785433"
#             }
#         ]
#     },
#     {
#         "service_name": "Microsoft Entra",
#         "service_status": "serviceOperational",
#         "service_issues": []
#     },
#     ...
# ]


import json
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any, List, TypedDict

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


class ServiceIssue(TypedDict):
    issue_title: str
    issue_start: str
    issue_feature: str
    issue_classification: str
    issue_id: str


@dataclass(frozen=True)
class MicrosoftService:
    service_name: str
    service_status: str
    service_issues: List[ServiceIssue]


Section = Mapping[str, MicrosoftService]


def parse_m365_service_health(string_table: StringTable) -> Section:
    parsed = {}
    for item in json.loads("".join(string_table[0])):
        parsed[item["service_name"]] = MicrosoftService(**item)
    return parsed


def discover_m365_service_health(section: Section) -> DiscoveryResult:
    for group in section:
        yield Service(item=group)


def check_m365_service_health(
    item: str, params: Mapping[str, Any], section: Section
) -> CheckResult:
    m365_service = section.get(item)
    if not m365_service:
        return

    service_issues = m365_service.service_issues

    issue_classification_dict = {}
    if service_issues:
        severity_list = []
        for issue in service_issues:
            classification = issue["issue_classification"]
            if classification in issue_classification_dict:
                issue_classification_dict[classification] += 1
            else:
                issue_classification_dict[classification] = 1
            severity_list.append(params.get(classification, 0))

        result_summary = (
            f"Incident: {issue_classification_dict.get('incident', 0)}, "
            f"Advisory: {issue_classification_dict.get('advisory', 0)}, "
            f"Status: {m365_service.service_status}"
        )

        result_details_list = []
        for issue in service_issues:
            issue_start = issue.get("issue_start")
            issue_start_datetime = datetime.fromisoformat(issue_start)
            issue_start_timestamp = issue_start_datetime.timestamp()
            issue_classification = issue["issue_classification"].capitalize()
            issue_details = (
                f"Start time: {render.datetime(issue_start_timestamp)}"
                f"\n - Type: {issue_classification}"
                f"\n - Feature: {issue.get('issue_feature')}"
                f"\n - Title: {issue.get('issue_title')} ({issue.get('issue_id')})"
            )
            result_details_list.append(issue_details)

        result_details = "\n\n".join(result_details_list)

        yield Result(
            state=State.worst(*severity_list),
            summary=f"{result_summary}",
            details=f"{result_details}",
        )

    else:
        yield Result(
            state=State.OK,
            summary="No open issues",
        )

    yield Metric(
        name="m365_service_health_count_incident",
        value=issue_classification_dict.get("incident", 0),
    )
    yield Metric(
        name="m365_service_health_count_advisory",
        value=issue_classification_dict.get("advisory", 0),
    )


agent_section_m365_service_health = AgentSection(
    name="m365_service_health",
    parse_function=parse_m365_service_health,
)


check_plugin_m365_service_health = CheckPlugin(
    name="m365_service_health",
    service_name="M365 health %s",
    discovery_function=discover_m365_service_health,
    check_function=check_m365_service_health,
    check_ruleset_name="m365_service_health",
    check_default_parameters={"incident": 2, "advisory": 1},
)
