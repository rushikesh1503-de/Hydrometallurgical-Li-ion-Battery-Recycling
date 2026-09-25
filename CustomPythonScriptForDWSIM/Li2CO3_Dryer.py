# ------------------------------------------------------------
# CUSTOM_Li2CO3_Dryer
#
# Purpose:
#   Remove water from the washed Li2CO3 cake.
#
# Process:
#   Heated_Li2CO3_Cake
#          |
#          v
#   CUSTOM_Li2CO3_Dryer
#          |
#          +------> Li2CO3_Dryer_Offgas
#          |
#          v
#   Dry_Li2CO3
#
# Modeling basis:
#   - Drying removes water only.
#   - Li2CO3 remains in the product.
#   - Non-water components remain in the product.
#   - No chemical reaction occurs.
#
# DWSIM phase treatment:
#
#   Dry_Li2CO3
#       -> explicitly assigned to the SOLID phase.
#
#   Li2CO3_Dryer_Offgas
#       -> explicitly assigned to the VAPOR phase.
#
# This is necessary because the Li2CO3 cake is represented
# in DWSIM using an electrolyte property package, while the
# dry Li2CO3 product is conceptually a solid material.
#
# A normal electrolyte PH flash can therefore cause:
#
#       PH Flash [Electrolyte]:
#       Temperature did not converge
#
# The custom unit operation therefore:
#
#   1. Calculates all component mass flows explicitly.
#   2. Calculates all component molar flows explicitly.
#   3. Calculates overall composition explicitly.
#   4. Assigns the dry product to the Solid phase.
#   5. Assigns the dryer offgas to the Vapor phase.
#   6. Forces the corresponding phase.
#   7. Prevents DWSIM from re-flashing the outlet streams.
#
# ------------------------------------------------------------
#
# LITERATURE BASIS
#
# 1. Sharifian, S.; Nikfar, S.; Subasinghe, C.;
#    Iranmanesh, Z.; Rezaee, M.; Vahidi, E.
#
#    "Conventional vs. direct vs. electrochemical lithium
#    extraction: a holistic TEA-LCA of lithium carbonate
#    production from spodumene"
#
#    Green Chemistry, 2026, 28, 1144-1157.
#
#    DOI:
#    10.1039/D5GC04866D
#
#    Link:
#    https://doi.org/10.1039/D5GC04866D
#
#    The process description reports:
#
#       filter press
#       -> moist Li2CO3 cake
#       -> washing
#       -> drying at 100 degC
#       -> tray or rotary dryer
#
#    Therefore:
#
#       DRYER_TEMPERATURE = 373.15 K
#
#    is the literature-based base-case drying temperature.
#
#
# 2. Recovery of Lithium Carbonate from Dilute Li-Rich
#    Brine via Homogenous and Heterogeneous Precipitation
#
#    Industrial & Engineering Chemistry Research, 2022.
#
#    DOI:
#    10.1021/acs.iecr.2c01397
#
#    Link:
#    https://doi.org/10.1021/acs.iecr.2c01397
#
#    The experimental procedure reports that filtered
#    Li2CO3 crystals were dried at:
#
#       105 degC for 12 h.
#
#    This provides an independent experimental reference
#    supporting the selected approximately 100 degC drying
#    temperature.
#
# ------------------------------------------------------------
#
# IMPORTANT MODELING ASSUMPTIONS
#
# Dryer temperature:
#
#       100 degC
#
#       Literature-based.
#
#
# Feed cake moisture:
#
#       5 wt%
#
#       Inherited from the previous Li2CO3 separator/
#       washing model.
#
#       This is an engineering modeling assumption,
#       NOT a literature value.
#
#
# Target residual moisture:
#
#       0.1 wt%
#
#       Screening-level product specification used to
#       define "dry Li2CO3" in this model.
#
#       This should NOT be described as a universal
#       industrial Li2CO3 drying requirement.
#
#
# Li2CO3 recovery:
#
#       100%
#
#       Screening-level assumption.
#
#       No Li2CO3 loss is modeled during drying.
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


# ------------------------------------------------------------
# DRYER DESIGN BASIS
# ------------------------------------------------------------
#
# Literature-supported base-case dryer temperature:
#
#       100 degC
#
#       373.15 K
# ------------------------------------------------------------

DRYER_TEMPERATURE = 373.15


# ------------------------------------------------------------
# TARGET RESIDUAL MOISTURE
# ------------------------------------------------------------
#
# Screening-level modeling target:
#
#       0.1 wt% H2O
#
# Therefore:
#
#       0.001 mass fraction H2O
#
# This is a model specification, not a universal
# literature value.
# ------------------------------------------------------------

TARGET_MOISTURE = 0.001


# ------------------------------------------------------------
# Li2CO3 RECOVERY
# ------------------------------------------------------------
#
# Base-case assumption:
#
#       100% Li2CO3 recovery
#
# No Li2CO3 loss is modeled in the dryer.
# ------------------------------------------------------------

LI2CO3_RECOVERY = 1.0


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
    DRYER_TEMPERATURE
)


pressure = safe_float(
    feed_props.pressure,
    101325.0
)


# ------------------------------------------------------------
# CHECK INPUT FLOW
# ------------------------------------------------------------

if inlet_mass_flow <= 0.0:

    raise Exception(
        "CUSTOM_Li2CO3_Dryer: "
        "Input mass flow is zero."
    )


# ------------------------------------------------------------
# CALCULATE COMPONENT MASS FLOWS
# ------------------------------------------------------------
#
# For each component:
#
#       m_i = w_i * m_total
#
# where:
#
#       m_i     = component mass flow [kg/s]
#       w_i     = component mass fraction [-]
#       m_total = total stream mass flow [kg/s]
# ------------------------------------------------------------

component_mass_flow = {}


for comp in feed.Phases[0].Compounds.Values:

    name = comp.Name


    mass_fraction = safe_float(
        comp.MassFraction,
        0.0
    )


    component_mass_flow[name] = (
        mass_fraction *
        inlet_mass_flow
    )


# ------------------------------------------------------------
# IDENTIFY WATER
# ------------------------------------------------------------

water_in = component_mass_flow.get(
    "Water",
    0.0
)


# ------------------------------------------------------------
# IDENTIFY Li2CO3
# ------------------------------------------------------------

li2co3_in = component_mass_flow.get(
    "Lithium Carbonate",
    0.0
)


# ------------------------------------------------------------
# CHECK Li2CO3
# ------------------------------------------------------------

if li2co3_in <= 0.0:

    raise Exception(
        "CUSTOM_Li2CO3_Dryer: "
        "Lithium Carbonate mass flow is zero."
    )


# ------------------------------------------------------------
# Li2CO3 RECOVERY
# ------------------------------------------------------------
#
# Formula:
#
#       m_Li2CO3,out =
#       m_Li2CO3,in × recovery
#
# Base case:
#
#       recovery = 1.0
# ------------------------------------------------------------

li2co3_product = (
    li2co3_in *
    LI2CO3_RECOVERY
)


# ------------------------------------------------------------
# CALCULATE OTHER NON-WATER MATERIAL
# ------------------------------------------------------------
#
# All components other than water are retained in the
# dry product.
#
# Therefore:
#
#       m_nonwater =
#       m_total - m_water
#
# Li2CO3 is included within this quantity.
# ------------------------------------------------------------

nonwater_mass = (
    inlet_mass_flow -
    water_in
)


# ------------------------------------------------------------
# CALCULATE OTHER NON-WATER COMPONENTS
#
# This value represents all non-water material other than
# Li2CO3.
# ------------------------------------------------------------

other_nonwater_mass = (
    nonwater_mass -
    li2co3_in
)


if other_nonwater_mass < 0.0:

    other_nonwater_mass = 0.0


# ------------------------------------------------------------
# DRY SOLID MASS
# ------------------------------------------------------------
#
# The dry product contains:
#
#       Li2CO3
#       +
#       other non-water material
#
# Therefore:
#
#       m_dry_solid =
#       m_Li2CO3,out
#       +
#       m_other_nonwater
# ------------------------------------------------------------

dry_solid_mass = (
    li2co3_product +
    other_nonwater_mass
)


# ------------------------------------------------------------
# CALCULATE FINAL PRODUCT MASS
# ------------------------------------------------------------
#
# Target moisture definition:
#
#       w_H2O =
#       m_H2O,out / m_product
#
# And:
#
#       m_product =
#       m_dry_solid + m_H2O,out
#
# Therefore:
#
#       m_product =
#       m_dry_solid /
#       (1 - w_H2O)
# ------------------------------------------------------------

dry_mass_flow = (
    dry_solid_mass /
    (1.0 - TARGET_MOISTURE)
)


# ------------------------------------------------------------
# CALCULATE RESIDUAL WATER
# ------------------------------------------------------------
#
#       m_H2O,out =
#       m_product × target moisture
# ------------------------------------------------------------

water_remaining = (
    dry_mass_flow *
    TARGET_MOISTURE
)


# ------------------------------------------------------------
# CALCULATE WATER REMOVED
# ------------------------------------------------------------
#
#       m_H2O,removed =
#       m_H2O,in - m_H2O,out
# ------------------------------------------------------------

water_removed = (
    water_in -
    water_remaining
)


if water_removed < 0.0:

    water_removed = 0.0


# ------------------------------------------------------------
# DRY PRODUCT COMPONENT FLOWS
# ------------------------------------------------------------
#
# All non-water components remain in the product.
#
# Only the water flow is reduced.
# ------------------------------------------------------------

dry_component_flow = dict(
    component_mass_flow
)


dry_component_flow["Water"] = (
    water_remaining
)


dry_component_flow[
    "Lithium Carbonate"
] = li2co3_product


# ------------------------------------------------------------
# FINAL DRY PRODUCT MASS FLOW
# ------------------------------------------------------------

dry_mass_flow = sum(
    dry_component_flow.values()
)


# ------------------------------------------------------------
# DRYER OFFGAS COMPONENT FLOWS
# ------------------------------------------------------------
#
# Only removed water is sent to the dryer offgas.
#
# No Li2CO3 is assumed to enter the offgas.
# ------------------------------------------------------------

offgas_component_flow = {}


for comp in feed.Phases[0].Compounds.Values:

    name = comp.Name

    offgas_component_flow[name] = 0.0


offgas_component_flow["Water"] = (
    water_removed
)


offgas_mass_flow = (
    water_removed
)


# ------------------------------------------------------------
# WRITE STREAM VALUES
# ------------------------------------------------------------
#
# This function writes both:
#
#       1. Overall mixture values
#       2. The explicitly selected physical phase
#
# The normal DWSIM electrolyte flash is NOT used to determine
# the outlet composition.
# ------------------------------------------------------------

def write_stream(
    stream,
    component_flow,
    total_mass_flow,
    temp,
    pres,
    forced_phase
):


    # --------------------------------------------------------
    # SELECT PHASE
    # --------------------------------------------------------
    #
    # DWSIM phase indices:
    #
    #       Vapor = 2
    #       Solid = 7
    #
    # The phase is selected explicitly rather than allowing
    # the electrolyte PH flash to determine it.
    # --------------------------------------------------------

    if forced_phase == "Solid":

        phase = stream.Solid

    else:

        phase = stream.Vapor


    # --------------------------------------------------------
    # PREVENT ELECTROLYTE FLASHING
    # --------------------------------------------------------
    #
    # These outlet streams are being defined explicitly by
    # the custom dryer.
    #
    # They should therefore not be sent back through the
    # electrolyte PH flash.
    # --------------------------------------------------------

    try:

        stream.IsElectrolyteStream = False

    except:

        pass


    # --------------------------------------------------------
    # FORCE THE PHYSICAL PHASE
    # --------------------------------------------------------
    #
    # DWSIM provides ForcePhase specifically to override the
    # flash-calculated phase.
    # --------------------------------------------------------

    if forced_phase == "Solid":

        stream.ForcePhase = (
            Interfaces.Enums.ForcedPhase.Solid
        )

    else:

        stream.ForcePhase = (
            Interfaces.Enums.ForcedPhase.Vapor
        )


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
    # For every component:
    #
    #       n_i = m_i / MW_i
    #
    # where:
    #
    #       m_i  = kg/s
    #       MW_i = kg/kmol
    #
    # Result:
    #
    #       kmol/s
    #
    # Conversion:
    #
    #       mol/s = kmol/s × 1000
    # ------------------------------------------------------------

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
                flow /
                mw
            )


    total_molar_flow = (
        total_kmol_per_s *
        1000.0
    )


    # --------------------------------------------------------
    # WRITE OVERALL MOLAR FLOW
    # --------------------------------------------------------

    stream.Phases[0].Properties.molarflow = (
        total_molar_flow
    )


    # --------------------------------------------------------
    # CALCULATE OVERALL MOLE FRACTIONS
    # --------------------------------------------------------

    overall_mole_fraction = {}


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
                    flow /
                    mw *
                    1000.0
                )


                overall_mole_fraction[name] = (
                    component_molar_flow /
                    total_molar_flow
                )

            else:

                overall_mole_fraction[name] = 0.0

    else:

        for comp in stream.Phases[0].Compounds.Values:

            overall_mole_fraction[
                comp.Name
            ] = 0.0


    # --------------------------------------------------------
    # WRITE OVERALL COMPONENT DATA
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
                flow /
                mw *
                1000.0
            )

        else:

            comp.MolarFlow = 0.0


        # ----------------------------------------------------
        # COMPONENT MASS FRACTION
        # ----------------------------------------------------

        if total_mass_flow > 0.0:

            comp.MassFraction = (
                flow /
                total_mass_flow
            )

        else:

            comp.MassFraction = 0.0


        # ----------------------------------------------------
        # COMPONENT MOLE FRACTION
        # ----------------------------------------------------

        comp.MoleFraction = (
            overall_mole_fraction.get(
                name,
                0.0
            )
        )


    # --------------------------------------------------------
    # SET OVERALL MASS COMPOSITION
    # --------------------------------------------------------
    #
    # SetOverallMassComposition expects a .NET Array rather
    # than a normal Python list in the DWSIM Python.NET
    # environment.
    # ------------------------------------------------------------

    overall_mass_fraction = []


    for comp in stream.Phases[0].Compounds.Values:

        name = comp.Name


        flow = component_flow.get(
            name,
            0.0
        )


        if total_mass_flow > 0.0:

            fraction = (
                flow /
                total_mass_flow
            )

        else:

            fraction = 0.0


        overall_mass_fraction.append(
            fraction
        )


    try:

        stream.SetOverallMassComposition(
            Array[float](
                overall_mass_fraction
            )
        )

    except:

        pass


    # --------------------------------------------------------
    # PHASE PROPERTIES
    # --------------------------------------------------------
    #
    # The selected phase receives the complete outlet flow.
    #
    # For the dry Li2CO3 product:
    #
    #       Solid phase = complete product
    #
    # For the dryer offgas:
    #
    #       Vapor phase = complete offgas
    # ------------------------------------------------------------

    phase.Properties.massflow = (
        total_mass_flow
    )


    phase.Properties.molarflow = (
        total_molar_flow
    )


    phase.Properties.temperature = (
        temp
    )


    phase.Properties.pressure = (
        pres
    )


    # --------------------------------------------------------
    # PHASE COMPOSITION
    # --------------------------------------------------------
    #
    # SetPhaseComposition1 requires a molar-composition array
    # and the DWSIM phase index.
    #
    # Solid phase:
    #
    #       phase index = 7
    #
    # Vapor phase:
    #
    #       phase index = 2
    # ------------------------------------------------------------

    phase_mole_fraction = []


    for comp in stream.Phases[0].Compounds.Values:

        name = comp.Name


        phase_mole_fraction.append(
            overall_mole_fraction.get(
                name,
                0.0
            )
        )


    if forced_phase == "Solid":

        phase_index = 7

    else:

        phase_index = 2


    try:

        stream.SetPhaseComposition1(
            Array[float](
                phase_mole_fraction
            ),
            phase_index
        )

    except:

        pass


    # --------------------------------------------------------
    # WRITE COMPONENT DATA INTO THE SELECTED PHASE
    # --------------------------------------------------------
    #
    # This is the additional step that makes the phase columns
    # visible in the DWSIM stream report.
    # ------------------------------------------------------------

    for comp in phase.Compounds.Values:

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
        # PHASE COMPONENT MASS FLOW
        # ----------------------------------------------------

        comp.MassFlow = flow


        # ----------------------------------------------------
        # PHASE COMPONENT MOLAR FLOW
        # ----------------------------------------------------

        if mw > 0.0:

            comp.MolarFlow = (
                flow /
                mw *
                1000.0
            )

        else:

            comp.MolarFlow = 0.0


        # ----------------------------------------------------
        # PHASE COMPONENT MASS FRACTION
        # ----------------------------------------------------

        if total_mass_flow > 0.0:

            comp.MassFraction = (
                flow /
                total_mass_flow
            )

        else:

            comp.MassFraction = 0.0


        # ----------------------------------------------------
        # PHASE COMPONENT MOLE FRACTION
        # ----------------------------------------------------

        comp.MoleFraction = (
            overall_mole_fraction.get(
                name,
                0.0
            )
        )


# ------------------------------------------------------------
# WRITE DRY Li2CO3 PRODUCT
# ------------------------------------------------------------
#
# The dry Li2CO3 product is explicitly assigned to the
# Solid phase.
#
# IMPORTANT:
#
# The remaining 0.1 wt% water is retained in this stream
# because it represents residual product moisture.
#
# The stream is therefore a pseudo-solid product stream
# containing dry Li2CO3 plus residual moisture.
#
# This does NOT mean that the residual water is physically
# solid at 100 degC.
# ------------------------------------------------------------

write_stream(
    dry_product,
    dry_component_flow,
    dry_mass_flow,
    DRYER_TEMPERATURE,
    pressure,
    "Solid"
)


# ------------------------------------------------------------
# WRITE DRYER OFFGAS
# ------------------------------------------------------------
#
# The removed water is represented as vapor at the dryer
# temperature and atmospheric pressure.
#
# At:
#
#       100 degC
#       101325 Pa
#
# this is the physically appropriate phase representation
# for the water removed by the dryer.
# ------------------------------------------------------------

write_stream(
    offgas,
    offgas_component_flow,
    offgas_mass_flow,
    DRYER_TEMPERATURE,
    pressure,
    "Vapor"
)


# ------------------------------------------------------------
# PREVENT DWSIM FROM RE-FLASHING THE DRY PRODUCT
# ------------------------------------------------------------
#
# The dry product has already been explicitly calculated
# above.
#
# The normal DWSIM electrolyte PH flash must therefore not
# overwrite these values.
#
# Reference:
#
# DWSIM Model Customization:
#
# https://dwsim.org/wiki/index.php?title=Model_Customization
# ------------------------------------------------------------

def hold_dry_product_values():

    pass


dry_product.OverrideCalculationRoutine = True


dry_product.CalculationRoutineOverride = (
    hold_dry_product_values
)


# ------------------------------------------------------------
# PREVENT DWSIM FROM RE-FLASHING THE OFFGAS
# ------------------------------------------------------------
#
# The offgas has also been explicitly calculated.
#
# It is represented as water vapor and is protected from
# the electrolyte PH flash.
# ------------------------------------------------------------

def hold_offgas_values():

    pass


offgas.OverrideCalculationRoutine = True


offgas.CalculationRoutineOverride = (
    hold_offgas_values
)


# ------------------------------------------------------------
# MASS BALANCE
# ------------------------------------------------------------
#
#       Error =
#
#       inlet
#       -
#       dry product
#       -
#       offgas
#
# The expected value is approximately zero.
# ------------------------------------------------------------

mass_balance_error = (
    inlet_mass_flow
    -
    dry_mass_flow
    -
    offgas_mass_flow
)


# ------------------------------------------------------------
# WATER BALANCE
# ------------------------------------------------------------
#
#       Error =
#
#       water in
#       -
#       water remaining
#       -
#       water removed
#
# The expected value is approximately zero.
# ------------------------------------------------------------

water_balance_error = (
    water_in
    -
    water_remaining
    -
    water_removed
)


# ------------------------------------------------------------
# FINAL PRODUCT MOISTURE
# ------------------------------------------------------------

if dry_mass_flow > 0.0:

    final_moisture = (
        water_remaining /
        dry_mass_flow
    )

else:

    final_moisture = 0.0


# ------------------------------------------------------------
# DIAGNOSTICS
# ------------------------------------------------------------

Flowsheet.WriteMessage(
    "------------------------------------------------------------"
)

Flowsheet.WriteMessage(
    "CUSTOM_Li2CO3_Dryer"
)

Flowsheet.WriteMessage(
    "------------------------------------------------------------"
)


# ------------------------------------------------------------
# LITERATURE INFORMATION
# ------------------------------------------------------------

Flowsheet.WriteMessage(
    "Literature base case:"
)

Flowsheet.WriteMessage(
    "Sharifian et al., Green Chemistry, 2026"
)

Flowsheet.WriteMessage(
    "DOI: 10.1039/D5GC04866D"
)

Flowsheet.WriteMessage(
    "https://doi.org/10.1039/D5GC04866D"
)

Flowsheet.WriteMessage(
    "Reported drying temperature: 100 degC"
)


Flowsheet.WriteMessage(
    "Independent experimental reference:"
)

Flowsheet.WriteMessage(
    "Industrial & Engineering Chemistry Research, 2022"
)

Flowsheet.WriteMessage(
    "DOI: 10.1021/acs.iecr.2c01397"
)

Flowsheet.WriteMessage(
    "https://doi.org/10.1021/acs.iecr.2c01397"
)

Flowsheet.WriteMessage(
    "Reported drying condition: 105 degC, 12 h"
)


# ------------------------------------------------------------
# PROCESS CONDITIONS
# ------------------------------------------------------------

Flowsheet.WriteMessage(
    "------------------------------------------------------------"
)

Flowsheet.WriteMessage(
    "Inlet temperature = "
    + str(temperature)
    + " K"
)

Flowsheet.WriteMessage(
    "Dryer temperature = "
    + str(DRYER_TEMPERATURE)
    + " K"
)

Flowsheet.WriteMessage(
    "Pressure = "
    + str(pressure)
    + " Pa"
)


# ------------------------------------------------------------
# MASS FLOWS
# ------------------------------------------------------------

Flowsheet.WriteMessage(
    "Inlet mass flow = "
    + str(inlet_mass_flow)
    + " kg/s"
)

Flowsheet.WriteMessage(
    "Inlet mass flow = "
    + str(inlet_mass_flow * 3600.0)
    + " kg/h"
)


Flowsheet.WriteMessage(
    "Li2CO3 inlet = "
    + str(li2co3_in)
    + " kg/s"
)

Flowsheet.WriteMessage(
    "Li2CO3 inlet = "
    + str(li2co3_in * 3600.0)
    + " kg/h"
)


Flowsheet.WriteMessage(
    "Water inlet = "
    + str(water_in)
    + " kg/s"
)

Flowsheet.WriteMessage(
    "Water inlet = "
    + str(water_in * 3600.0)
    + " kg/h"
)


Flowsheet.WriteMessage(
    "Dry solid mass = "
    + str(dry_solid_mass)
    + " kg/s"
)

Flowsheet.WriteMessage(
    "Dry solid mass = "
    + str(dry_solid_mass * 3600.0)
    + " kg/h"
)


Flowsheet.WriteMessage(
    "Dry product mass flow = "
    + str(dry_mass_flow)
    + " kg/s"
)

Flowsheet.WriteMessage(
    "Dry product mass flow = "
    + str(dry_mass_flow * 3600.0)
    + " kg/h"
)


Flowsheet.WriteMessage(
    "Water remaining in product = "
    + str(water_remaining)
    + " kg/s"
)

Flowsheet.WriteMessage(
    "Water remaining in product = "
    + str(water_remaining * 3600.0)
    + " kg/h"
)


Flowsheet.WriteMessage(
    "Water removed = "
    + str(water_removed)
    + " kg/s"
)

Flowsheet.WriteMessage(
    "Water removed = "
    + str(water_removed * 3600.0)
    + " kg/h"
)


Flowsheet.WriteMessage(
    "Dryer offgas mass flow = "
    + str(offgas_mass_flow)
    + " kg/s"
)

Flowsheet.WriteMessage(
    "Dryer offgas mass flow = "
    + str(offgas_mass_flow * 3600.0)
    + " kg/h"
)


# ------------------------------------------------------------
# PRODUCT MOISTURE
# ------------------------------------------------------------

Flowsheet.WriteMessage(
    "Target product moisture = "
    + str(TARGET_MOISTURE * 100.0)
    + " wt%"
)

Flowsheet.WriteMessage(
    "Calculated product moisture = "
    + str(final_moisture * 100.0)
    + " wt%"
)


# ------------------------------------------------------------
# PHASE ASSIGNMENT
# ------------------------------------------------------------

Flowsheet.WriteMessage(
    "Dry_Li2CO3 phase = Solid"
)

Flowsheet.WriteMessage(
    "Li2CO3_Dryer_Offgas phase = Vapor"
)


# ------------------------------------------------------------
# BALANCE DIAGNOSTICS
# ------------------------------------------------------------

Flowsheet.WriteMessage(
    "Mass balance error = "
    + str(mass_balance_error)
    + " kg/s"
)

Flowsheet.WriteMessage(
    "Water balance error = "
    + str(water_balance_error)
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


if abs(water_balance_error) < 1.0e-10:

    Flowsheet.WriteMessage(
        "Water balance check: OK"
    )

else:

    Flowsheet.WriteMessage(
        "Water balance check: WARNING"
    )
