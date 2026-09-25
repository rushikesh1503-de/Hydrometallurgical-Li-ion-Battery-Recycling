# ------------------------------------------------------------
# CUSTOM_NMC_Hydroxide_Dryer
#
# Purpose:
#   Remove water from the washed NMC622 hydroxide cake.
#
# Process:
#   Heated_Wet_Cake
#          |
#          v
#   CUSTOM_NMC_Hydroxide_Dryer
#          |
#          +------> Dryer_Offgas
#          |
#          v
#   Dry_NMC622_Hydroxide
#
# Modeling basis:
#   - Drying removes water only.
#   - NMC622_Hydroxide remains in the product.
#   - Nonvolatile soluble residues remain with the product.
#   - No additional separation of soluble residues occurs
#     during drying.
#
# DWSIM limitation:
#   The final dry product contains the custom
#   NMC622_Hydroxide pseudo-component and trace electrolyte
#   species. Normal electrolyte PH flashing causes
#   temperature-convergence failure.
#
# Therefore:
#   - Component mass flows are calculated explicitly.
#   - Component molar flows are calculated explicitly.
#   - Composition is calculated explicitly.
#   - The final output values are protected using
#     OverrideCalculationRoutine so DWSIM does not
#     re-flash the dry product.
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
# DRYING ASSUMPTION
# ------------------------------------------------------------
#
# DRYING_EFFICIENCY = fraction of water removed.
#
# 1.0 = 100% of the water present in the washed cake
#       is removed in the drying calculation.
#
# This is a modeling assumption for the screening-level
# mass balance. It is not being claimed as a measured
# dryer efficiency.
# ------------------------------------------------------------

DRYING_EFFICIENCY = 1.0


# ------------------------------------------------------------
# STREAM CONNECTIONS
# ------------------------------------------------------------

feed = ims1
dry_product = oms1
offgas = oms2


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
    383.15
)

pressure = safe_float(
    feed_props.pressure,
    101325.0
)


# ------------------------------------------------------------
# CALCULATE COMPONENT MASS FLOWS IN THE WET CAKE
# ------------------------------------------------------------
#
# For every component:
#
#   m_i = w_i * m_total
#
# where:
#
#   m_i     = component mass flow [kg/s]
#   w_i     = component mass fraction [-]
#   m_total = total stream mass flow [kg/s]
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
# WATER REMOVAL
# ------------------------------------------------------------

water_in = component_mass_flow.get(
    "Water",
    0.0
)

water_removed = (
    water_in * DRYING_EFFICIENCY
)

water_remaining = (
    water_in - water_removed
)


# ------------------------------------------------------------
# DRY PRODUCT COMPONENT FLOWS
# ------------------------------------------------------------
#
# All non-water components remain in the dry product.
#
# Water remaining after drying:
#
#   m_water,out = m_water,in - m_water,removed
#
# With 100% drying efficiency:
#
#   m_water,out = 0
# ------------------------------------------------------------

dry_component_flow = dict(
    component_mass_flow
)

dry_component_flow["Water"] = (
    water_remaining
)

dry_mass_flow = sum(
    dry_component_flow.values()
)


# ------------------------------------------------------------
# DRYER OFFGAS COMPONENT FLOWS
# ------------------------------------------------------------
#
# Only the removed water is assigned to the dryer offgas.
#
# No dissolved salts or NMC hydroxide are transferred
# to the offgas.
# ------------------------------------------------------------

offgas_component_flow = {
    "Water": water_removed
}

offgas_mass_flow = water_removed


# ------------------------------------------------------------
# WRITE STREAM VALUES
# ------------------------------------------------------------

def write_stream(
    stream,
    component_flow,
    total_mass_flow,
    temp,
    pres
):

    # --------------------------------------------------------
    # TOTAL STREAM PROPERTIES
    # --------------------------------------------------------

    stream.Phases[0].Properties.massflow = (
        total_mass_flow
    )

    stream.Phases[0].Properties.temperature = (
        temp
    )

    stream.Phases[0].Properties.pressure = (
        pres
    )

    stream.DefinedFlow = (
        Interfaces.Enums.FlowSpec.Mass
    )

    stream.SpecType = (
        Interfaces.Enums.StreamSpec.Temperature_and_Pressure
    )


    # --------------------------------------------------------
    # CALCULATE TOTAL MOLAR FLOW
    # --------------------------------------------------------
    #
    # For each component:
    #
    #   n_i = m_i / MW_i
    #
    # where:
    #
    #   m_i  = component mass flow [kg/s]
    #   MW_i = molecular weight [kg/kmol]
    #
    # This gives kmol/s.
    #
    # Convert to mol/s:
    #
    #   mol/s = kmol/s * 1000
    # --------------------------------------------------------

    total_kmol_per_s = 0.0

    for comp in stream.Phases[0].Compounds.Values:

        name = comp.Name

        flow = component_flow.get(
            name,
            0.0
        )

        mw = safe_float(
            comp.ConstantProperties.Molar_Weight,
            0.0
        )

        if mw > 0.0:
            total_kmol_per_s += (
                flow / mw
            )


    total_molar_flow = (
        total_kmol_per_s * 1000.0
    )

    stream.Phases[0].Properties.molarflow = (
        total_molar_flow
    )


    # --------------------------------------------------------
    # WRITE COMPONENT MASS FLOW
    # AND COMPONENT MOLAR FLOW
    # --------------------------------------------------------
    #
    # This is the important correction.
    #
    # Because the output stream is protected from the normal
    # DWSIM calculation, we explicitly populate:
    #
    #   comp.MassFlow
    #   comp.MolarFlow
    #
    # instead of relying on DWSIM to calculate them later.
    # --------------------------------------------------------

    for comp in stream.Phases[0].Compounds.Values:

        name = comp.Name

        flow = component_flow.get(
            name,
            0.0
        )

        mw = safe_float(
            comp.ConstantProperties.Molar_Weight,
            0.0
        )


        # ----------------------------------------------------
        # COMPONENT MASS FLOW
        # ----------------------------------------------------

        comp.MassFlow = flow


        # ----------------------------------------------------
        # COMPONENT MOLAR FLOW
        # ----------------------------------------------------

        if mw > 0.0:

            comp.MolarFlow = (
                flow / mw * 1000.0
            )

        else:

            comp.MolarFlow = 0.0


        # ----------------------------------------------------
        # COMPONENT MASS FRACTION
        # ----------------------------------------------------

        if total_mass_flow > 0.0:

            comp.MassFraction = (
                flow / total_mass_flow
            )

        else:

            comp.MassFraction = 0.0


    # --------------------------------------------------------
    # MOLE FRACTIONS
    # --------------------------------------------------------

    if total_molar_flow > 0.0:

        for comp in stream.Phases[0].Compounds.Values:

            name = comp.Name

            flow = component_flow.get(
                name,
                0.0
            )

            mw = safe_float(
                comp.ConstantProperties.Molar_Weight,
                0.0
            )

            if mw > 0.0:

                component_molar_flow = (
                    flow / mw * 1000.0
                )

                comp.MoleFraction = (
                    component_molar_flow
                    / total_molar_flow
                )

            else:

                comp.MoleFraction = 0.0

    else:

        for comp in stream.Phases[0].Compounds.Values:

            comp.MoleFraction = 0.0


# ------------------------------------------------------------
# WRITE DRY PRODUCT
# ------------------------------------------------------------

write_stream(
    dry_product,
    dry_component_flow,
    dry_mass_flow,
    temperature,
    pressure
)


# ------------------------------------------------------------
# WRITE DRYER OFFGAS
# ------------------------------------------------------------

write_stream(
    offgas,
    offgas_component_flow,
    offgas_mass_flow,
    temperature,
    pressure
)


# ------------------------------------------------------------
# PREVENT DWSIM FROM RE-FLASHING THE OUTPUT STREAMS
# ------------------------------------------------------------
#
# The stream values have already been calculated explicitly.
#
# The override prevents DWSIM from sending the dry product
# back through the electrolyte PH flash, which previously
# caused:
#
#   PH Flash [Electrolyte]:
#   Temperature did not converge
#
# The override is therefore a software protection mechanism,
# not a physical drying assumption.
# ------------------------------------------------------------

def hold_dry_product_values():
    pass


dry_product.OverrideCalculationRoutine = True

dry_product.CalculationRoutineOverride = (
    hold_dry_product_values
)


# ------------------------------------------------------------
# PROTECT OFFGAS STREAM
# ------------------------------------------------------------

def hold_offgas_values():
    pass


offgas.OverrideCalculationRoutine = True

offgas.CalculationRoutineOverride = (
    hold_offgas_values
)


# ------------------------------------------------------------
# DIAGNOSTICS
# ------------------------------------------------------------

mass_balance_error = (
    inlet_mass_flow
    - dry_mass_flow
    - offgas_mass_flow
)


Flowsheet.WriteMessage(
    "CUSTOM_NMC_Hydroxide_Dryer: calculation completed."
)

Flowsheet.WriteMessage(
    "Inlet mass flow = "
    + str(inlet_mass_flow)
    + " kg/s"
)

Flowsheet.WriteMessage(
    "Dry product mass flow = "
    + str(dry_mass_flow)
    + " kg/s"
)

Flowsheet.WriteMessage(
    "Dryer offgas mass flow = "
    + str(offgas_mass_flow)
    + " kg/s"
)

Flowsheet.WriteMessage(
    "Water removed = "
    + str(water_removed)
    + " kg/s"
)

Flowsheet.WriteMessage(
    "Mass balance error = "
    + str(mass_balance_error)
    + " kg/s"
)