# ------------------------------------------------------------
# CUSTOM_Li2CO3_Separator
#
# Purpose:
#   Separate precipitated Li2CO3 from the mother liquor.
#
# Process:
#   Li2CO3_Slurry
#          |
#          v
#   CUSTOM_Li2CO3_Separator
#          |
#          +------> Li2CO3_Mother_Liquor
#          |
#          v
#   Li2CO3_Wet_Cake
#
# Modeling basis:
#   - Precipitated Li2CO3 is separated from the mother liquor.
#   - The wet cake contains Li2CO3 and retained mother liquor.
#   - All components other than Li2CO3 are treated as
#     mother-liquor components.
#   - Retained mother liquor is distributed proportionally
#     among the non-Li2CO3 components.
#   - The separator uses an idealized Li2CO3 capture efficiency
#     of 100% for the base-case screening model.
#
# Cake moisture assumption:
#   5 wt% moisture in the wet cake.
#
# This is an engineering assumption for the screening-level
# model and is not being claimed as a direct literature value.
#
# Literature basis:
#   Published Li2CO3 processes show that the precipitated
#   slurry is subjected to solid-liquid separation to produce
#   a Li2CO3 cake and mother liquor.
#
#   A recent Li2CO3 process study reports approximately 3 wt%
#   moisture in the cake after belt filtration.
#
#   Another recent study describes a filter-press cake with
#   less than 10 wt% moisture.
#
#   Therefore, 5 wt% is selected as an engineering assumption
#   within this literature-supported range.
#
# Li2CO3 capture assumption:
#   100% capture is used only as an idealized base-case
#   assumption. It is not claimed to represent actual
#   industrial separation efficiency.
#
# ------------------------------------------------------------


import clr
import System

clr.AddReference("DWSIM.Interfaces")

from DWSIM import Interfaces


# ------------------------------------------------------------
# HELPER FUNCTION
# ------------------------------------------------------------

def safe_float(value, default_value):
    try:
        return float(value)
    except:
        return default_value


# ------------------------------------------------------------
# SEPARATOR ASSUMPTIONS
# ------------------------------------------------------------
#
# Cake moisture:
#
#   moisture =
#       retained liquid / wet cake
#
# Li2CO3 capture:
#
#   fraction of Li2CO3 entering the separator that is
#   recovered in the wet cake.
#
# 1.0 represents the idealized 100% capture base case.
# ------------------------------------------------------------

FILTER_CAKE_MOISTURE = 0.05

LI2CO3_CAPTURE_EFFICIENCY = 1.0


# ------------------------------------------------------------
# STREAM CONNECTIONS
# ------------------------------------------------------------

feed = ims1
mother_liquor = oms1
wet_cake = oms2


# ------------------------------------------------------------
# READ INLET STREAM
# ------------------------------------------------------------

feed.Validate()

feed_props = feed.Phases[0].Properties

inlet_mass_flow = safe_float(
    feed_props.massflow,
    0.0
)

temperature = safe_float(
    feed_props.temperature,
    298.15
)

pressure = safe_float(
    feed_props.pressure,
    101325.0
)


# ------------------------------------------------------------
# CALCULATE COMPONENT MASS FLOWS IN THE SLURRY
# ------------------------------------------------------------
#
# DWSIM provides the component mass fractions through
# GetOverallMassComposition().
#
# This is important because the Li2CO3 value reported as
# 0.0113866 in the slurry is a MOLAR fraction, not a
# mass fraction.
#
# Component mass flow:
#
#   m_i = w_i * m_total
# ------------------------------------------------------------

component_mass_flow = {}

for comp in feed.Phases[0].Compounds.Values:

    name = comp.Name

    mass_fraction = safe_float(
        comp.MassFraction,
        0.0
    )

    component_mass_flow[name] = (
        mass_fraction * inlet_mass_flow
    )


# ------------------------------------------------------------
# IDENTIFY Li2CO3
# ------------------------------------------------------------

product_name = "Lithium Carbonate"

if product_name not in component_mass_flow:

    raise Exception(
        "Lithium Carbonate was not found in "
        "Li2CO3_Slurry."
    )


# ------------------------------------------------------------
# Li2CO3 ENTERING THE SEPARATOR
# ------------------------------------------------------------

li2co3_in = component_mass_flow[
    product_name
]


# ------------------------------------------------------------
# Li2CO3 RECOVERED IN THE WET CAKE
# ------------------------------------------------------------
#
# For the base case:
#
#   Li2CO3 capture efficiency = 1.0
#
# Therefore:
#
#   m_Li2CO3,cake =
#       m_Li2CO3,in * capture efficiency
# ------------------------------------------------------------

li2co3_cake_mass = (
    li2co3_in
    * LI2CO3_CAPTURE_EFFICIENCY
)


# ------------------------------------------------------------
# Li2CO3 LOST TO MOTHER LIQUOR
# ------------------------------------------------------------

li2co3_mother_liquor_mass = (
    li2co3_in
    - li2co3_cake_mass
)


# ------------------------------------------------------------
# LIQUID MASS ENTERING THE SEPARATOR
# ------------------------------------------------------------
#
# The feed liquid consists of:
#
#   total feed
#   -
#   Li2CO3 solid
#
# ------------------------------------------------------------

feed_liquid_mass = (
    inlet_mass_flow
    - li2co3_in
)


# ------------------------------------------------------------
# RETAINED MOTHER LIQUOR IN THE WET CAKE
# ------------------------------------------------------------
#
# The cake moisture is defined as:
#
#   w =
#       m_retained_liquid / m_wet_cake
#
# Therefore:
#
#   m_wet_cake =
#       m_dry_Li2CO3 / (1 - w)
#
# and:
#
#   m_retained_liquid =
#       m_wet_cake - m_dry_Li2CO3
#
# ------------------------------------------------------------

wet_cake_mass = (
    li2co3_cake_mass
    / (1.0 - FILTER_CAKE_MOISTURE)
)


retained_liquid_mass = (
    wet_cake_mass
    - li2co3_cake_mass
)


# ------------------------------------------------------------
# CHECK AVAILABLE LIQUID
# ------------------------------------------------------------

if retained_liquid_mass > feed_liquid_mass:

    raise Exception(
        "Required retained mother liquor exceeds "
        "the available liquid in Li2CO3_Slurry."
    )


# ------------------------------------------------------------
# MOTHER LIQUOR MASS FLOW
# ------------------------------------------------------------

mother_liquor_mass = (
    feed_liquid_mass
    - retained_liquid_mass
)


# ------------------------------------------------------------
# RETAINED LIQUID FRACTION
# ------------------------------------------------------------
#
# The retained mother liquor is distributed proportionally
# among the mother-liquor components.
# ------------------------------------------------------------

retained_fraction = 0.0

if feed_liquid_mass > 0.0:

    retained_fraction = (
        retained_liquid_mass
        / feed_liquid_mass
    )


# ------------------------------------------------------------
# CALCULATE OUTLET COMPONENT MASS FLOWS
# ------------------------------------------------------------

wet_cake_component_flow = {}

mother_liquor_component_flow = {}


for name in component_mass_flow:

    component_mass = component_mass_flow[name]


    # --------------------------------------------------------
    # Li2CO3
    # --------------------------------------------------------

    if name == product_name:

        wet_cake_component_flow[name] = (
            li2co3_cake_mass
        )

        mother_liquor_component_flow[name] = (
            li2co3_mother_liquor_mass
        )


    # --------------------------------------------------------
    # MOTHER-LIQUOR COMPONENTS
    #
    # A fraction remains with the wet cake as retained
    # mother liquor.
    # --------------------------------------------------------

    else:

        retained_component_mass = (
            component_mass
            * retained_fraction
        )

        mother_liquor_component_mass = (
            component_mass
            * (1.0 - retained_fraction)
        )

        wet_cake_component_flow[name] = (
            retained_component_mass
        )

        mother_liquor_component_flow[name] = (
            mother_liquor_component_mass
        )


# ------------------------------------------------------------
# CONVERT COMPONENT MASS FLOWS TO DWSIM ARRAYS
# ------------------------------------------------------------

wet_cake_mass_array = []

mother_liquor_mass_array = []


for comp in feed.Phases[0].Compounds.Values:

    name = comp.Name

    wet_cake_mass_array.append(
        wet_cake_component_flow.get(
            name,
            0.0
        )
    )

    mother_liquor_mass_array.append(
        mother_liquor_component_flow.get(
            name,
            0.0
        )
    )


wet_cake_array = System.Array[float](
    wet_cake_mass_array
)

mother_liquor_array = System.Array[float](
    mother_liquor_mass_array
)


# ------------------------------------------------------------
# CLEAR OUTPUT STREAMS
# ------------------------------------------------------------

wet_cake.Clear()

wet_cake.ClearAllProps()

mother_liquor.Clear()

mother_liquor.ClearAllProps()


# ------------------------------------------------------------
# WRITE OUTPUT COMPOSITIONS
# ------------------------------------------------------------

wet_cake.SetOverallMassComposition(
    wet_cake_array
)

mother_liquor.SetOverallMassComposition(
    mother_liquor_array
)


# ------------------------------------------------------------
# WRITE TEMPERATURE AND PRESSURE
# ------------------------------------------------------------

wet_cake.SetTemperature(
    temperature
)

mother_liquor.SetTemperature(
    temperature
)


wet_cake.SetPressure(
    pressure
)

mother_liquor.SetPressure(
    pressure
)


# ------------------------------------------------------------
# SET FLOW SPECIFICATION
# ------------------------------------------------------------

wet_cake.DefinedFlow = (
    Interfaces.Enums.FlowSpec.Mass
)

mother_liquor.DefinedFlow = (
    Interfaces.Enums.FlowSpec.Mass
)


wet_cake.SpecType = (
    Interfaces.Enums.StreamSpec.Temperature_and_Pressure
)

mother_liquor.SpecType = (
    Interfaces.Enums.StreamSpec.Temperature_and_Pressure
)


# ------------------------------------------------------------
# SET OUTLET MASS FLOWS
# ------------------------------------------------------------

wet_cake.SetMassFlow(
    wet_cake_mass
)

mother_liquor.SetMassFlow(
    mother_liquor_mass
)


# ------------------------------------------------------------
# MASS BALANCE CHECK
# ------------------------------------------------------------

mass_balance_error = (
    inlet_mass_flow
    - wet_cake_mass
    - mother_liquor_mass
)


# ------------------------------------------------------------
# Li2CO3 BALANCE CHECK
# ------------------------------------------------------------

li2co3_balance_error = (
    li2co3_in
    - li2co3_cake_mass
    - li2co3_mother_liquor_mass
)


# ------------------------------------------------------------
# DIAGNOSTICS
# ------------------------------------------------------------

Flowsheet.WriteMessage(
    "CUSTOM_Li2CO3_Separator: calculation completed."
)

Flowsheet.WriteMessage(
    "Inlet mass flow = "
    + str(inlet_mass_flow * 3600.0)
    + " kg/h"
)

Flowsheet.WriteMessage(
    "Li2CO3 entering separator = "
    + str(li2co3_in * 3600.0)
    + " kg/h"
)

Flowsheet.WriteMessage(
    "Li2CO3 capture efficiency = "
    + str(LI2CO3_CAPTURE_EFFICIENCY * 100.0)
    + " %"
)

Flowsheet.WriteMessage(
    "Dry Li2CO3 in wet cake = "
    + str(li2co3_cake_mass * 3600.0)
    + " kg/h"
)

Flowsheet.WriteMessage(
    "Li2CO3 in mother liquor = "
    + str(li2co3_mother_liquor_mass * 3600.0)
    + " kg/h"
)

Flowsheet.WriteMessage(
    "Filter cake moisture = "
    + str(FILTER_CAKE_MOISTURE * 100.0)
    + " wt%"
)

Flowsheet.WriteMessage(
    "Retained mother liquor = "
    + str(retained_liquid_mass * 3600.0)
    + " kg/h"
)

Flowsheet.WriteMessage(
    "Wet Li2CO3 cake = "
    + str(wet_cake_mass * 3600.0)
    + " kg/h"
)

Flowsheet.WriteMessage(
    "Li2CO3 mother liquor = "
    + str(mother_liquor_mass * 3600.0)
    + " kg/h"
)

Flowsheet.WriteMessage(
    "Mass balance error = "
    + str(mass_balance_error * 3600.0)
    + " kg/h"
)

Flowsheet.WriteMessage(
    "Li2CO3 balance error = "
    + str(li2co3_balance_error * 3600.0)
    + " kg/h"
)