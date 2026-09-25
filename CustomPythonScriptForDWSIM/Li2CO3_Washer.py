# ------------------------------------------------------------
# CUSTOM_Li2CO3_Washer
#
# Purpose:
#   Repulp-wash the wet Li2CO3 cake with DI water and perform
#   a second idealized solid-liquid separation.
#
# Input 1:
#   Li2CO3_Wet_Cake
#
# Input 2:
#   Heated_DI_Wash_Water
#
# Output 1:
#   Washed_Li2CO3_Cake
#
# Output 2:
#   Li2CO3_Wash_Liquor
#
# Modeling basis:
#   - Wash water = 1.0 kg per kg wet cake
#   - Fresh DI water is heated upstream to 90 degC
#   - Wet cake enters at its actual inlet temperature
#   - Washer temperature is estimated from the two inlet
#     temperatures using their arithmetic average
#   - Original entrained mother liquor is completely displaced
#   - Washed cake retains 5 wt% liquid
#   - Li2CO3 dissolution loss is estimated from published
#     temperature-dependent Li2CO3 solubility in water
#   - No chemical reaction occurs in the washer
#
# IMPORTANT TEMPERATURE INTERPRETATION:
#
#   The literature-supported washing range used as process
#   background is 50-90 degC.
#
#   The current DWSIM configuration heats the fresh DI water
#   to 90 degC, while the wet Li2CO3 cake enters at 50 degC.
#
#   Therefore the model calculates:
#
#       T_washer = (T_cake + T_wash_water) / 2
#
#   For the current case:
#
#       T_washer = (50 + 90) / 2 = 70 degC
#
#   Consequently, the Li2CO3 solubility used by this model
#   is the published value at 70 degC = 9.2 g/L.
#
#   This represents a simplified adiabatic mixing estimate.
#   It does NOT represent a washer actively controlled at
#   90 degC.
#
# Literature / technical basis:
#
#   1. Greil, R.; Chai, J.; Rudelstorfer, G.; Mitsche, S.;
#      Lux, S.
#      "Water as a Sustainable Leaching Agent for the
#      Selective Leaching of Lithium from Spent
#      Lithium-Ion Batteries."
#      ACS Omega, 2024, 9, 7806-7816.
#      DOI: 10.1021/acsomega.3c07405
#
#      Used here for the published temperature-dependent
#      Li2CO3 solubility values in water:
#
#          0 degC   = 15.4 g/L
#          20 degC  = 13.3 g/L
#          25 degC  = 12.8 g/L
#          40 degC  = 11.5 g/L
#          50 degC  = 10.7 g/L
#          60 degC  = 9.9 g/L
#          70 degC  = 9.2 g/L
#          80 degC  = 8.5 g/L
#          90 degC  = 7.8 g/L
#          100 degC = 7.2 g/L
#
#   2. EP3845492B1
#      "Method for producing lithium carbonate."
#
#      Used here for the Li2CO3 repulp-washing basis:
#        - pure water = 0.5-2.0 times wet Li2CO3 weight
#        - preferred water ratio = 1.0-1.5 times wet weight
#        - washing temperature = 50-90 degC
#        - washing time = 0.5-1 h
#        - repeated washing is preferred in the patent
#
#   3. US9074265B2
#      "Processes for preparing highly pure lithium carbonate
#      and other highly pure lithium containing compounds."
#
#      Used as additional technical support for hot DI-water
#      washing of Li2CO3. The patent describes final washing
#      with hot DI water at approximately 80-95 degC, including
#      about 90 degC.
#
# Important:
#   The Li2CO3 wet cake is represented in DWSIM as an
#   overall material stream, not as a rigorous solid phase.
#   Therefore this unit explicitly performs the material
#   balance instead of using the standard DWSIM Filter.
# ------------------------------------------------------------


import math
from System import Array


# ------------------------------------------------------------
# Helper function
# ------------------------------------------------------------

def safe_float(value, default=0.0):

    try:

        if value is None:
            return default

        value = float(value)

        if math.isnan(value) or math.isinf(value):
            return default

        return value

    except:

        return default


# ------------------------------------------------------------
# User-defined modeling assumptions
# ------------------------------------------------------------

# Literature basis:
#
# EP3845492B1 describes:
#
#   wash water = 0.5-2.0 kg/kg wet Li2CO3
#
# Preferred:
#
#   1.0-1.5 kg/kg wet Li2CO3
#
# Base case selected:
#
#   1.0 kg/kg wet cake
#
WASH_WATER_RATIO = 1.0


# ------------------------------------------------------------
# Fresh wash-water temperature
# ------------------------------------------------------------

# The fresh DI water is heated upstream in the DWSIM
# Heater_Li2CO3_Wash_Water unit.

EXPECTED_WASH_WATER_TEMPERATURE = 363.15


# ------------------------------------------------------------
# Engineering assumption for final cake moisture
# ------------------------------------------------------------

# The washed cake is assumed to retain:
#
#   5 wt% liquid
#
# This is an engineering modeling assumption.
#
# It is NOT treated as a universal literature value.
#
FILTER_CAKE_MOISTURE = 0.05


# ------------------------------------------------------------
# Engineering assumption:
# complete displacement of original mother liquor
# ------------------------------------------------------------

# The mother liquor originally entrained in the wet cake
# is assumed to be completely displaced into the wash liquor.
#
# This is a base-case modeling assumption.
#
# It can later be changed for sensitivity analysis.
#
MOTHER_LIQUOR_REMOVAL_EFFICIENCY = 1.0


# ------------------------------------------------------------
# Linear interpolation is used between published data points.
# ------------------------------------------------------------

SOLUBILITY_T_C = [
    0.0,
    20.0,
    25.0,
    40.0,
    50.0,
    60.0,
    70.0,
    80.0,
    90.0,
    100.0
]


SOLUBILITY_G_PER_L = [
    15.4,
    13.3,
    12.8,
    11.5,
    10.7,
    9.9,
    9.2,
    8.5,
    7.8,
    7.2
]


# ------------------------------------------------------------
# Linear interpolation function for Li2CO3 solubility
# ------------------------------------------------------------

def get_li2co3_solubility_g_per_l(T_K):

    T_C = T_K - 273.15

    if T_C < SOLUBILITY_T_C[0] or T_C > SOLUBILITY_T_C[-1]:

        raise Exception(
            "CUSTOM_Li2CO3_Washer: "
            "wash temperature is outside the available "
            "Li2CO3 solubility data range of 0-100 degC."
        )


    for i in range(len(SOLUBILITY_T_C) - 1):

        T1 = SOLUBILITY_T_C[i]
        T2 = SOLUBILITY_T_C[i + 1]

        if T1 <= T_C <= T2:

            S1 = SOLUBILITY_G_PER_L[i]
            S2 = SOLUBILITY_G_PER_L[i + 1]

            if T2 == T1:

                return S1

            fraction = (
                (T_C - T1) /
                (T2 - T1)
            )

            return (
                S1 +
                fraction * (S2 - S1)
            )


    return SOLUBILITY_G_PER_L[-1]


# ------------------------------------------------------------
# Stream connections
# ------------------------------------------------------------

wet_cake = ims1
wash_water = ims2

washed_cake = oms1
wash_liquor = oms2


# ------------------------------------------------------------
# Read inlet stream conditions
# ------------------------------------------------------------

wet_cake_mass_flow = safe_float(
    wet_cake.GetMassFlow()
)


wash_water_mass_flow = safe_float(
    wash_water.GetMassFlow()
)


wet_cake_temperature = safe_float(
    wet_cake.GetTemperature(),
    323.15
)


wash_water_temperature = safe_float(
    wash_water.GetTemperature(),
    EXPECTED_WASH_WATER_TEMPERATURE
)


wet_cake_pressure = safe_float(
    wet_cake.GetPressure(),
    101325.0
)


wash_water_pressure = safe_float(
    wash_water.GetPressure(),
    101325.0
)


# ------------------------------------------------------------
# Basic input validation
# ------------------------------------------------------------

if wet_cake_mass_flow <= 0.0:

    raise Exception(
        "CUSTOM_Li2CO3_Washer: "
        "wet cake mass flow is zero."
    )


if wash_water_mass_flow <= 0.0:

    raise Exception(
        "CUSTOM_Li2CO3_Washer: "
        "wash water mass flow is zero."
    )


# ------------------------------------------------------------
# Determine the actual washing ratio
#
# The connected streams are used rather than forcing the
# ratio. This makes the diagnostic show the actual DWSIM
# flow ratio.
# ------------------------------------------------------------

actual_wash_ratio = (
    wash_water_mass_flow /
    wet_cake_mass_flow
)


# ------------------------------------------------------------
# Determine the effective washer temperature
#
# Current screening-level assumption:
#
#   T_washer =
#       (T_wet_cake + T_wash_water) / 2
#
# This corresponds to a simplified adiabatic mixing estimate.
#
# Current DWSIM case:
#
#   wet cake       = 323.15 K = 50 degC
#   wash water     = 363.15 K = 90 degC
#
# Therefore:
#
#   T_washer       = 343.15 K = 70 degC
#
# The solubility calculation below therefore uses the
# Li2CO3 solubility at 70 degC.
# ------------------------------------------------------------

wash_temperature = (
    wet_cake_temperature +
    wash_water_temperature
) / 2.0


compound_names = list(
    wet_cake.GetCompoundNames()
)


wet_cake_mass_fraction = list(
    wet_cake.GetOverallMassComposition()
)


# ------------------------------------------------------------
# Calculate component mass flows in the wet cake
# ------------------------------------------------------------

component_mass_flow = {}


for i in range(len(compound_names)):

    name = compound_names[i]

    mf = safe_float(
        wet_cake_mass_fraction[i]
    )

    component_mass_flow[name] = (
        wet_cake_mass_flow * mf
    )


# ------------------------------------------------------------
# Identify Li2CO3
# ------------------------------------------------------------

LI2CO3_NAME = "Lithium Carbonate"


if LI2CO3_NAME not in component_mass_flow:

    raise Exception(
        "CUSTOM_Li2CO3_Washer: "
        "Lithium Carbonate was not found "
        "in the wet cake."
    )


li2co3_in = component_mass_flow[
    LI2CO3_NAME
]


# ------------------------------------------------------------
# Calculate retained mother liquor in the incoming cake
#
# The wet cake contains:
#
#   Li2CO3 + entrained mother liquor
#
# Therefore:
#
#   retained mother liquor =
#       wet cake mass - Li2CO3 mass
# ------------------------------------------------------------

retained_mother_liquor = (
    wet_cake_mass_flow -
    li2co3_in
)


# ------------------------------------------------------------
# Calculate Li2CO3 solubility at the actual washer
# temperature
#
# For the current case:
#
#   T_washer = 70 degC
#
# Therefore:
#
#   solubility = 9.2 g/L
#
# If the inlet temperatures change, this function
# automatically interpolates the published data.
# ------------------------------------------------------------

li2co3_solubility = (
    get_li2co3_solubility_g_per_l(
        wash_temperature
    )
)


# ------------------------------------------------------------
# Calculate wash-water volumetric flow
#
# DWSIM returns:
#
#   m3/s
#
# Convert to:
#
#   L/s
#
# using:
#
#   1 m3 = 1000 L
# ------------------------------------------------------------

wash_water_volumetric_flow = safe_float(
    wash_water.GetVolumetricFlow()
)


if wash_water_volumetric_flow <= 0.0:

    raise Exception(
        "CUSTOM_Li2CO3_Washer: "
        "wash-water volumetric flow is zero."
    )


wash_water_L_per_s = (
    wash_water_volumetric_flow *
    1000.0
)


# ------------------------------------------------------------
# Estimate Li2CO3 dissolution loss
#
# Published solubility:
#
#   g Li2CO3 / L water
#
# Therefore:
#
#   Li2CO3 dissolution =
#       solubility × water volumetric flow
#
# First:
#
#   g/s = g/L × L/s
#
# Then:
#
#   kg/s = g/s / 1000
#
# IMPORTANT:
#
# This is a screening-level equilibrium-capacity estimate.
# It is NOT a measured washing loss for this exact slurry.
# ------------------------------------------------------------

li2co3_loss_mass_flow = (
    li2co3_solubility *
    wash_water_L_per_s /
    1000.0
)


# ------------------------------------------------------------
# Prevent the model from dissolving more Li2CO3 than
# actually enters the washer
# ------------------------------------------------------------

li2co3_loss_mass_flow = min(
    li2co3_loss_mass_flow,
    li2co3_in
)


# ------------------------------------------------------------
# Li2CO3 remaining in washed cake
# ------------------------------------------------------------

li2co3_washed = (
    li2co3_in -
    li2co3_loss_mass_flow
)


# ------------------------------------------------------------
# Calculate washed-cake total mass from the assumed
# 5 wt% retained liquid
#
# If:
#
#   moisture = 5 wt%
#
# then:
#
#   dry Li2CO3 = 0.95 × wet cake
#
# therefore:
#
#   wet cake =
#       dry Li2CO3 / 0.95
# ------------------------------------------------------------

washed_cake_mass_flow = (
    li2co3_washed /
    (1.0 - FILTER_CAKE_MOISTURE)
)


# ------------------------------------------------------------
# Calculate liquid retained in the washed cake
# ------------------------------------------------------------

washed_cake_retained_liquid = (
    washed_cake_mass_flow *
    FILTER_CAKE_MOISTURE
)


# ------------------------------------------------------------
# Build wash-water component mass flows
# ------------------------------------------------------------

wash_water_mass_fraction = list(
    wash_water.GetOverallMassComposition()
)


wash_water_component_mass_flow = {}


for i in range(len(compound_names)):

    name = compound_names[i]

    if i < len(wash_water_mass_fraction):

        mf = safe_float(
            wash_water_mass_fraction[i]
        )

    else:

        mf = 0.0

    wash_water_component_mass_flow[name] = (
        wash_water_mass_flow * mf
    )


# ------------------------------------------------------------
# Build output component mass flows
#
# Washed cake:
#
#   Li2CO3 remaining after dissolution
#   + retained fresh wash liquid
#
# Wash liquor:
#
#   dissolved Li2CO3
#   + displaced mother liquor
#   + remaining fresh wash water
# ------------------------------------------------------------

washed_cake_component_mass_flow = {}

wash_liquor_component_mass_flow = {}


for name in compound_names:

    washed_cake_component_mass_flow[name] = 0.0

    wash_liquor_component_mass_flow[name] = 0.0


# ------------------------------------------------------------
# Li2CO3 distribution
#
# Remaining Li2CO3 -> washed cake
#
# Dissolved Li2CO3 -> wash liquor
# ------------------------------------------------------------

washed_cake_component_mass_flow[
    LI2CO3_NAME
] = li2co3_washed


wash_liquor_component_mass_flow[
    LI2CO3_NAME
] = li2co3_loss_mass_flow


# ------------------------------------------------------------
# Original wet-cake non-Li2CO3 components
#
# These components represent the entrained mother liquor.
#
# Base-case assumption:
#
#   100% of the entrained mother liquor is displaced
#   into the wash liquor.
# ------------------------------------------------------------

for name in compound_names:

    if name != LI2CO3_NAME:

        original_component = (
            component_mass_flow[name]
        )


        removed_component = (
            original_component *
            MOTHER_LIQUOR_REMOVAL_EFFICIENCY
        )


        remaining_component = (
            original_component -
            removed_component
        )


        wash_liquor_component_mass_flow[name] += (
            removed_component
        )


        washed_cake_component_mass_flow[name] += (
            remaining_component
        )


# ------------------------------------------------------------
# Add the fresh wash water to the wash liquor
# ------------------------------------------------------------

for name in compound_names:

    wash_liquor_component_mass_flow[name] += (
        wash_water_component_mass_flow[name]
    )


# ------------------------------------------------------------
# Retain a fraction of the fresh wash liquid in the cake
#
# The cake moisture is assumed to be 5 wt%.
#
# The retained liquid is taken from the fresh wash-water
# stream.
#
# Because the original mother liquor is assumed to have
# been completely displaced, the retained liquid is treated
# as fresh wash water in this simplified model.
# ------------------------------------------------------------

total_fresh_wash_water = (
    wash_water_mass_flow
)


if total_fresh_wash_water > 0.0:

    retained_wash_fraction = (
        washed_cake_retained_liquid /
        total_fresh_wash_water
    )

else:

    retained_wash_fraction = 0.0


for name in compound_names:

    retained_from_wash = (
        wash_water_component_mass_flow[name] *
        retained_wash_fraction
    )


    wash_liquor_component_mass_flow[name] -= (
        retained_from_wash
    )


    washed_cake_component_mass_flow[name] += (
        retained_from_wash
    )


# ------------------------------------------------------------
# Remove numerical negative values
# ------------------------------------------------------------

for name in compound_names:

    if (
        washed_cake_component_mass_flow[name]
        < 0.0
    ):

        washed_cake_component_mass_flow[name] = 0.0


    if (
        wash_liquor_component_mass_flow[name]
        < 0.0
    ):

        wash_liquor_component_mass_flow[name] = 0.0


# ------------------------------------------------------------
# Calculate total output mass flows
# ------------------------------------------------------------

calculated_washed_cake_mass_flow = sum(
    washed_cake_component_mass_flow.values()
)


calculated_wash_liquor_mass_flow = sum(
    wash_liquor_component_mass_flow.values()
)


# ------------------------------------------------------------
# Normalize component mass flows into mass fractions
# ------------------------------------------------------------

washed_cake_mass_fraction = []

wash_liquor_mass_fraction = []


for name in compound_names:

    if calculated_washed_cake_mass_flow > 0.0:

        cake_mf = (
            washed_cake_component_mass_flow[name] /
            calculated_washed_cake_mass_flow
        )

    else:

        cake_mf = 0.0


    if calculated_wash_liquor_mass_flow > 0.0:

        liquor_mf = (
            wash_liquor_component_mass_flow[name] /
            calculated_wash_liquor_mass_flow
        )

    else:

        liquor_mf = 0.0


    washed_cake_mass_fraction.append(
        cake_mf
    )


    wash_liquor_mass_fraction.append(
        liquor_mf
    )


# ------------------------------------------------------------
# Write washed-cake outlet stream
# ------------------------------------------------------------

washed_cake.Clear()


washed_cake.SetTemperature(
    wash_temperature
)


washed_cake.SetPressure(
    min(
        wet_cake_pressure,
        wash_water_pressure
    )
)


washed_cake.SetMassFlow(
    calculated_washed_cake_mass_flow
)


# DWSIM Python scripting requires a .NET Array[float]
# rather than a normal Python list for this method.
washed_cake.SetOverallMassComposition(
    Array[float](
        washed_cake_mass_fraction
    )
)


washed_cake.Calculate()


# ------------------------------------------------------------
# Write wash-liquor outlet stream
# ------------------------------------------------------------

wash_liquor.Clear()


wash_liquor.SetTemperature(
    wash_temperature
)


wash_liquor.SetPressure(
    min(
        wet_cake_pressure,
        wash_water_pressure
    )
)


wash_liquor.SetMassFlow(
    calculated_wash_liquor_mass_flow
)


# DWSIM Python scripting requires a .NET Array[float]
# rather than a normal Python list for this method.
wash_liquor.SetOverallMassComposition(
    Array[float](
        wash_liquor_mass_fraction
    )
)


wash_liquor.Calculate()


# ------------------------------------------------------------
# Diagnostics
# ------------------------------------------------------------

feed_total = (
    wet_cake_mass_flow +
    wash_water_mass_flow
)


out_total = (
    calculated_washed_cake_mass_flow +
    calculated_wash_liquor_mass_flow
)


mass_balance_error = (
    feed_total -
    out_total
)


li2co3_balance_error = (
    li2co3_in -
    li2co3_washed -
    li2co3_loss_mass_flow
)


# ------------------------------------------------------------
# Additional diagnostic temperatures
# ------------------------------------------------------------

wet_cake_temperature_C = (
    wet_cake_temperature - 273.15
)


wash_water_temperature_C = (
    wash_water_temperature - 273.15
)


wash_temperature_C = (
    wash_temperature - 273.15
)


# ------------------------------------------------------------
# Write diagnostics to DWSIM
# ------------------------------------------------------------

Flowsheet.WriteMessage(
    "------------------------------------------------------------"
)

Flowsheet.WriteMessage(
    "CUSTOM_Li2CO3_Washer"
)

Flowsheet.WriteMessage(
    "------------------------------------------------------------"
)

Flowsheet.WriteMessage(
    "Wet cake feed: "
    + str(
        wet_cake_mass_flow * 3600.0
    )
    + " kg/h"
)


Flowsheet.WriteMessage(
    "Wash water feed: "
    + str(
        wash_water_mass_flow * 3600.0
    )
    + " kg/h"
)


Flowsheet.WriteMessage(
    "Actual wash ratio: "
    + str(
        actual_wash_ratio
    )
    + " kg/kg wet cake"
)


Flowsheet.WriteMessage(
    "Wet cake temperature: "
    + str(
        wet_cake_temperature_C
    )
    + " degC"
)


Flowsheet.WriteMessage(
    "Wash water temperature: "
    + str(
        wash_water_temperature_C
    )
    + " degC"
)


Flowsheet.WriteMessage(
    "Calculated washer temperature: "
    + str(
        wash_temperature_C
    )
    + " degC"
)


Flowsheet.WriteMessage(
    "Li2CO3 entering washer: "
    + str(
        li2co3_in * 3600.0
    )
    + " kg/h"
)


Flowsheet.WriteMessage(
    "Li2CO3 solubility used: "
    + str(
        li2co3_solubility
    )
    + " g/L"
)


Flowsheet.WriteMessage(
    "Estimated Li2CO3 dissolved: "
    + str(
        li2co3_loss_mass_flow * 3600.0
    )
    + " kg/h"
)


Flowsheet.WriteMessage(
    "Li2CO3 remaining in washed cake: "
    + str(
        li2co3_washed * 3600.0
    )
    + " kg/h"
)


Flowsheet.WriteMessage(
    "Washed cake mass flow: "
    + str(
        calculated_washed_cake_mass_flow * 3600.0
    )
    + " kg/h"
)


Flowsheet.WriteMessage(
    "Washed cake moisture: "
    + str(
        FILTER_CAKE_MOISTURE * 100.0
    )
    + " wt%"
)


Flowsheet.WriteMessage(
    "Wash liquor mass flow: "
    + str(
        calculated_wash_liquor_mass_flow * 3600.0
    )
    + " kg/h"
)


Flowsheet.WriteMessage(
    "Total mass balance error: "
    + str(
        mass_balance_error
    )
    + " kg/s"
)


Flowsheet.WriteMessage(
    "Li2CO3 balance error: "
    + str(
        li2co3_balance_error
    )
    + " kg/s"
)


Flowsheet.WriteMessage(
    "------------------------------------------------------------"
)