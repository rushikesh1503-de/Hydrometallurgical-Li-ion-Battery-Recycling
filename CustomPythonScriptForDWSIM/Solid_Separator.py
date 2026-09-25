# --------------------------------------------------------
#
# CUSTOM_Solid_Separator
#
# Purpose:
# Split Leach_Slurry into:
#
#     Leach_Liquid
#     Leach_Solids
#
# Solid components:
#     Graphite
#     BM_Inert_Lumped
#
# Base-case assumptions:
#
#     SOLIDS_RECOVERY = 1.00
#     LIQUID_RECOVERY = 1.00
#
# --------------------------------------------------------


import clr

clr.AddReference("DWSIM.Interfaces")

from DWSIM import Interfaces


# --------------------------------------------------------
# PARAMETERS
# --------------------------------------------------------

SOLIDS_RECOVERY = 1.00

LIQUID_RECOVERY = 1.00


SOLID_COMPONENTS = [
    "Graphite",
    "BM_Inert_Lumped"
]


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
# CUSTOM UO PORTS
#
# ims1 = Leach_Slurry
# oms1 = Leach_Liquid
# oms2 = Leach_Solids
# --------------------------------------------------------

feed = ims1

liquid_out = oms1

solid_out = oms2


# --------------------------------------------------------
# CHECK INPUT
# --------------------------------------------------------

if feed is None:

    Flowsheet.WriteMessage(
        "CUSTOM_Solid_Separator ERROR: "
        + "Input stream ims1 is not connected."
    )

else:

    # ----------------------------------------------------
    # READ FEED CONDITIONS
    # ----------------------------------------------------

    feed_props = feed.Phases[0].Properties


    inlet_mass_flow = safe_float(
        feed_props.massflow,
        0.0
    )


    temperature = safe_float(
        feed_props.temperature,
        323.15
    )


    pressure = safe_float(
        feed_props.pressure,
        101325.0
    )


    # ----------------------------------------------------
    # COMPONENT MASS FLOWS
    # ----------------------------------------------------

    component_mass_flow = {}


    for comp in feed.Phases[0].Compounds.Values:

        name = comp.Name

        mass_fraction = safe_float(
            comp.MassFraction,
            0.0
        )


        component_mass_flow[name] = (
            mass_fraction
            * inlet_mass_flow
        )


    # ----------------------------------------------------
    # INITIALIZE OUTLET FLOWS
    # ----------------------------------------------------

    liquid_component_mass_flow = {}

    solid_component_mass_flow = {}


    # ----------------------------------------------------
    # SPLIT COMPONENTS
    # ----------------------------------------------------

    for comp in feed.Phases[0].Compounds.Values:

        name = comp.Name


        inlet_component_flow = (
            component_mass_flow.get(
                name,
                0.0
            )
        )


        # ----------------------------------------------
        # SOLID COMPONENTS
        # ----------------------------------------------

        if name in SOLID_COMPONENTS:

            solid_flow = (
                inlet_component_flow
                * SOLIDS_RECOVERY
            )


            liquid_flow = (
                inlet_component_flow
                * (1.0 - SOLIDS_RECOVERY)
            )


        # ----------------------------------------------
        # ALL OTHER COMPONENTS
        # ----------------------------------------------

        else:

            liquid_flow = (
                inlet_component_flow
                * LIQUID_RECOVERY
            )


            solid_flow = (
                inlet_component_flow
                * (1.0 - LIQUID_RECOVERY)
            )


        solid_component_mass_flow[name] = solid_flow

        liquid_component_mass_flow[name] = liquid_flow


    # ----------------------------------------------------
    # TOTAL OUTLET MASS FLOWS
    # ----------------------------------------------------

    liquid_mass_flow = 0.0

    solid_mass_flow = 0.0


    for value in liquid_component_mass_flow.values():

        liquid_mass_flow += value


    for value in solid_component_mass_flow.values():

        solid_mass_flow += value


    # ----------------------------------------------------
    # MOLAR FLOW FUNCTION
    #
    # DWSIM molecular weight = kg/kmol
    #
    # kg/s
    # -------- = kmol/s
    # kg/kmol
    #
    # ×1000 = mol/s
    # ----------------------------------------------------

    def calculate_molar_flow(component_flows):

        molar_flow_kmol_s = 0.0


        for comp in feed.Phases[0].Compounds.Values:

            name = comp.Name


            component_flow = (
                component_flows.get(
                    name,
                    0.0
                )
            )


            mw = safe_float(
                comp.ConstantProperties.Molar_Weight,
                0.0
            )


            if mw > 0.0:

                molar_flow_kmol_s += (
                    component_flow / mw
                )


        return molar_flow_kmol_s * 1000.0


    # ----------------------------------------------------
    # OUTLET MOLAR FLOWS
    # ----------------------------------------------------

    liquid_molar_flow = calculate_molar_flow(
        liquid_component_mass_flow
    )


    solid_molar_flow = calculate_molar_flow(
        solid_component_mass_flow
    )


    # ----------------------------------------------------
    # LEACH_LIQUID
    # ----------------------------------------------------

    if liquid_out is not None:

        # ------------------------------------------------
        # CLEAR OLD VALUES
        # ------------------------------------------------

        liquid_out.Clear()

        liquid_out.ClearAllProps()


        # ------------------------------------------------
        # BASIC PROPERTIES
        # ------------------------------------------------

        liquid_out.Phases[0].Properties.massflow = (
            liquid_mass_flow
        )


        liquid_out.Phases[0].Properties.molarflow = (
            liquid_molar_flow
        )


        liquid_out.Phases[0].Properties.temperature = (
            temperature
        )


        liquid_out.Phases[0].Properties.pressure = (
            pressure
        )


        # ------------------------------------------------
        # FLOW SPECIFICATION
        # ------------------------------------------------

        liquid_out.DefinedFlow = (
            Interfaces.Enums.FlowSpec.Mass
        )


        liquid_out.SpecType = (
            Interfaces.Enums.StreamSpec.Temperature_and_Pressure
        )


        # ------------------------------------------------
        # MASS FRACTIONS
        # ------------------------------------------------

        for comp in liquid_out.Phases[0].Compounds.Values:

            name = comp.Name


            component_flow = (
                liquid_component_mass_flow.get(
                    name,
                    0.0
                )
            )


            if liquid_mass_flow > 0.0:

                comp.MassFraction = (
                    component_flow
                    / liquid_mass_flow
                )

            else:

                comp.MassFraction = 0.0


        # ------------------------------------------------
        # MOLE FRACTIONS
        # ------------------------------------------------

        liquid_molar_sum = 0.0


        for comp in liquid_out.Phases[0].Compounds.Values:

            name = comp.Name


            component_flow = (
                liquid_component_mass_flow.get(
                    name,
                    0.0
                )
            )


            mw = safe_float(
                comp.ConstantProperties.Molar_Weight,
                0.0
            )


            if mw > 0.0:

                liquid_molar_sum += (
                    component_flow / mw
                )


        for comp in liquid_out.Phases[0].Compounds.Values:

            name = comp.Name


            component_flow = (
                liquid_component_mass_flow.get(
                    name,
                    0.0
                )
            )


            mw = safe_float(
                comp.ConstantProperties.Molar_Weight,
                0.0
            )


            if (
                liquid_molar_sum > 0.0
                and mw > 0.0
            ):

                comp.MoleFraction = (
                    (component_flow / mw)
                    / liquid_molar_sum
                )

            else:

                comp.MoleFraction = 0.0


    else:

        Flowsheet.WriteMessage(
            "CUSTOM_Solid_Separator ERROR: "
            + "Output oms1 is not connected."
        )


    # ----------------------------------------------------
    # LEACH_SOLIDS
    # ----------------------------------------------------

    if solid_out is not None:

        # ------------------------------------------------
        # CLEAR OLD VALUES
        # ------------------------------------------------

        solid_out.Clear()

        solid_out.ClearAllProps()


        # ------------------------------------------------
        # BASIC PROPERTIES
        # ------------------------------------------------

        solid_out.Phases[0].Properties.massflow = (
            solid_mass_flow
        )


        solid_out.Phases[0].Properties.molarflow = (
            solid_molar_flow
        )


        solid_out.Phases[0].Properties.temperature = (
            temperature
        )


        solid_out.Phases[0].Properties.pressure = (
            pressure
        )


        # ------------------------------------------------
        # FLOW SPECIFICATION
        # ------------------------------------------------

        solid_out.DefinedFlow = (
            Interfaces.Enums.FlowSpec.Mass
        )


        solid_out.SpecType = (
            Interfaces.Enums.StreamSpec.Temperature_and_Pressure
        )


        # ------------------------------------------------
        # MASS FRACTIONS
        # ------------------------------------------------

        for comp in solid_out.Phases[0].Compounds.Values:

            name = comp.Name


            component_flow = (
                solid_component_mass_flow.get(
                    name,
                    0.0
                )
            )


            if solid_mass_flow > 0.0:

                comp.MassFraction = (
                    component_flow
                    / solid_mass_flow
                )

            else:

                comp.MassFraction = 0.0


        # ------------------------------------------------
        # MOLE FRACTIONS
        # ------------------------------------------------

        solid_molar_sum = 0.0


        for comp in solid_out.Phases[0].Compounds.Values:

            name = comp.Name


            component_flow = (
                solid_component_mass_flow.get(
                    name,
                    0.0
                )
            )


            mw = safe_float(
                comp.ConstantProperties.Molar_Weight,
                0.0
            )


            if mw > 0.0:

                solid_molar_sum += (
                    component_flow / mw
                )


        for comp in solid_out.Phases[0].Compounds.Values:

            name = comp.Name


            component_flow = (
                solid_component_mass_flow.get(
                    name,
                    0.0
                )
            )


            mw = safe_float(
                comp.ConstantProperties.Molar_Weight,
                0.0
            )


            if (
                solid_molar_sum > 0.0
                and mw > 0.0
            ):

                comp.MoleFraction = (
                    (component_flow / mw)
                    / solid_molar_sum
                )

            else:

                comp.MoleFraction = 0.0


    else:

        Flowsheet.WriteMessage(
            "CUSTOM_Solid_Separator ERROR: "
            + "Output oms2 is not connected."
        )


    # ----------------------------------------------------
    # MASS BALANCE
    # ----------------------------------------------------

    outlet_mass_flow = (
        liquid_mass_flow
        + solid_mass_flow
    )


    mass_balance_error = (
        inlet_mass_flow
        - outlet_mass_flow
    )


    # ----------------------------------------------------
    # DIAGNOSTIC MESSAGES
    # ----------------------------------------------------

    Flowsheet.WriteMessage(
        "CUSTOM_Solid_Separator: calculation completed."
    )


    Flowsheet.WriteMessage(
        "Inlet mass flow = "
        + str(inlet_mass_flow)
        + " kg/s"
    )


    Flowsheet.WriteMessage(
        "Leach_Liquid mass flow = "
        + str(liquid_mass_flow)
        + " kg/s"
    )


    Flowsheet.WriteMessage(
        "Leach_Solids mass flow = "
        + str(solid_mass_flow)
        + " kg/s"
    )


    Flowsheet.WriteMessage(
        "Outlet total mass flow = "
        + str(outlet_mass_flow)
        + " kg/s"
    )


    Flowsheet.WriteMessage(
        "Mass balance error = "
        + str(mass_balance_error)
        + " kg/s"
    )


    Flowsheet.WriteMessage(
        "Solid recovery = "
        + str(SOLIDS_RECOVERY * 100.0)
        + " %"
    )


    Flowsheet.WriteMessage(
        "Liquid recovery = "
        + str(LIQUID_RECOVERY * 100.0)
        + " %"
    )