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
# CHECKMK CHECK PLUG-IN: Microsoft 365 Service Health
#
# This plug-in generates the Checkmk services and determines their status.
# This file is part of the Microsoft 365 special agent (m365).
####################################################################################################

# Example data from special agent (formatted):
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
class ServiceIssue:
    issue_title: str
    issue_start: str
    issue_feature: str
    issue_classification: str
    issue_id: str


@dataclass(frozen=True)
class MicrosoftService:
    service_name: str
    service_status: str
    service_issues: list[ServiceIssue]


Section = Mapping[str, MicrosoftService]


def parse_m365_service_health(string_table: StringTable) -> Section:
    parsed = {}
    for item in json.loads("".join(string_table[0])):
        service_issues = [ServiceIssue(**issue) for issue in item["service_issues"]]
        parsed[item["service_name"]] = MicrosoftService(
            service_name=item["service_name"],
            service_status=item["service_status"],
            service_issues=service_issues,
        )
    return parsed


def discover_m365_service_health(section: Section) -> DiscoveryResult:
    for group in section:
        yield Service(item=group)


def check_m365_service_health(
    item: str, params: Mapping[str, Any], section: Section
) -> CheckResult:
    m365_service = section.get(item)
    if m365_service is None:
        return

    # Count the issues grouped by issue type and build the severity_list to calculate the
    # overall severity level for the service.
    issue_classification_dict: dict[str, int] = {}
    if m365_service.service_issues:
        issue_severity_list = []
        for issue in m365_service.service_issues:
            classification = issue.issue_classification
            if classification in issue_classification_dict:
                issue_classification_dict[classification] += 1
            else:
                issue_classification_dict[classification] = 1
            issue_severity_list.append(params.get(classification, 0))

        # This content will be used as the check result summary.
        result_summary = (
            f"Incident: {issue_classification_dict.get('incident', 0)}, "
            f"Advisory: {issue_classification_dict.get('advisory', 0)}, "
            f"Status: {m365_service.service_status}"
        )

        health_issue_base_url = (
            "https://admin.microsoft.com/Adminportal/Home#/servicehealth/:/alerts/"
        )

        # Build a list of health issue details to be displayed in the check result details.
        result_details_list = []
        for issue in m365_service.service_issues:
            if issue.issue_start:
                issue_start_timestamp = datetime.fromisoformat(issue.issue_start).timestamp()
                issue_start_render = render.datetime(issue_start_timestamp)
            else:
                issue_start_render = "(Not available)"

            issue_details_list = "\n".join(
                [
                    f"{issue.issue_classification.upper()} ({issue.issue_feature}): {issue.issue_id}",
                    f" - Title: {issue.issue_title}",
                    f" - Start time: {issue_start_render}",
                    f" - Issue URL: {health_issue_base_url}{issue.issue_id}",
                ]
            )
            result_details_list.append(issue_details_list)

        result_details = "\n\n".join(result_details_list)

        yield Result(
            state=State.worst(*issue_severity_list),
            summary=result_summary,
            details=result_details,
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
