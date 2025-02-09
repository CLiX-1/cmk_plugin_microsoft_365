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
# These are used for the check "Microsoft 365 Service Health".


from cmk.graphing.v1 import Title
from cmk.graphing.v1.graphs import Graph, MinimalRange
from cmk.graphing.v1.metrics import (
    Color,
    DecimalNotation,
    Metric,
    StrictPrecision,
    Unit,
)
from cmk.graphing.v1.perfometers import Closed, FocusRange, Perfometer, Stacked, Open

UNIT_COUNTER = Unit(DecimalNotation(""), StrictPrecision(0))

metric_m365_service_health_count_incident = Metric(
    name="m365_service_health_count_incident",
    title=Title("Incident"),
    unit=UNIT_COUNTER,
    color=Color.RED,
)

metric_m365_service_health_count_advisory = Metric(
    name="m365_service_health_count_advisory",
    title=Title("Advisory"),
    unit=UNIT_COUNTER,
    color=Color.YELLOW,
)

graph_m365_service_health_count = Graph(
    name="m365_service_health_count",
    title=Title("M365 service issues"),
    minimal_range=MinimalRange(0, 5),
    simple_lines=[
        "m365_service_health_count_incident",
        "m365_service_health_count_advisory",
    ],
    optional=[
        "m365_service_health_count_incident",
        "m365_service_health_count_advisory",
    ],
)

perfometer_m365_service_health_count = Stacked(
    name="name",
    lower=Perfometer(
        name="advisory",
        focus_range=FocusRange(
            Closed(0),
            Open(5),
        ),
        segments=["m365_service_health_count_advisory"],
    ),
    upper=Perfometer(
        name="incident",
        focus_range=FocusRange(
            Closed(0),
            Open(5),
        ),
        segments=["m365_service_health_count_incident"],
    ),
)
