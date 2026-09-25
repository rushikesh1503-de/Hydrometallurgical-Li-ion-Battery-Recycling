# --------------------------------------------------------
#
# DWSIM 10.2.1
#
# CUSTOM_NMC_Hydroxide_Wash
#
# Purpose:
# Wash the wet NMC622 hydroxide filter cake with
# deionized water.
#
# INPUTS:
#
#     ims1 = Wet_NMC_Hydroxide_Cake
#     ims2 = DI_Wash_Water
#
# OUTPUTS:
#
#     oms1 = Washed_NMC_Hydroxide_Cake
#     oms2 = Wash_Liquid
#
# --------------------------------------------------------

import clr
import System

clr.AddReference("DWSIM.Interfaces")

from System import Double
from DWSIM import Interfaces


# --------------------------------------------------------
# WASH DESIGN BASIS
#
# Wash water ratio:
#
#     0.6 kg water / kg dry solids
#
# Overall wash efficiency:
#
#     98%
#
# The 98% efficiency is applied to the soluble
# mother-liquor components retained in the wet cake.
#
# NMC622_Hydroxide is treated as the desired solid
# product and is retained in the washed cake.
#
# --------------------------------------------------------

WASH_RATIO = 0.6

WASH_EFFICIENCY = 0.98


# --------------------------------------------------------
# DEFAULT CONDITIONS
# --------------------------------------------------------

DEFAULT_TEMPERATURE = 298.15
DEFAULT_PRESSURE = 101325.0


# --------------------------------------------------------
# INPUT / OUTPUT PORTS
#
# ims1 = Wet_NMC_Hydroxide_Cake
# ims2 = DI_Wash_Water
#
# oms1 = Washed_NMC_Hydroxide_Cake
# oms2 = Wash_Liquid
# --------------------------------------------------------

wet_cake = ims1

wash_water = ims2

washed_cake = oms1

wash_liquid = oms2


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
# READ WET CAKE PROPERTIES
# --------------------------------------------------------

cake_properties = wet_cake.Phases[0].Properties


cake_mass_flow = safe_float(
    cake_properties.massflow,
    0.0
)


cake_temperature = safe_float(
    cake_properties.temperature,
    DEFAULT_TEMPERATURE
)


cake_pressure = safe_float(
    cake_properties.pressure,
    DEFAULT_PRESSURE
)


# --------------------------------------------------------
# READ WASH WATER PROPERTIES
# --------------------------------------------------------

wash_water_properties = wash_water.Phases[0].Properties


wash_water_mass_flow = safe_float(
    wash_water_properties.massflow,
    0.0
)


wash_water_temperature = safe_float(
    wash_water_properties.temperature,
    DEFAULT_TEMPERATURE
)


wash_water_pressure = safe_float(
    wash_water_properties.pressure,
    DEFAULT_PRESSURE
)


# --------------------------------------------------------
# COMPOUND INFORMATION
# --------------------------------------------------------

compound_names = wet_cake.GetCompoundNames()

cake_mass_comp = (
    wet_cake.GetOverallMassComposition()
)


water_compound_names = (
    wash_water.GetCompoundNames()
)


water_mass_comp = (
    wash_water.GetOverallMassComposition()
)


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
        "NMC622_Hydroxide not found in "
        "Wet_NMC_Hydroxide_Cake."
    )


# --------------------------------------------------------
# DRY PRODUCT MASS FLOW
#
#     m_product =
#         m_cake * w_product
#
# --------------------------------------------------------

dry_product_mass = (
    cake_mass_flow
    * cake_mass_comp[product_index]
)


# --------------------------------------------------------
# CALCULATE REQUIRED WASH WATER
#
#     m_wash =
#         WASH_RATIO * m_dry_product
#
# --------------------------------------------------------

required_wash_water = (
    WASH_RATIO
    * dry_product_mass
)


# --------------------------------------------------------
# CHECK WASH WATER STREAM
#
# The connected DI_Wash_Water stream should contain
# the calculated wash-water flow.
#
# This check prevents the model from silently using
# the wrong amount of wash water.
# --------------------------------------------------------

wash_water_difference = (
    wash_water_mass_flow
    - required_wash_water
)


# --------------------------------------------------------
# WASH WATER TOLERANCE
# --------------------------------------------------------

WASH_WATER_TOLERANCE = 1.0e-9


if abs(wash_water_difference) > WASH_WATER_TOLERANCE:

    raise Exception(
        "DI_Wash_Water flow does not match the "
        "required wash ratio."
    )


# --------------------------------------------------------
# INITIALIZE COMPONENT MASS-FLOW ARRAYS
# --------------------------------------------------------

washed_cake_mass_flows = []

wash_liquid_mass_flows = []


# --------------------------------------------------------
# COMPONENT MASS BALANCE
#
# Wet cake components:
#
#     NMC622_Hydroxide
#         -> remains in washed cake
#
#     All other components
#         -> soluble mother liquor
#
# 98% of the soluble mother liquor is removed.
#
# 2% remains in the washed cake.
#
# --------------------------------------------------------

for i, name in enumerate(compound_names):


    # ----------------------------------------------------
    # COMPONENT MASS FLOW IN WET CAKE
    # ----------------------------------------------------

    cake_component_mass = (
        cake_mass_flow
        * cake_mass_comp[i]
    )


    # ----------------------------------------------------
    # NMC622 HYDROXIDE
    #
    # Desired product remains in the washed cake.
    # ----------------------------------------------------

    if name == product_name:

        washed_cake_mass_flows.append(
            cake_component_mass
        )

        wash_liquid_mass_flows.append(
            0.0
        )


    # ----------------------------------------------------
    # SOLUBLE MOTHER LIQUOR
    #
    # 98% removed by washing.
    #
    # 2% remains with the washed cake.
    # ----------------------------------------------------

    else:

        remaining_fraction = (
            1.0 - WASH_EFFICIENCY
        )


        remaining_mass = (
            cake_component_mass
            * remaining_fraction
        )


        removed_mass = (
            cake_component_mass
            * WASH_EFFICIENCY
        )


        washed_cake_mass_flows.append(
            remaining_mass
        )


        wash_liquid_mass_flows.append(
            removed_mass
        )


# --------------------------------------------------------
# ADD DI WASH WATER TO WASH LIQUID
#
# The wash water itself leaves with the wash liquid.
# --------------------------------------------------------

for i, name in enumerate(water_compound_names):

    water_component_mass = (
        wash_water_mass_flow
        * water_mass_comp[i]
    )


    matching_index = -1


    for j, cake_name in enumerate(compound_names):

        if cake_name == name:

            matching_index = j

            break


    if matching_index >= 0:

        wash_liquid_mass_flows[
            matching_index
        ] += water_component_mass

    else:

        raise Exception(
            "Wash water compound "
            + str(name)
            + " was not found in the wet-cake "
            + "compound list."
        )


# --------------------------------------------------------
# TOTAL OUTLET MASS FLOWS
# --------------------------------------------------------

washed_cake_total = sum(
    washed_cake_mass_flows
)


wash_liquid_total = sum(
    wash_liquid_mass_flows
)


# --------------------------------------------------------
# TOTAL INPUT MASS
# --------------------------------------------------------

total_input_mass = (
    cake_mass_flow
    + wash_water_mass_flow
)


# --------------------------------------------------------
# MASS BALANCE
#
#     Wet cake
#     +
#     DI wash water
#     =
#     Washed cake
#     +
#     Wash liquid
#
# --------------------------------------------------------

mass_balance_error = (
    total_input_mass
    - washed_cake_total
    - wash_liquid_total
)


# --------------------------------------------------------
# CONVERT PYTHON LISTS TO .NET ARRAYS
# --------------------------------------------------------

washed_cake_array = System.Array[float](
    washed_cake_mass_flows
)


wash_liquid_array = System.Array[float](
    wash_liquid_mass_flows
)


# --------------------------------------------------------
# CLEAR OUTPUT STREAMS
# --------------------------------------------------------

washed_cake.Clear()

washed_cake.ClearAllProps()


wash_liquid.Clear()

wash_liquid.ClearAllProps()


# --------------------------------------------------------
# SET OUTPUT COMPOSITIONS
# --------------------------------------------------------

washed_cake.SetOverallMassComposition(
    washed_cake_array
)


wash_liquid.SetOverallMassComposition(
    wash_liquid_array
)


# --------------------------------------------------------
# OUTPUT TEMPERATURE
#
# Use mass-weighted mixing temperature.
# --------------------------------------------------------

total_input_mass_for_temperature = (
    cake_mass_flow
    + wash_water_mass_flow
)


if total_input_mass_for_temperature > 0.0:

    weighted_temperature = (
        cake_mass_flow * cake_temperature
        +
        wash_water_mass_flow
        * wash_water_temperature
    ) / total_input_mass_for_temperature

else:

    weighted_temperature = DEFAULT_TEMPERATURE


# --------------------------------------------------------
# OUTPUT PRESSURE
#
# Use the lower inlet pressure.
# --------------------------------------------------------

output_pressure = min(
    cake_pressure,
    wash_water_pressure
)


# --------------------------------------------------------
# SET OUTPUT TEMPERATURE
# --------------------------------------------------------

washed_cake.SetTemperature(
    weighted_temperature
)


wash_liquid.SetTemperature(
    weighted_temperature
)


# --------------------------------------------------------
# SET OUTPUT PRESSURE
# --------------------------------------------------------

washed_cake.SetPressure(
    output_pressure
)


wash_liquid.SetPressure(
    output_pressure
)


# --------------------------------------------------------
# SET FLOW SPECIFICATION
# --------------------------------------------------------

washed_cake.DefinedFlow = (
    Interfaces.Enums.FlowSpec.Mass
)


wash_liquid.DefinedFlow = (
    Interfaces.Enums.FlowSpec.Mass
)


washed_cake.SpecType = (
    Interfaces.Enums.StreamSpec.Temperature_and_Pressure
)


wash_liquid.SpecType = (
    Interfaces.Enums.StreamSpec.Temperature_and_Pressure
)


# --------------------------------------------------------
# SET FINAL MASS FLOWS
# --------------------------------------------------------

washed_cake.SetMassFlow(
    washed_cake_total
)


wash_liquid.SetMassFlow(
    wash_liquid_total
)


# --------------------------------------------------------
# DIAGNOSTIC INFORMATION
# --------------------------------------------------------

Flowsheet.WriteMessage(
    "CUSTOM_NMC_Hydroxide_Wash: "
    + "calculation completed."
)


Flowsheet.WriteMessage(
    "Wet cake mass flow = "
    + str(cake_mass_flow)
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
    "Wash ratio = "
    + str(WASH_RATIO)
    + " kg/kg dry solids"
)


Flowsheet.WriteMessage(
    "Required DI wash water = "
    + str(required_wash_water)
    + " kg/s"
)


Flowsheet.WriteMessage(
    "Required DI wash water = "
    + str(required_wash_water * 3600.0)
    + " kg/h"
)


Flowsheet.WriteMessage(
    "Wash efficiency = "
    + str(WASH_EFFICIENCY * 100.0)
    + " %"
)


Flowsheet.WriteMessage(
    "Washed cake mass flow = "
    + str(washed_cake_total)
    + " kg/s"
)


Flowsheet.WriteMessage(
    "Washed cake mass flow = "
    + str(washed_cake_total * 3600.0)
    + " kg/h"
)


Flowsheet.WriteMessage(
    "Wash liquid mass flow = "
    + str(wash_liquid_total)
    + " kg/s"
)


Flowsheet.WriteMessage(
    "Wash liquid mass flow = "
    + str(wash_liquid_total * 3600.0)
    + " kg/h"
)


Flowsheet.WriteMessage(
    "Mass balance error = "
    + str(mass_balance_error)
    + " kg/s"
)