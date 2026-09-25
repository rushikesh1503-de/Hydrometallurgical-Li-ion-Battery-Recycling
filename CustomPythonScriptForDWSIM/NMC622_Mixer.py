# ------------------------------------------------------------
# CUSTOM_NMC622_Mixer
#
# Purpose:
# Mix the three calcination-feed streams:
#
#   1. Dry_NMC622_Hydroxide
#   2. Li2CO3_to_NMC622
#   3. O2_Feed
#
# The calculation is performed using the low-level DWSIM
# PhaseProperties and Compound properties, consistent with the
# working custom-unit scripts used elsewhere in this project.
#
# The mixer performs:
#
#   - total mass-flow balance
#   - component mass-flow balance
#   - component molar-flow calculation
#   - overall molar-flow calculation
#   - mass-fraction calculation
#   - mole-fraction calculation
#   - mass-weighted temperature calculation
#   - pressure calculation
#   - enthalpy-flow calculation
#   - Li/M calculation
#   - O2/NMC622 molar ratio
#   - mass-balance closure
#   - mass-fraction closure
#   - mole-fraction closure
#
# The outlet is not flashed through the electrolyte property
# package. This is intentional because the calcination feed
# contains solid NMC622_Hydroxide, solid Lithium Carbonate and
# gaseous Oxygen.
# ------------------------------------------------------------


import clr

clr.AddReference("DWSIM.Interfaces")

from System import Double
from DWSIM import Interfaces


# ------------------------------------------------------------
# Helper function
#
# Converts a DWSIM value safely to a Python float.
# NaN and Infinity are also replaced by the supplied default.
# ------------------------------------------------------------

def safe_float(value, default_value):

    try:

        result = float(value)

        if Double.IsNaN(result):

            return default_value

        if Double.IsInfinity(result):

            return default_value

        return result

    except:

        return default_value


# ------------------------------------------------------------
# Streams
#
# ims1 / ims2 / ims3 are the three CustomUO inlet ports.
# oms1 is the CustomUO outlet port.
#
# Connector assignment:
#
#   ims1 = Dry_NMC622_Hydroxide
#   ims2 = Li2CO3_to_NMC622
#   ims3 = O2_Feed
#   oms1 = NMC622_Calcination_Feed
# ------------------------------------------------------------

feed_nmc = ims1

feed_li2co3 = ims2

feed_o2 = ims3

outflow = oms1


feeds = [

    feed_nmc,
    feed_li2co3,
    feed_o2

]


# ------------------------------------------------------------
# Check stream connections
# ------------------------------------------------------------

if feed_nmc is None:

    raise Exception(
        "CUSTOM_NMC622_Mixer: inlet 1 is not connected."
    )


if feed_li2co3 is None:

    raise Exception(
        "CUSTOM_NMC622_Mixer: inlet 2 is not connected."
    )


if feed_o2 is None:

    raise Exception(
        "CUSTOM_NMC622_Mixer: inlet 3 is not connected."
    )


if outflow is None:

    raise Exception(
        "CUSTOM_NMC622_Mixer: outlet is not connected."
    )


# ------------------------------------------------------------
# Initialize total balances
# ------------------------------------------------------------

total_mass_flow = 0.0

total_enthalpy_flow = 0.0

weighted_temperature = 0.0

outlet_pressure = 0.0


# ------------------------------------------------------------
# Component mass-flow dictionary
#
# Key:
#     DWSIM compound name
#
# Value:
#     component mass flow [kg/s]
# ------------------------------------------------------------

component_mass_flow = {}


# ------------------------------------------------------------
# Read inlet streams
#
# DWSIM low-level properties are used directly:
#
#   Properties.massflow
#   Properties.temperature
#   Properties.pressure
#   Properties.enthalpy
#   Compound.MassFraction
# ------------------------------------------------------------

for feed in feeds:

    feed.Validate()

    props = feed.Phases[0].Properties


    # --------------------------------------------------------
    # Read stream properties
    # --------------------------------------------------------

    mass_flow = safe_float(

        props.massflow,

        0.0

    )


    temperature = safe_float(

        props.temperature,

        298.15

    )


    pressure = safe_float(

        props.pressure,

        101325.0

    )


    enthalpy = safe_float(

        props.enthalpy,

        0.0

    )


    # --------------------------------------------------------
    # Total mass balance
    # --------------------------------------------------------

    total_mass_flow += mass_flow


    # --------------------------------------------------------
    # Mass-weighted temperature numerator
    #
    # The final outlet temperature is:
    #
    # T_out =
    #
    # SUM(m_i*T_i) / SUM(m_i)
    # --------------------------------------------------------

    weighted_temperature += (

        mass_flow
        * temperature

    )


    # --------------------------------------------------------
    # Total enthalpy flow
    #
    # H_flow =
    #
    # m_dot * h
    #
    # where:
    #
    # m_dot = kg/s
    # h     = kJ/kg
    # H     = kJ/s = kW
    # --------------------------------------------------------

    if not Double.IsNaN(enthalpy):

        if not Double.IsInfinity(enthalpy):

            total_enthalpy_flow += (

                mass_flow
                * enthalpy

            )


    # --------------------------------------------------------
    # Outlet pressure
    #
    # Minimum inlet pressure is used.
    # --------------------------------------------------------

    if outlet_pressure == 0.0:

        outlet_pressure = pressure

    elif pressure < outlet_pressure:

        outlet_pressure = pressure


    # --------------------------------------------------------
    # Component mass-flow balance
    #
    # m_i =
    #
    # w_i * m_total
    #
    # where w_i is the inlet component mass fraction.
    # --------------------------------------------------------

    for comp in feed.Phases[0].Compounds.Values:

        component_name = comp.Name

        mass_fraction = safe_float(

            comp.MassFraction,

            0.0

        )


        if component_name not in component_mass_flow:

            component_mass_flow[component_name] = 0.0


        component_mass_flow[component_name] += (

            mass_fraction
            * mass_flow

        )


# ------------------------------------------------------------
# Calculate outlet temperature
# ------------------------------------------------------------

if total_mass_flow > 0.0:

    outlet_temperature = (

        weighted_temperature
        / total_mass_flow

    )

else:

    outlet_temperature = 298.15

    Flowsheet.WriteMessage(
        "CUSTOM_NMC622_Mixer: WARNING -- total mass flow is zero."
    )


# ------------------------------------------------------------
# Calculate outlet specific enthalpy
#
# h_out =
#
# H_total / m_total
# ------------------------------------------------------------

if total_mass_flow > 0.0:

    outlet_specific_enthalpy = (

        total_enthalpy_flow
        / total_mass_flow

    )

else:

    outlet_specific_enthalpy = 0.0


# ------------------------------------------------------------
# Clear old outlet values
# ------------------------------------------------------------

outflow.Clear()

outflow.ClearAllProps()


# ------------------------------------------------------------
# Write basic outlet properties
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
# Set the mixed-stream enthalpy.
#
# This is the mass-weighted inlet enthalpy.
#
# It is retained as a diagnostic/stream property and avoids
# leaving the outlet enthalpy undefined.
# ------------------------------------------------------------

outflow.Phases[0].Properties.enthalpy = (

    outlet_specific_enthalpy

)


# ------------------------------------------------------------
# Define the outlet flow basis
# ------------------------------------------------------------

outflow.DefinedFlow = (

    Interfaces.Enums.FlowSpec.Mass

)


# ------------------------------------------------------------
# Set overall phase fractions
#
# The complete outlet composition belongs to the overall
# mixture represented by Phase 0.
# ------------------------------------------------------------

outflow.Phases[0].Properties.massfraction = 1.0

outflow.Phases[0].Properties.molarfraction = 1.0


# ------------------------------------------------------------
# Calculate and write component mass fractions
#
# w_i =
#
# m_i / m_total
# ------------------------------------------------------------

for comp in outflow.Phases[0].Compounds.Values:

    component_name = comp.Name


    if (

        total_mass_flow > 0.0
        and component_name in component_mass_flow

    ):

        comp.MassFraction = (

            component_mass_flow[component_name]
            / total_mass_flow

        )

    else:

        comp.MassFraction = 0.0


# ------------------------------------------------------------
# Normalize mass fractions
#
# This removes numerical round-off so that the sum is exactly
# approximately 1.0.
# ------------------------------------------------------------

mass_fraction_sum = 0.0


for comp in outflow.Phases[0].Compounds.Values:

    mass_fraction_sum += safe_float(

        comp.MassFraction,

        0.0

    )


if mass_fraction_sum > 0.0:

    for comp in outflow.Phases[0].Compounds.Values:

        comp.MassFraction = (

            comp.MassFraction
            / mass_fraction_sum

        )


# ------------------------------------------------------------
# Calculate mole fractions
#
# DWSIM molecular weight is stored as kg/kmol.
#
# Therefore:
#
#   mass_fraction / MW
#
# is proportional to the molar amount.
#
# The common conversion factor cancels when calculating the
# normalized mole fraction.
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

            mass_fraction
            / mw

        )


# ------------------------------------------------------------
# Write mole fractions
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
# Component molar flows
#
# IMPORTANT UNIT CONVERSION
#
# DWSIM molecular weight:
#
#     kg/kmol
#
# Component mass flow:
#
#     kg/s
#
# Therefore:
#
#     kg/s
#     ---------------- = kmol/s
#     kg/kmol
#
# DWSIM's component MolarFlow is in mol/s.
#
# Therefore:
#
#     mol/s = kg/s / (kg/kmol) * 1000
#
# This is the same conversion used in DWSIM's own component
# separation calculations.
# ------------------------------------------------------------

component_molar_flow = {}


total_molar_flow = 0.0


for comp in outflow.Phases[0].Compounds.Values:

    component_name = comp.Name

    mw = safe_float(

        comp.ConstantProperties.Molar_Weight,

        0.0

    )

    component_mass = component_mass_flow.get(

        component_name,

        0.0

    )


    if mw > 0.0:

        component_moles = (

            component_mass
            / mw
            * 1000.0

        )

    else:

        component_moles = 0.0


    component_molar_flow[component_name] = (

        component_moles

    )


    total_molar_flow += component_moles


# ------------------------------------------------------------
# Write component mass flow and molar flow
#
# This makes the individual compound flow values consistent
# with the overall stream flow.
# ------------------------------------------------------------

for comp in outflow.Phases[0].Compounds.Values:

    component_name = comp.Name


    if component_name in component_mass_flow:

        comp.MassFlow = (

            component_mass_flow[component_name]

        )

    else:

        comp.MassFlow = 0.0


    if component_name in component_molar_flow:

        comp.MolarFlow = (

            component_molar_flow[component_name]

        )

    else:

        comp.MolarFlow = 0.0


# ------------------------------------------------------------
# Write total molar flow
#
# DWSIM reports this property in mol/s for the current unit
# system.
# ------------------------------------------------------------

outflow.Phases[0].Properties.molarflow = (

    total_molar_flow

)


# ------------------------------------------------------------
# Calculate mixture molecular weight
#
# Since:
#
#   m_dot = kg/s
#   n_dot = mol/s
#
# the mixture molecular weight in kg/kmol is:
#
#   MW_mix =
#
#   m_dot / n_dot * 1000
# ------------------------------------------------------------

if total_molar_flow > 0.0:

    outlet_molecular_weight = (

        total_mass_flow
        / total_molar_flow
        * 1000.0

    )

else:

    outlet_molecular_weight = 0.0


# ------------------------------------------------------------
# Calculate molar enthalpy
#
# Specific enthalpy:
#
#   kJ/kg
#
# Molar flow:
#
#   mol/s
#
# Therefore:
#
#   H_molar =
#
#   h_mass * MW_mix
#
# with MW_mix in kg/mol.
#
# Since MW_mix is stored/reported in kg/kmol:
#
#   MW_mix / 1000 = kg/mol
#
# ------------------------------------------------------------

if outlet_molecular_weight > 0.0:

    outlet_molar_enthalpy = (

        outlet_specific_enthalpy
        * outlet_molecular_weight
        / 1000.0

    )

else:

    outlet_molar_enthalpy = 0.0


# ------------------------------------------------------------
# Calculate important reaction component molar flows
# ------------------------------------------------------------

n_nmc = 0.0

n_li2co3 = 0.0

n_o2 = 0.0


for comp in outflow.Phases[0].Compounds.Values:

    component_name = comp.Name


    if component_name in component_molar_flow:

        component_n = (

            component_molar_flow[component_name]

        )

    else:

        component_n = 0.0


    if component_name == "NMC622_Hydroxide":

        n_nmc = component_n


    elif component_name == "Lithium Carbonate":

        n_li2co3 = component_n


    elif component_name == "Oxygen":

        n_o2 = component_n


# ------------------------------------------------------------
# Calculate Li/M ratio
#
# Reaction-basis calculation:
#
# Li/M =
#
# 2 * n(Li2CO3)
# ---------------------
# n(NMC622_Hydroxide)
#
# Li2CO3 contains two Li atoms.
# ------------------------------------------------------------

if n_nmc > 0.0:

    li_m_ratio = (

        2.0
        * n_li2co3
        / n_nmc

    )

else:

    li_m_ratio = 0.0


# ------------------------------------------------------------
# Calculate O2/NMC622 molar ratio
# ------------------------------------------------------------

if n_nmc > 0.0:

    o2_nmc_ratio = (

        n_o2
        / n_nmc

    )

else:

    o2_nmc_ratio = 0.0


# ------------------------------------------------------------
# Calculate component mass-balance closure
# ------------------------------------------------------------

calculated_component_mass = sum(

    component_mass_flow.values()

)


mass_balance_error = (

    calculated_component_mass
    - total_mass_flow

)


# ------------------------------------------------------------
# Calculate relative mass-balance error
# ------------------------------------------------------------

if total_mass_flow > 0.0:

    mass_balance_relative_error = (

        mass_balance_error
        / total_mass_flow

    )

else:

    mass_balance_relative_error = 0.0


# ------------------------------------------------------------
# Calculate mass-fraction closure
# ------------------------------------------------------------

mass_fraction_sum_final = 0.0


for comp in outflow.Phases[0].Compounds.Values:

    mass_fraction_sum_final += safe_float(

        comp.MassFraction,

        0.0

    )


mass_fraction_error = (

    mass_fraction_sum_final
    - 1.0

)


# ------------------------------------------------------------
# Calculate mole-fraction closure
# ------------------------------------------------------------

mole_fraction_sum = 0.0


for comp in outflow.Phases[0].Compounds.Values:

    mole_fraction_sum += safe_float(

        comp.MoleFraction,

        0.0

    )


mole_fraction_error = (

    mole_fraction_sum
    - 1.0

)


# ------------------------------------------------------------
# Prevent DWSIM from automatically performing another
# thermodynamic calculation on this custom mixed-phase stream.
#
# CalculationRoutineOverride MUST be assigned an actual
# callable function when OverrideCalculationRoutine is True.
#
# This prevents the previous "Object reference not set to an
# instance of an object" error.
# ------------------------------------------------------------

def _hold_calcination_feed_values():

    pass


outflow.OverrideCalculationRoutine = True

outflow.CalculationRoutineOverride = (

    _hold_calcination_feed_values

)


# ------------------------------------------------------------
# Stream specification
#
# The custom mixer explicitly defines temperature and pressure.
# ------------------------------------------------------------

outflow.SpecType = (

    Interfaces.Enums.StreamSpec.Temperature_and_Pressure

)


# ------------------------------------------------------------
# Diagnostics
# ------------------------------------------------------------

Flowsheet.WriteMessage("")

Flowsheet.WriteMessage(
    "------------------------------------------------------------"
)

Flowsheet.WriteMessage(
    "CUSTOM_NMC622_Mixer"
)

Flowsheet.WriteMessage(
    "------------------------------------------------------------"
)

Flowsheet.WriteMessage(
    "NMC622 hydroxide inlet mass flow = "
    + str(
        safe_float(
            feed_nmc.Phases[0].Properties.massflow,
            0.0
        )
    )
    + " kg/s"
)

Flowsheet.WriteMessage(
    "Li2CO3 inlet mass flow           = "
    + str(
        safe_float(
            feed_li2co3.Phases[0].Properties.massflow,
            0.0
        )
    )
    + " kg/s"
)

Flowsheet.WriteMessage(
    "O2 inlet mass flow                = "
    + str(
        safe_float(
            feed_o2.Phases[0].Properties.massflow,
            0.0
        )
    )
    + " kg/s"
)

Flowsheet.WriteMessage(
    "------------------------------------------------------------"
)

Flowsheet.WriteMessage(
    "Total outlet mass flow           = "
    + str(total_mass_flow)
    + " kg/s"
)

Flowsheet.WriteMessage(
    "Total outlet molar flow          = "
    + str(total_molar_flow)
    + " mol/s"
)

Flowsheet.WriteMessage(
    "Mixed temperature                = "
    + str(outlet_temperature)
    + " K"
)

Flowsheet.WriteMessage(
    "Outlet pressure                  = "
    + str(outlet_pressure)
    + " Pa"
)

Flowsheet.WriteMessage(
    "Mixture molecular weight         = "
    + str(outlet_molecular_weight)
    + " kg/kmol"
)

Flowsheet.WriteMessage(
    "------------------------------------------------------------"
)

Flowsheet.WriteMessage(
    "Total enthalpy flow              = "
    + str(total_enthalpy_flow)
    + " kW"
)

Flowsheet.WriteMessage(
    "Specific enthalpy                = "
    + str(outlet_specific_enthalpy)
    + " kJ/kg"
)

Flowsheet.WriteMessage(
    "Molar enthalpy                   = "
    + str(outlet_molar_enthalpy)
    + " kJ/mol"
)

Flowsheet.WriteMessage(
    "------------------------------------------------------------"
)

Flowsheet.WriteMessage(
    "NMC622 hydroxide molar flow      = "
    + str(n_nmc)
    + " mol/s"
)

Flowsheet.WriteMessage(
    "Li2CO3 molar flow                = "
    + str(n_li2co3)
    + " mol/s"
)

Flowsheet.WriteMessage(
    "O2 molar flow                    = "
    + str(n_o2)
    + " mol/s"
)

Flowsheet.WriteMessage(
    "Li/M ratio                       = "
    + str(li_m_ratio)
)

Flowsheet.WriteMessage(
    "O2/NMC622 molar ratio            = "
    + str(o2_nmc_ratio)
)

Flowsheet.WriteMessage(
    "------------------------------------------------------------"
)

Flowsheet.WriteMessage(
    "Component mass balance error     = "
    + str(mass_balance_error)
    + " kg/s"
)

Flowsheet.WriteMessage(
    "Relative mass balance error      = "
    + str(mass_balance_relative_error)
)

Flowsheet.WriteMessage(
    "Mass-fraction sum                = "
    + str(mass_fraction_sum_final)
)

Flowsheet.WriteMessage(
    "Mass-fraction closure error      = "
    + str(mass_fraction_error)
)

Flowsheet.WriteMessage(
    "Mole-fraction sum                = "
    + str(mole_fraction_sum)
)

Flowsheet.WriteMessage(
    "Mole-fraction closure error      = "
    + str(mole_fraction_error)
)

Flowsheet.WriteMessage(
    "------------------------------------------------------------"
)

Flowsheet.WriteMessage("")