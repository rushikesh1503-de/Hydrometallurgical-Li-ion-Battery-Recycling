# --------------------------------------------------------
# CUSTOM_Precipitate_Separator
#
# Purpose:
# Separate:
#
#     Precip_Slurry
#
# into:
#
#     Precip_Filtrate
#     Wet_NMC_Hydroxide_Cake
#
# The wet cake contains:
#
#     NMC622_Hydroxide
#     + retained mother liquor
#
# --------------------------------------------------------
#
# FILTER DESIGN BASIS
#
# Filter cake discharge moisture:
#
#     5 wt%
#
# --------------------------------------------------------

import clr
import System

clr.AddReference("DWSIM.Interfaces")

from System import Double
from DWSIM import Interfaces


# --------------------------------------------------------
# FILTER DESIGN BASIS
# --------------------------------------------------------

FILTER_CAKE_MOISTURE = 0.05


# --------------------------------------------------------
# DEFAULT CONDITIONS
# --------------------------------------------------------

DEFAULT_TEMPERATURE = 298.15
DEFAULT_PRESSURE = 101325.0


# --------------------------------------------------------
# INPUT / OUTPUT PORTS
#
# ims1 = Precip_Slurry
#
# oms1 = Precip_Filtrate
# oms2 = Wet_NMC_Hydroxide_Cake
# --------------------------------------------------------

feed = ims1

filtrate = oms1

wet_cake = oms2


# --------------------------------------------------------
# HELPER FUNCTION
# --------------------------------------------------------

def safe_float(value, default_value):

    try:

        value = float(value)

        if value != value:

            return default_value

        return value

    except:

        return default_value


# --------------------------------------------------------
# READ FEED PROPERTIES
# --------------------------------------------------------

feed_properties = feed.Phases[0].Properties


# --------------------------------------------------------
# FEED MASS FLOW
# --------------------------------------------------------

feed_mass_flow = safe_float(
    feed_properties.massflow,
    0.0
)


# --------------------------------------------------------
# FEED TEMPERATURE
# --------------------------------------------------------

feed_temperature = safe_float(
    feed_properties.temperature,
    DEFAULT_TEMPERATURE
)


# --------------------------------------------------------
# FEED PRESSURE
# --------------------------------------------------------

feed_pressure = safe_float(
    feed_properties.pressure,
    DEFAULT_PRESSURE
)


# --------------------------------------------------------
# COMPOUND INFORMATION
# --------------------------------------------------------

compound_names = feed.GetCompoundNames()

mass_comp = feed.GetOverallMassComposition()


# --------------------------------------------------------
# IDENTIFY NMC622 HYDROXIDE
# --------------------------------------------------------

product_name = "NMC622_Hydroxide"

product_index = -1


for i, name in enumerate(compound_names):

    if name == product_name:

        product_index = i

        break


if product_index < 0:

    raise Exception(
        "NMC622_Hydroxide not found in Precip_Slurry."
    )


# --------------------------------------------------------
# DRY NMC622 HYDROXIDE MASS FLOW
#
#     m_product =
#         m_feed * w_product
#
# --------------------------------------------------------

dry_product_mass = (
    feed_mass_flow
    * mass_comp[product_index]
)


# --------------------------------------------------------
# TOTAL NON-PRODUCT MATERIAL
#
# In this component-based model, everything other than
# NMC622_Hydroxide is treated as liquid mother liquor.
# --------------------------------------------------------

feed_liquid_mass = (
    feed_mass_flow
    - dry_product_mass
)


# --------------------------------------------------------
# FILTER CAKE MOISTURE
#
# Design basis:
#
#     5 wt% moisture
#
# Therefore:
#
#     m_liquid
#     ----------------
#     m_dry + m_liquid
#
#     = 0.05
#
# Rearranging:
#
#     m_liquid =
#         0.05
#         --------
#         1 - 0.05
#         *
#         m_dry
#
# --------------------------------------------------------

retained_liquid_mass = (
    FILTER_CAKE_MOISTURE
    / (1.0 - FILTER_CAKE_MOISTURE)
    * dry_product_mass
)


# --------------------------------------------------------
# CHECK AVAILABLE LIQUID
# --------------------------------------------------------

if retained_liquid_mass > feed_liquid_mass:

    raise Exception(
        "Required retained liquid is greater "
        "than the available liquid in Precip_Slurry."
    )


# --------------------------------------------------------
# FILTRATE LIQUID
#
#     filtrate =
#         feed liquid
#         -
#         retained liquid
#
# --------------------------------------------------------

filtrate_liquid_mass = (
    feed_liquid_mass
    - retained_liquid_mass
)


# --------------------------------------------------------
# RETAINED LIQUID FRACTION
#
# This fraction is applied to every liquid component.
# --------------------------------------------------------

if feed_liquid_mass > 0.0:

    retained_fraction = (
        retained_liquid_mass
        / feed_liquid_mass
    )

else:

    retained_fraction = 0.0


# --------------------------------------------------------
# INITIALIZE COMPONENT MASS-FLOW ARRAYS
# --------------------------------------------------------

wet_cake_mass_flows = []

filtrate_mass_flows = []


# --------------------------------------------------------
# COMPONENT MASS BALANCE
# --------------------------------------------------------

for i, name in enumerate(compound_names):


    # ----------------------------------------------------
    # COMPONENT MASS FLOW IN FEED
    # ----------------------------------------------------

    component_mass = (
        feed_mass_flow
        * mass_comp[i]
    )


    # ----------------------------------------------------
    # NMC622 HYDROXIDE
    #
    # All calculated NMC622 hydroxide is retained in
    # the wet cake.
    #
    # This assumes no product loss during filtration.
    # ----------------------------------------------------

    if name == product_name:

        wet_cake_mass_flows.append(
            component_mass
        )

        filtrate_mass_flows.append(
            0.0
        )


    # ----------------------------------------------------
    # LIQUID COMPONENTS
    #
    # A fraction remains in the wet cake as retained
    # mother liquor.
    #
    # The remainder leaves as filtrate.
    # ----------------------------------------------------

    else:

        wet_cake_component_mass = (
            component_mass
            * retained_fraction
        )


        filtrate_component_mass = (
            component_mass
            * (1.0 - retained_fraction)
        )


        wet_cake_mass_flows.append(
            wet_cake_component_mass
        )


        filtrate_mass_flows.append(
            filtrate_component_mass
        )


# --------------------------------------------------------
# TOTAL OUTLET MASS FLOWS
# --------------------------------------------------------

wet_cake_total = sum(
    wet_cake_mass_flows
)


filtrate_total = sum(
    filtrate_mass_flows
)


# --------------------------------------------------------
# MASS BALANCE
#
#     Feed =
#         Wet cake
#         +
#         Filtrate
# --------------------------------------------------------

mass_balance_error = (
    feed_mass_flow
    - wet_cake_total
    - filtrate_total
)


# --------------------------------------------------------
# CONVERT PYTHON LISTS TO .NET ARRAYS
# --------------------------------------------------------

wet_cake_array = System.Array[float](
    wet_cake_mass_flows
)


filtrate_array = System.Array[float](
    filtrate_mass_flows
)


# --------------------------------------------------------
# CLEAR OUTPUT STREAMS
# --------------------------------------------------------

filtrate.Clear()

filtrate.ClearAllProps()


wet_cake.Clear()

wet_cake.ClearAllProps()


# --------------------------------------------------------
# SET OUTPUT COMPOSITIONS
# --------------------------------------------------------

filtrate.SetOverallMassComposition(
    filtrate_array
)


wet_cake.SetOverallMassComposition(
    wet_cake_array
)


# --------------------------------------------------------
# SET TEMPERATURE
# --------------------------------------------------------

filtrate.SetTemperature(
    feed_temperature
)


wet_cake.SetTemperature(
    feed_temperature
)


# --------------------------------------------------------
# SET PRESSURE
# --------------------------------------------------------

filtrate.SetPressure(
    feed_pressure
)


wet_cake.SetPressure(
    feed_pressure
)


# --------------------------------------------------------
# SET FLOW SPECIFICATION
# --------------------------------------------------------

filtrate.DefinedFlow = (
    Interfaces.Enums.FlowSpec.Mass
)


wet_cake.DefinedFlow = (
    Interfaces.Enums.FlowSpec.Mass
)


filtrate.SpecType = (
    Interfaces.Enums.StreamSpec.Temperature_and_Pressure
)


wet_cake.SpecType = (
    Interfaces.Enums.StreamSpec.Temperature_and_Pressure
)


# --------------------------------------------------------
# SET FINAL MASS FLOWS
# --------------------------------------------------------

filtrate.SetMassFlow(
    filtrate_total
)


wet_cake.SetMassFlow(
    wet_cake_total
)


# --------------------------------------------------------
# DIAGNOSTIC INFORMATION
# --------------------------------------------------------

Flowsheet.WriteMessage(
    "CUSTOM_Precipitate_Separator: "
    + "calculation completed."
)


Flowsheet.WriteMessage(
    "Precip_Slurry mass flow = "
    + str(feed_mass_flow)
    + " kg/s"
)


Flowsheet.WriteMessage(
    "Dry NMC622_Hydroxide = "
    + str(dry_product_mass)
    + " kg/s"
)


Flowsheet.WriteMessage(
    "Dry NMC622_Hydroxide = "
    + str(dry_product_mass * 3600.0)
    + " kg/h"
)


Flowsheet.WriteMessage(
    "Filter cake moisture = "
    + str(FILTER_CAKE_MOISTURE * 100.0)
    + " wt%"
)


Flowsheet.WriteMessage(
    "Retained mother liquor = "
    + str(retained_liquid_mass)
    + " kg/s"
)


Flowsheet.WriteMessage(
    "Retained mother liquor = "
    + str(retained_liquid_mass * 3600.0)
    + " kg/h"
)


Flowsheet.WriteMessage(
    "Wet cake mass flow = "
    + str(wet_cake_total)
    + " kg/s"
)


Flowsheet.WriteMessage(
    "Wet cake mass flow = "
    + str(wet_cake_total * 3600.0)
    + " kg/h"
)


Flowsheet.WriteMessage(
    "Filtrate mass flow = "
    + str(filtrate_total)
    + " kg/s"
)


Flowsheet.WriteMessage(
    "Filtrate mass flow = "
    + str(filtrate_total * 3600.0)
    + " kg/h"
)


Flowsheet.WriteMessage(
    "Retained liquid fraction = "
    + str(retained_fraction)
)


Flowsheet.WriteMessage(
    "Mass balance error = "
    + str(mass_balance_error)
    + " kg/s"
)