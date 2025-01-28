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
# Checkmk ruleset to set the thresholds for the Microsoft 365 licenses. The ruleset
# allows you to set the lower levels for the number of remaining available Microsoft 365 licenses.
# This ruleset is part of the Microsoft 365 special agent (m365).


from cmk.rulesets.v1 import Help, Title
from cmk.rulesets.v1.form_specs import (
    CascadingSingleChoice,
    CascadingSingleChoiceElement,
    DefaultValue,
    DictElement,
    Dictionary,
    InputHint,
    Integer,
    LevelDirection,
    Percentage,
    SimpleLevels,
)
from cmk.rulesets.v1.rule_specs import CheckParameters, HostAndItemCondition, Topic


def _parameter_form_m365_licenses() -> Dictionary:
    return Dictionary(
        title=Title("Microsoft 365 Licenses"),
        help_text=Help(
            "Check parameters for the Microsoft 365 licenses. Each SKU can have its own set of "
            "parameters. To use this service, you need to set up the <b>Microsoft 365</b> special "
            "agent."
        ),
        elements={
            "lic_unit_available_lower": DictElement(
                parameter_form=CascadingSingleChoice(
                    title=Title("Licenses lower levels"),
                    help_text=Help(
                        "Set lower-level thresholds for the number of remaining available "
                        "Microsoft 365 licenses as absolute or percentage values. "
                        'To ignore the remaining available licenses, Select "Percentage" or '
                        '"Absolute" and "No levels".'
                    ),
                    elements=[
                        CascadingSingleChoiceElement(
                            name="lic_unit_available_lower_pct",
                            title=Title("Percentage"),
                            parameter_form=SimpleLevels[float](
                                form_spec_template=Percentage(),
                                level_direction=LevelDirection.LOWER,
                                prefill_fixed_levels=InputHint(value=(10.0, 5.0)),
                            ),
                        ),
                        CascadingSingleChoiceElement(
                            name="lic_unit_available_lower_abs",
                            title=Title("Absolute"),
                            parameter_form=SimpleLevels[int](
                                form_spec_template=Integer(),
                                level_direction=LevelDirection.LOWER,
                                prefill_fixed_levels=InputHint(value=(10, 5)),
                            ),
                        ),
                    ],
                    prefill=DefaultValue("lic_unit_available_lower_pct"),
                ),
                required=True,
            ),
        },
    )


rule_spec_m365_licenses = CheckParameters(
    name="m365_licenses",
    title=Title("Microsoft 365 Licenses"),
    parameter_form=_parameter_form_m365_licenses,
    topic=Topic.CLOUD,
    condition=HostAndItemCondition(item_title=Title("SKU name")),
)
