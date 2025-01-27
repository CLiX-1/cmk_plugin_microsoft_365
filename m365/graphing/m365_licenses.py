#!/usr/bin/env python3
# -*- coding: utf-8; py-indent-offset: 4; max-line-length: 100 -*-

# Copyright (C) 2025  Christopher Pommer <cp.software@outlook.de>

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


from cmk.graphing.v1 import Title
from cmk.graphing.v1.graphs import Graph, MinimalRange
from cmk.graphing.v1.metrics import (
    Color,
    CriticalOf,
    DecimalNotation,
    Metric,
    StrictPrecision,
    Unit,
    WarningOf,
)
from cmk.graphing.v1.perfometers import Closed, FocusRange, Perfometer

UNIT_COUNTER = Unit(DecimalNotation(""), StrictPrecision(0))
UNIT_PERCENTAGE = Unit(DecimalNotation("%"))

metric_m365_licenses_available = Metric(
    name="m365_licenses_available",
    title=Title("Available"),
    unit=UNIT_COUNTER,
    color=Color.LIGHT_GRAY,
)

metric_m365_licenses_consumed = Metric(
    name="m365_licenses_consumed",
    title=Title("Consumed"),
    unit=UNIT_COUNTER,
    color=Color.CYAN,
)

metric_m365_licenses_consumed_pct = Metric(
    name="m365_licenses_consumed_pct",
    title=Title("Usage"),
    unit=UNIT_PERCENTAGE,
    color=Color.BLUE,
)

metric_m365_licenses_enabled = Metric(
    name="m365_licenses_enabled",
    title=Title("Enabled"),
    unit=UNIT_COUNTER,
    color=Color.PURPLE,
)

metric_m365_licenses_total = Metric(
    name="m365_licenses_total",
    title=Title("Total (Enabled + Warning)"),
    unit=UNIT_COUNTER,
    color=Color.GREEN,
)

metric_m365_licenses_warning = Metric(
    name="m365_licenses_warning",
    title=Title("Warning"),
    unit=UNIT_COUNTER,
    color=Color.BROWN,
)

graph_m365_license_count = Graph(
    name="m365_license_count",
    title=Title("License count"),
    compound_lines=[
        "m365_licenses_consumed",
        "m365_licenses_available",
    ],
    simple_lines=[
        "m365_licenses_total",
        "m365_licenses_enabled",
        "m365_licenses_warning",
        WarningOf("m365_licenses_consumed"),
        CriticalOf("m365_licenses_consumed"),
    ],
)

graph_m365_license_usage = Graph(
    name="m365_license_usage",
    title=Title("License usage"),
    minimal_range=MinimalRange(0, 100),
    simple_lines=[
        "m365_licenses_consumed_pct",
        WarningOf("m365_licenses_consumed_pct"),
        CriticalOf("m365_licenses_consumed_pct"),
    ],
)

perfometer_m365_licenses_consumed_pct = Perfometer(
    name="m365_licenses_consumed_pct",
    focus_range=FocusRange(Closed(0), Closed(100)),
    segments=["m365_licenses_consumed_pct"],
)
