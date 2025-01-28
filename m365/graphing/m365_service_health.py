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
# The graph parameters are part of the Microsoft 365 special agent (m365).


from cmk.graphing.v1 import graphs, metrics, Title

UNIT_COUNTER = metrics.Unit(metrics.DecimalNotation(""), metrics.StrictPrecision(0))

metric_m365_service_health_count_incident = metrics.Metric(
    name="m365_service_health_count_incident",
    title=Title("Incident"),
    unit=UNIT_COUNTER,
    color=metrics.Color.RED,
)

metric_m365_service_health_count_advisory = metrics.Metric(
    name="m365_service_health_count_advisory",
    title=Title("Advisory"),
    unit=UNIT_COUNTER,
    color=metrics.Color.YELLOW,
)

graph_m365_service_health_count = graphs.Graph(
    name="m365_service_health_count",
    title=Title("M365 service issues"),
    minimal_range=graphs.MinimalRange(0, 5),
    simple_lines=[
        "m365_service_health_count_incident",
        "m365_service_health_count_advisory",
    ],
    optional=[
        "m365_service_health_count_incident",
        "m365_service_health_count_advisory",
    ],
)
