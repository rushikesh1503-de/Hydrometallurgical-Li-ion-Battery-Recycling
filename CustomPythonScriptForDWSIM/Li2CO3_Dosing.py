# ------------------------------------------------------------
# CUSTOM_Li2CO3_Dosing
#
# Purpose:
#   Split the recovered dry Li2CO3 into:
#
#       1. Excess_Li2CO3
#       2. Li2CO3_to_NMC622
#
# Process:
#
#       Dry_Li2CO3
#             |
#             v
#       CUSTOM_Li2CO3_Dosing
#             |
#             +------------------> Excess_Li2CO3
#             |
#             +------------------> Li2CO3_to_NMC622
#
# ------------------------------------------------------------
#
# MODELING PURPOSE
#
# This custom unit operation replaces the native DWSIM
# Splitter.
#
# The native Splitter was causing:
#
#       PH Flash [Electrolyte]:
#       Invalid result:
#       Temperature did not converge
#
# The reason is that the upstream process uses an electrolyte
# property package, while the recovered Li2CO3 after drying
# is represented as a dry solid product.
#
# A simple mass split does not require an electrolyte
# equilibrium calculation.
#
# Therefore this unit operation:
#
#       - reads Dry_Li2CO3
#       - calculates component mass flows
#       - divides the material between two outlets
#       - explicitly assigns both outlets to the Solid phase
#       - explicitly sets the Solid phase fraction to 1
#       - sets all other phase fractions to 0
#       - prevents normal outlet-stream recalculation
#
# ------------------------------------------------------------
#
# STOICHIOMETRIC BASIS
#
# NMC622 precursor:
#
#       Ni0.6Co0.2Mn0.2(OH)2
#
# Literature regeneration basis:
#
#       Li/M = 1.06
#
# For one mole of precursor:
#
#       M = 0.6 + 0.2 + 0.2
#         = 1.0 mol
#
# Therefore:
#
#       Li atoms required = 1.06 mol
#
# Since Li2CO3 contains two Li atoms:
#
#       Li2CO3 required
#       = 1.06 / 2
#       = 0.53 mol Li2CO3/mol precursor
#
# ------------------------------------------------------------
#
# CURRENT PROJECT BASIS
#
# Current recovered dry Li2CO3:
#
#       approximately 1.0049 kg/h
#
# Required Li2CO3 for the current NMC622 hydroxide feed:
#
#       approximately 0.2510 kg/h
#
# Therefore:
#
#       Li2CO3_to_NMC622 = 24.98%
#
#       Excess_Li2CO3    = 75.02%
#
# ------------------------------------------------------------
#
# LITERATURE
#
# Gu et al., RSC Advances, 2023:
#
# "Regeneration of NCM622 from end-of-life lithium-ion
# cathode materials"
#
# DOI:
#
#       10.1039/D2RA06937G
#
# The study used Li/M = 1.06 followed by calcination
# at 800 degC for 12 h under pure O2.
#
# https://doi.org/10.1039/D2RA06937G
#
# ------------------------------------------------------------


import clr
import System

clr.AddReference("DWSIM.Interfaces")

from System import Array
from DWSIM import Interfaces


# ------------------------------------------------------------
# HELPER FUNCTION
# ------------------------------------------------------------

def safe_float(value, default_value):

    try:

        value = float(value)

        if value != value:

            return default_value

        return value

    except:

        return default_value

EXCESS_SPLIT = 0.7502

NMC622_SPLIT = 0.2498


# ------------------------------------------------------------
# CHECK SPLIT FRACTIONS
# ------------------------------------------------------------

split_total = (
    EXCESS_SPLIT +
    NMC622_SPLIT
)


if abs(split_total - 1.0) > 1.0e-8:

    raise Exception(
        "CUSTOM_Li2CO3_Dosing: "
        "Split fractions must add to 1.0."
    )


# ------------------------------------------------------------
# STREAM CONNECTIONS
# ------------------------------------------------------------
#
# ims1:
#
#       Dry_Li2CO3
#
# oms1:
#
#       Excess_Li2CO3
#
# oms2:
#
#       Li2CO3_to_NMC622
# ------------------------------------------------------------

feed = ims1

excess_product = oms1

nmc_product = oms2


# ------------------------------------------------------------
# READ INLET STREAM
# ------------------------------------------------------------

feed.Validate()


feed_properties = (
    feed.Phases[0].Properties
)


inlet_mass_flow = safe_float(
    feed_properties.massflow,
    0.0
)


temperature = safe_float(
    feed_properties.temperature,
    373.15
)


pressure = safe_float(
    feed_properties.pressure,
    101325.0
)


# ------------------------------------------------------------
# CHECK INLET
# ------------------------------------------------------------

if inlet_mass_flow <= 0.0:

    raise Exception(
        "CUSTOM_Li2CO3_Dosing: "
        "Dry_Li2CO3 inlet mass flow is zero."
    )


# ------------------------------------------------------------
# READ INLET COMPONENT MASS FLOWS
# ------------------------------------------------------------
#
# The inlet composition is preserved in both outlets.
#
#       m_i = w_i × m_total
#
# where:
#
#       m_i     = component mass flow [kg/s]
#       w_i     = component mass fraction
#       m_total = total mass flow [kg/s]
# ------------------------------------------------------------

inlet_component_mass_flow = {}


for comp in feed.Phases[0].Compounds.Values:

    name = comp.Name


    mass_fraction = safe_float(
        comp.MassFraction,
        0.0
    )


    inlet_component_mass_flow[name] = (
        mass_fraction *
        inlet_mass_flow
    )


# ------------------------------------------------------------
# CHECK Li2CO3
# ------------------------------------------------------------

li2co3_in = (
    inlet_component_mass_flow.get(
        "Lithium Carbonate",
        0.0
    )
)


if li2co3_in <= 0.0:

    raise Exception(
        "CUSTOM_Li2CO3_Dosing: "
        "Lithium Carbonate mass flow is zero."
    )


# ------------------------------------------------------------
# CALCULATE OUTLET TOTAL MASS FLOWS
# ------------------------------------------------------------

excess_mass_flow = (
    inlet_mass_flow *
    EXCESS_SPLIT
)


nmc_mass_flow = (
    inlet_mass_flow *
    NMC622_SPLIT
)


# ------------------------------------------------------------
# CALCULATE OUTLET COMPONENT MASS FLOWS
# ------------------------------------------------------------
#
# The complete inlet composition is split proportionally.
#
# Therefore:
#
#       m_i,excess =
#       m_i,in × EXCESS_SPLIT
#
#
#       m_i,NMC =
#       m_i,in × NMC622_SPLIT
# ------------------------------------------------------------

excess_component_mass_flow = {}

nmc_component_mass_flow = {}


for name in inlet_component_mass_flow:

    inlet_component_flow = (
        inlet_component_mass_flow[name]
    )


    excess_component_mass_flow[name] = (
        inlet_component_flow *
        EXCESS_SPLIT
    )


    nmc_component_mass_flow[name] = (
        inlet_component_flow *
        NMC622_SPLIT
    )


# ------------------------------------------------------------
# Li2CO3 DISTRIBUTION
# ------------------------------------------------------------

li2co3_excess = (
    li2co3_in *
    EXCESS_SPLIT
)


li2co3_to_nmc = (
    li2co3_in *
    NMC622_SPLIT
)


# ------------------------------------------------------------
# STREAM OVERRIDE ROUTINES
# ------------------------------------------------------------
#
# The custom unit operation explicitly calculates the outlet
# streams.
#
# These empty routines prevent DWSIM from replacing the
# explicitly calculated outlet values with a subsequent
# electrolyte PH flash when the stream itself is solved.
#
# DWSIM supports OverrideCalculationRoutine at the simulation
# object level.
# ------------------------------------------------------------

def hold_excess_values():

    pass


def hold_nmc_values():

    pass


# ------------------------------------------------------------
# RESET ALL PHASES
# ------------------------------------------------------------
#
# DWSIM uses the following phase indices:
#
#       0 = Mixture
#       1 = Liquid
#       2 = Vapor
#       3 = Liquid 1
#       4 = Liquid 2
#       5 = Liquid 3
#       6 = Aqueous
#       7 = Solid
#
# The important correction in this version is that we do not
# only write values into stream.Solid.
#
# We also explicitly set:
#
#       Solid molar fraction = 1
#       Solid mass fraction  = 1
#
# and all other physical phases to zero.
#
# This is required because DWSIM's property-package routines
# use the phase fraction when calculating phase flows.
# ------------------------------------------------------------

def reset_phases_to_solid(stream):


    # --------------------------------------------------------
    # LIQUID
    # --------------------------------------------------------

    stream.Phases[1].Properties.molarfraction = 0.0

    stream.Phases[1].Properties.massfraction = 0.0


    # --------------------------------------------------------
    # VAPOR
    # --------------------------------------------------------

    stream.Phases[2].Properties.molarfraction = 0.0

    stream.Phases[2].Properties.massfraction = 0.0


    # --------------------------------------------------------
    # LIQUID 1
    # --------------------------------------------------------

    stream.Phases[3].Properties.molarfraction = 0.0

    stream.Phases[3].Properties.massfraction = 0.0


    # --------------------------------------------------------
    # LIQUID 2
    # --------------------------------------------------------

    stream.Phases[4].Properties.molarfraction = 0.0

    stream.Phases[4].Properties.massfraction = 0.0


    # --------------------------------------------------------
    # LIQUID 3
    # --------------------------------------------------------

    stream.Phases[5].Properties.molarfraction = 0.0

    stream.Phases[5].Properties.massfraction = 0.0


    # --------------------------------------------------------
    # AQUEOUS
    # --------------------------------------------------------

    stream.Phases[6].Properties.molarfraction = 0.0

    stream.Phases[6].Properties.massfraction = 0.0


    # --------------------------------------------------------
    # SOLID
    # --------------------------------------------------------
    #
    # This is the critical part.
    #
    # The complete stream is assigned to the Solid phase.
    # --------------------------------------------------------

    stream.Phases[7].Properties.molarfraction = 1.0

    stream.Phases[7].Properties.massfraction = 1.0


# ------------------------------------------------------------
# CONFIGURE SOLID OUTLET STREAM
# ------------------------------------------------------------

def configure_solid_stream(
    stream,
    component_mass_flow,
    total_mass_flow,
    temp,
    pres
):


    # --------------------------------------------------------
    # DISABLE ELECTROLYTE STREAM BEHAVIOR
    # --------------------------------------------------------

    try:

        stream.IsElectrolyteStream = False

    except:

        pass


    # --------------------------------------------------------
    # OVERRIDE SINGLE-COMPOUND FLASH BEHAVIOR
    # --------------------------------------------------------
    #
    # This provides additional protection against an automatic
    # flash on the dry Li2CO3 outlet.
    # --------------------------------------------------------

    try:

        stream.OverrideSingleCompoundFlashBehavior = True

    except:

        pass


    # --------------------------------------------------------
    # FORCE SOLID PHASE
    # --------------------------------------------------------

    try:

        stream.ForcePhase = (
            Interfaces.Enums.ForcedPhase.Solid
        )

    except:

        pass


    # --------------------------------------------------------
    # OVERRIDE STREAM CALCULATION ROUTINE
    # --------------------------------------------------------

    try:

        stream.OverrideCalculationRoutine = True

    except:

        pass


    # --------------------------------------------------------
    # STREAM SPECIFICATION
    # --------------------------------------------------------

    try:

        stream.DefinedFlow = (
            Interfaces.Enums.FlowSpec.Mass
        )

    except:

        pass


    try:

        stream.SpecType = (
            Interfaces.Enums.StreamSpec.Temperature_and_Pressure
        )

    except:

        pass


    # --------------------------------------------------------
    # OVERALL STREAM CONDITIONS
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


    stream.Phases[0].Properties.molarfraction = 1.0

    stream.Phases[0].Properties.massfraction = 1.0


    # --------------------------------------------------------
    # CALCULATE TOTAL MOLAR FLOW
    # ------------------------------------------------------------

    total_molar_flow = 0.0


    for comp in stream.Phases[0].Compounds.Values:

        name = comp.Name


        component_flow_value = (
            component_mass_flow.get(
                name,
                0.0
            )
        )


        mw = safe_float(
            comp.ConstantProperties.Molar_Weight,
            0.0
        )


        if mw > 0.0:

            total_molar_flow += (
                component_flow_value /
                mw *
                1000.0
            )


    # --------------------------------------------------------
    # WRITE OVERALL MOLAR FLOW
    # --------------------------------------------------------

    stream.Phases[0].Properties.molarflow = (
        total_molar_flow
    )


    # --------------------------------------------------------
    # CALCULATE MOLE FRACTIONS
    # ------------------------------------------------------------

    mole_fraction_values = {}


    for comp in stream.Phases[0].Compounds.Values:

        name = comp.Name


        component_flow_value = (
            component_mass_flow.get(
                name,
                0.0
            )
        )


        mw = safe_float(
            comp.ConstantProperties.Molar_Weight,
            0.0
        )


        if (
            mw > 0.0
            and
            total_molar_flow > 0.0
        ):

            component_molar_flow = (
                component_flow_value /
                mw *
                1000.0
            )


            mole_fraction_values[name] = (
                component_molar_flow /
                total_molar_flow
            )

        else:

            mole_fraction_values[name] = 0.0


    # --------------------------------------------------------
    # WRITE OVERALL COMPONENT DATA
    # ------------------------------------------------------------

    for comp in stream.Phases[0].Compounds.Values:

        name = comp.Name


        component_flow_value = (
            component_mass_flow.get(
                name,
                0.0
            )
        )


        mw = safe_float(
            comp.ConstantProperties.Molar_Weight,
            0.0
        )


        comp.MassFlow = (
            component_flow_value
        )


        if mw > 0.0:

            comp.MolarFlow = (
                component_flow_value /
                mw *
                1000.0
            )

        else:

            comp.MolarFlow = 0.0


        if total_mass_flow > 0.0:

            comp.MassFraction = (
                component_flow_value /
                total_mass_flow
            )

        else:

            comp.MassFraction = 0.0


        comp.MoleFraction = (
            mole_fraction_values.get(
                name,
                0.0
            )
        )


    # --------------------------------------------------------
    # SET OVERALL MASS COMPOSITION
    # --------------------------------------------------------

    overall_mass_fraction_array = []


    for comp in stream.Phases[0].Compounds.Values:

        name = comp.Name


        component_flow_value = (
            component_mass_flow.get(
                name,
                0.0
            )
        )


        if total_mass_flow > 0.0:

            mass_fraction = (
                component_flow_value /
                total_mass_flow
            )

        else:

            mass_fraction = 0.0


        overall_mass_fraction_array.append(
            mass_fraction
        )


    try:

        stream.SetOverallMassComposition(
            Array[float](
                overall_mass_fraction_array
            )
        )

    except:

        pass


    # --------------------------------------------------------
    # RESET ALL PHASES
    # --------------------------------------------------------
    #
    # Do this AFTER writing the overall stream but BEFORE
    # writing the Solid phase.
    # --------------------------------------------------------

    reset_phases_to_solid(
        stream
    )


    # --------------------------------------------------------
    # SOLID PHASE
    # --------------------------------------------------------

    solid_phase = stream.Phases[7]


    # --------------------------------------------------------
    # SOLID PHASE FRACTIONS
    # --------------------------------------------------------
    #
    # These are essential.
    #
    # Without them DWSIM can still treat the stream as Liquid
    # even when Solid component values have been populated.
    # --------------------------------------------------------

    solid_phase.Properties.molarfraction = 1.0

    solid_phase.Properties.massfraction = 1.0


    # --------------------------------------------------------
    # SOLID PHASE FLOW
    # --------------------------------------------------------

    solid_phase.Properties.massflow = (
        total_mass_flow
    )


    solid_phase.Properties.molarflow = (
        total_molar_flow
    )


    solid_phase.Properties.temperature = (
        temp
    )


    solid_phase.Properties.pressure = (
        pres
    )


    # --------------------------------------------------------
    # SET SOLID PHASE COMPOSITION
    # --------------------------------------------------------
    #
    # DWSIM Solid phase index = 7.
    # ------------------------------------------------------------

    solid_mole_fraction_array = []


    for comp in stream.Phases[0].Compounds.Values:

        name = comp.Name


        solid_mole_fraction_array.append(
            mole_fraction_values.get(
                name,
                0.0
            )
        )


    try:

        stream.SetPhaseComposition1(
            Array[float](
                solid_mole_fraction_array
            ),
            7
        )

    except:

        pass


    # --------------------------------------------------------
    # RE-APPLY SOLID PHASE FRACTIONS
    # --------------------------------------------------------
    #
    # SetPhaseComposition1 changes the composition, but we
    # explicitly reassert the phase fraction afterwards.
    # --------------------------------------------------------

    solid_phase.Properties.molarfraction = 1.0

    solid_phase.Properties.massfraction = 1.0


    # --------------------------------------------------------
    # WRITE SOLID COMPONENT DATA
    # ------------------------------------------------------------

    for comp in solid_phase.Compounds.Values:

        name = comp.Name


        component_flow_value = (
            component_mass_flow.get(
                name,
                0.0
            )
        )


        mw = safe_float(
            comp.ConstantProperties.Molar_Weight,
            0.0
        )


        # ----------------------------------------------------
        # SOLID MASS FLOW
        # ----------------------------------------------------

        comp.MassFlow = (
            component_flow_value
        )


        # ----------------------------------------------------
        # SOLID MOLAR FLOW
        # ----------------------------------------------------

        if mw > 0.0:

            comp.MolarFlow = (
                component_flow_value /
                mw *
                1000.0
            )

        else:

            comp.MolarFlow = 0.0


        # ----------------------------------------------------
        # SOLID MASS FRACTION
        # ----------------------------------------------------

        if total_mass_flow > 0.0:

            comp.MassFraction = (
                component_flow_value /
                total_mass_flow
            )

        else:

            comp.MassFraction = 0.0


        # ----------------------------------------------------
        # SOLID MOLE FRACTION
        # ----------------------------------------------------

        comp.MoleFraction = (
            mole_fraction_values.get(
                name,
                0.0
            )
        )


# ------------------------------------------------------------
# CONFIGURE EXCESS_Li2CO3
# ------------------------------------------------------------

configure_solid_stream(
    excess_product,
    excess_component_mass_flow,
    excess_mass_flow,
    temperature,
    pressure
)


# ------------------------------------------------------------
# CONFIGURE Li2CO3_to_NMC622
# ------------------------------------------------------------

configure_solid_stream(
    nmc_product,
    nmc_component_mass_flow,
    nmc_mass_flow,
    temperature,
    pressure
)


# ------------------------------------------------------------
# ASSIGN CALCULATION OVERRIDES
# ------------------------------------------------------------

excess_product.OverrideCalculationRoutine = True

excess_product.CalculationRoutineOverride = (
    hold_excess_values
)


nmc_product.OverrideCalculationRoutine = True

nmc_product.CalculationRoutineOverride = (
    hold_nmc_values
)


# ------------------------------------------------------------
# FINAL PHASE PROTECTION
# ------------------------------------------------------------
#
# Re-assert the phase state after all outlet values have been
# written.
# ------------------------------------------------------------

reset_phases_to_solid(
    excess_product
)

reset_phases_to_solid(
    nmc_product
)


# ------------------------------------------------------------
# RE-ASSERT SOLID PHASE FLOWS
# ------------------------------------------------------------

excess_product.Phases[7].Properties.molarfraction = 1.0

excess_product.Phases[7].Properties.massfraction = 1.0

excess_product.Phases[7].Properties.massflow = (
    excess_mass_flow
)


nmc_product.Phases[7].Properties.molarfraction = 1.0

nmc_product.Phases[7].Properties.massfraction = 1.0

nmc_product.Phases[7].Properties.massflow = (
    nmc_mass_flow
)


# ------------------------------------------------------------
# MASS BALANCE
# ------------------------------------------------------------

mass_balance_error = (
    inlet_mass_flow
    -
    excess_mass_flow
    -
    nmc_mass_flow
)


# ------------------------------------------------------------
# Li2CO3 BALANCE
# ------------------------------------------------------------

li2co3_balance_error = (
    li2co3_in
    -
    li2co3_excess
    -
    li2co3_to_nmc
)


# ------------------------------------------------------------
# COMPONENT BALANCE
# ------------------------------------------------------------

component_balance_error = 0.0


for name in inlet_component_mass_flow:

    inlet_component = (
        inlet_component_mass_flow[name]
    )


    excess_component = (
        excess_component_mass_flow.get(
            name,
            0.0
        )
    )


    nmc_component = (
        nmc_component_mass_flow.get(
            name,
            0.0
        )
    )


    component_balance_error += abs(
        inlet_component
        -
        excess_component
        -
        nmc_component
    )


# ------------------------------------------------------------
# DIAGNOSTICS
# ------------------------------------------------------------

Flowsheet.WriteMessage(
    "------------------------------------------------------------"
)

Flowsheet.WriteMessage(
    "CUSTOM_Li2CO3_Dosing"
)

Flowsheet.WriteMessage(
    "------------------------------------------------------------"
)


# ------------------------------------------------------------
# INPUT
# ------------------------------------------------------------

Flowsheet.WriteMessage(
    "Input stream = Dry_Li2CO3"
)


Flowsheet.WriteMessage(
    "Input mass flow = "
    + str(inlet_mass_flow)
    + " kg/s"
)


Flowsheet.WriteMessage(
    "Input mass flow = "
    + str(inlet_mass_flow * 3600.0)
    + " kg/h"
)


# ------------------------------------------------------------
# SPLIT FRACTIONS
# ------------------------------------------------------------

Flowsheet.WriteMessage(
    "Excess_Li2CO3 split fraction = "
    + str(EXCESS_SPLIT)
)


Flowsheet.WriteMessage(
    "Li2CO3_to_NMC622 split fraction = "
    + str(NMC622_SPLIT)
)


# ------------------------------------------------------------
# OUTLET MASS FLOWS
# ------------------------------------------------------------

Flowsheet.WriteMessage(
    "Excess_Li2CO3 mass flow = "
    + str(excess_mass_flow)
    + " kg/s"
)


Flowsheet.WriteMessage(
    "Excess_Li2CO3 mass flow = "
    + str(excess_mass_flow * 3600.0)
    + " kg/h"
)


Flowsheet.WriteMessage(
    "Li2CO3_to_NMC622 mass flow = "
    + str(nmc_mass_flow)
    + " kg/s"
)


Flowsheet.WriteMessage(
    "Li2CO3_to_NMC622 mass flow = "
    + str(nmc_mass_flow * 3600.0)
    + " kg/h"
)


# ------------------------------------------------------------
# Li2CO3 DISTRIBUTION
# ------------------------------------------------------------

Flowsheet.WriteMessage(
    "------------------------------------------------------------"
)


Flowsheet.WriteMessage(
    "Li2CO3 inlet = "
    + str(li2co3_in * 3600.0)
    + " kg/h"
)


Flowsheet.WriteMessage(
    "Li2CO3 to Excess_Li2CO3 = "
    + str(li2co3_excess * 3600.0)
    + " kg/h"
)


Flowsheet.WriteMessage(
    "Li2CO3 to Li2CO3_to_NMC622 = "
    + str(li2co3_to_nmc * 3600.0)
    + " kg/h"
)


# ------------------------------------------------------------
# PHASE INFORMATION
# ------------------------------------------------------------

Flowsheet.WriteMessage(
    "------------------------------------------------------------"
)

Flowsheet.WriteMessage(
    "Excess_Li2CO3 phase = Solid"
)

Flowsheet.WriteMessage(
    "Li2CO3_to_NMC622 phase = Solid"
)

Flowsheet.WriteMessage(
    "Excess_Li2CO3 solid phase fraction = 1.0"
)

Flowsheet.WriteMessage(
    "Li2CO3_to_NMC622 solid phase fraction = 1.0"
)


# ------------------------------------------------------------
# MASS BALANCE
# ------------------------------------------------------------

Flowsheet.WriteMessage(
    "------------------------------------------------------------"
)

Flowsheet.WriteMessage(
    "Mass balance error = "
    + str(mass_balance_error)
    + " kg/s"
)


Flowsheet.WriteMessage(
    "Component balance error = "
    + str(component_balance_error)
    + " kg/s"
)


Flowsheet.WriteMessage(
    "Li2CO3 balance error = "
    + str(li2co3_balance_error)
    + " kg/s"
)


# ------------------------------------------------------------
# BALANCE CHECK
# ------------------------------------------------------------

if abs(mass_balance_error) < 1.0e-10:

    Flowsheet.WriteMessage(
        "Mass balance check: OK"
    )

else:

    Flowsheet.WriteMessage(
        "Mass balance check: WARNING"
    )


if abs(component_balance_error) < 1.0e-10:

    Flowsheet.WriteMessage(
        "Component balance check: OK"
    )

else:

    Flowsheet.WriteMessage(
        "Component balance check: WARNING"
    )


if abs(li2co3_balance_error) < 1.0e-10:

    Flowsheet.WriteMessage(
        "Li2CO3 balance check: OK"
    )

else:

    Flowsheet.WriteMessage(
        "Li2CO3 balance check: WARNING"
    )


# ------------------------------------------------------------
# END OF CUSTOM_Li2CO3_Dosing
# ------------------------------------------------------------