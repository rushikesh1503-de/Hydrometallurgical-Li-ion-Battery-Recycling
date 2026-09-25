
# ------------------------------------------------------------
# Manual mixer for BM + H2SO4 + H2O2
#
# Inlet 1 = BM
# Inlet 2 = H2SO4_Feed
# Inlet 3 = H2O2_Feed
# Outlet 1 = Leach_Feed
# ------------------------------------------------------------

import clr
clr.AddReference("DWSIM.Interfaces")

from System import Double
from DWSIM import Interfaces


# ------------------------------------------------------------
# Helper function
# ------------------------------------------------------------

def safe_float(value, default_value):
    try:
        return float(value)
    except:
        return default_value


# ------------------------------------------------------------
# Streams
# ------------------------------------------------------------

feed1 = ims1
feed2 = ims2
feed3 = ims3

outflow = oms1

feeds = [feed1, feed2, feed3]


# ------------------------------------------------------------
# Initialize
# ------------------------------------------------------------

total_mass_flow = 0.0
total_enthalpy_flow = 0.0

weighted_temperature = 0.0

outlet_pressure = 0.0

component_mass_flow = {}


# ------------------------------------------------------------
# Read inlet streams
# ------------------------------------------------------------

for feed in feeds:

    # Validate inlet
    feed.Validate()

    props = feed.Phases[0].Properties

    # Mass flow
    mass_flow = safe_float(
        props.massflow,
        0.0
    )

    # Temperature
    temperature = safe_float(
        props.temperature,
        298.15
    )

    # Pressure
    pressure = safe_float(
        props.pressure,
        101325.0
    )

    # Enthalpy
    enthalpy = safe_float(
        props.enthalpy,
        0.0
    )


    # --------------------------------------------------------
    # Total mass flow
    # --------------------------------------------------------

    total_mass_flow += mass_flow


    # --------------------------------------------------------
    # Total enthalpy flow
    # --------------------------------------------------------

    if not Double.IsNaN(enthalpy):

        total_enthalpy_flow += (
            mass_flow * enthalpy
        )


    # --------------------------------------------------------
    # Minimum inlet pressure
    # --------------------------------------------------------

    if outlet_pressure == 0.0:

        outlet_pressure = pressure

    elif pressure < outlet_pressure:

        outlet_pressure = pressure


    # --------------------------------------------------------
    # Mass-weighted temperature
    # --------------------------------------------------------

    if total_mass_flow != 0.0:

        weighted_temperature += (
            mass_flow * temperature
        )


    # --------------------------------------------------------
    # Component mass-flow balance
    # --------------------------------------------------------

    for comp in feed.Phases[0].Compounds.Values:

        component_name = comp.Name

        if component_name not in component_mass_flow:

            component_mass_flow[component_name] = 0.0

        mass_fraction = safe_float(
            comp.MassFraction,
            0.0
        )

        component_mass_flow[component_name] += (
            mass_fraction * mass_flow
        )


# ------------------------------------------------------------
# Calculate outlet temperature
# ------------------------------------------------------------

if total_mass_flow > 0.0:

    outlet_temperature = (
        weighted_temperature / total_mass_flow
    )

else:

    outlet_temperature = 298.15


# ------------------------------------------------------------
# Calculate outlet specific enthalpy
# ------------------------------------------------------------

if total_mass_flow > 0.0:

    outlet_specific_enthalpy = (
        total_enthalpy_flow / total_mass_flow
    )

else:

    outlet_specific_enthalpy = 0.0


# ------------------------------------------------------------
# Clear outlet
# ------------------------------------------------------------

outflow.Clear()

outflow.ClearAllProps()


# ------------------------------------------------------------
# Set outlet basic properties
# ------------------------------------------------------------

outflow.Phases[0].Properties.massflow = (
    total_mass_flow
)

outflow.Phases[0].Properties.pressure = (
    outlet_pressure
)

outflow.Phases[0].Properties.temperature = (
    outlet_temperature
)


# ------------------------------------------------------------
# Set mass flow specification
# ------------------------------------------------------------

outflow.DefinedFlow = (
    Interfaces.Enums.FlowSpec.Mass
)

# ------------------------------------------------------------
# Set component mass fractions
# ------------------------------------------------------------

for comp in outflow.Phases[0].Compounds.Values:

    component_name = comp.Name

    if total_mass_flow > 0.0:

        if component_name in component_mass_flow:

            comp.MassFraction = (
                component_mass_flow[component_name]
                / total_mass_flow
            )

        else:

            comp.MassFraction = 0.0

    else:

        comp.MassFraction = 0.0


# ------------------------------------------------------------
# Calculate mole fractions from mass fractions
# ------------------------------------------------------------

mass_divided_by_mw = 0.0


for comp in outflow.Phases[0].Compounds.Values:

    mw = safe_float(
        comp.ConstantProperties.Molar_Weight,
        0.0
    )

    mass_fraction = safe_float(
        comp.MassFraction,
        0.0
    )

    if mw > 0.0:

        mass_divided_by_mw += (
            mass_fraction / mw
        )


# ------------------------------------------------------------
# Normalize mole fractions
# ------------------------------------------------------------

for comp in outflow.Phases[0].Compounds.Values:

    mw = safe_float(
        comp.ConstantProperties.Molar_Weight,
        0.0
    )

    mass_fraction = safe_float(
        comp.MassFraction,
        0.0
    )

    if (
        total_mass_flow > 0.0
        and mass_divided_by_mw > 0.0
        and mw > 0.0
    ):

        comp.MoleFraction = (
            mass_fraction
            / mw
            / mass_divided_by_mw
        )

    else:

        comp.MoleFraction = 0.0


# ------------------------------------------------------------
# IMPORTANT:
# Keep outlet specification as Temperature + Pressure.
#
# This avoids forcing an electrolyte PH flash at the mixer
# ------------------------------------------------------------

outflow.SpecType = (
    Interfaces.Enums.StreamSpec.Temperature_and_Pressure
)

# ------------------------------------------------------------
# Diagnostic messages
# ------------------------------------------------------------

Flowsheet.WriteMessage(
    "CUSTOM-1: Mixer calculation completed."
)

Flowsheet.WriteMessage(
    "Total mass flow = "
    + str(total_mass_flow)
    + " kg/s"
)

Flowsheet.WriteMessage(
    "Outlet temperature = "
    + str(outlet_temperature)
    + " K"
)

Flowsheet.WriteMessage(
    "Outlet pressure = "
    + str(outlet_pressure)
    + " Pa"
)

Flowsheet.WriteMessage(
    "Outlet specific enthalpy = "
    + str(outlet_specific_enthalpy)
    + " kJ/kg"
)
