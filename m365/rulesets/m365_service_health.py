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
# CHECKMK RULESET: Microsoft 365 Service Health (check plug-in)
#
# This file defines the check plug-in parameters for the "Microsoft Service Health" check.
# The check is part of the Microsoft 365 special agent (m365).
####################################################################################################

from cmk.rulesets.v1 import Help, Title
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    ServiceState,
)
from cmk.rulesets.v1.rule_specs import CheckParameters, HostAndItemCondition, Topic


def _parameter_form_m365_service_health() -> Dictionary:
    return Dictionary(
        title=Title("Check parameters"),
        help_text=Help(
            "Check parameters for the Microsoft 365 service health issues. "
            "Each Microsoft 365 service can have its own set of parameters. "
            "To use this service, you need to set up the <b>Microsoft 365</b> special agent."
        ),
        elements={
            "incident": DictElement(
                parameter_form=ServiceState(
                    title=Title("Severity level incident"),
                    help_text=Help(
                        "Set the severity level of the issue type incident. The default severity "
                        "level is critical."
                    ),
                    prefill=DefaultValue(2),
                ),
            ),
            "advisory": DictElement(
                parameter_form=ServiceState(
                    title=Title("Severity level advisory"),
                    help_text=Help(
                        "Set the severity level of the issue type advisory. The default severity "
                        "level is warning."
                    ),
                    prefill=DefaultValue(1),
                ),
            ),
        },
    )


rule_spec_m365_service_health = CheckParameters(
    name="m365_service_health",
    title=Title("Microsoft 365 Service Health"),
    parameter_form=_parameter_form_m365_service_health,
    topic=Topic.CLOUD,
    condition=HostAndItemCondition(item_title=Title("M365 Service")),
)
