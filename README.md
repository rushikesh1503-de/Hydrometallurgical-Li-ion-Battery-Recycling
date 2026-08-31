# Hydrometallurgical Li ion Battery Recycling

## Process Simulation and Life Cycle Assessment

A process engineering project investigating the hydrometallurgical recycling of NMC622 lithium ion battery black mass using process simulation, mass and energy balances, and life cycle assessment.

The project combines DWSIM process simulation with OpenLCA and Python based data analysis to evaluate material recovery, process requirements, environmental impacts, and the sensitivity of the recycling process to key operating parameters.

## Project Objectives

The project aims to:

- Develop a representative process model for hydrometallurgical recycling of NMC622 black mass
- Quantify material and energy flows through the recycling process
- Model lithium, nickel, manganese, and cobalt recovery
- Evaluate the environmental performance of the recycling route using life cycle assessment
- Compare recycled material production with relevant virgin material production
- Identify the influence of recovery efficiency, reagent consumption, energy demand, and transport on environmental impacts
- Develop Python based analysis and visualization tools for sensitivity analysis and process interpretation

## Process Route

The initial process route considered in the project is:

```text
Battery Black Mass
        |
        v
Feed Preparation
        |
        v
Acid Leaching
        |
        v
Solid / Liquid Separation
        |
        v
Impurity Removal
        |
        v
Ni / Mn / Co Recovery
        |
        v
Lithium Recovery
        |
        v
Recovered Products
