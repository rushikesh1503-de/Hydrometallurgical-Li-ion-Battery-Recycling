# Hydrometallurgical NMC622 Li ion Battery Recycling
---

## 1. Introduction and Industrial Relevance

Lithium ion batteries are a major technology for electric vehicles, portable electronics and stationary energy storage. Global electric car sales exceeded 17 million units in 2024, representing more than 20% of global car sales. China accounted for almost two thirds of global electric car sales, while Europe remained an important market with an electric car sales share of around 20% [1].

The rapid growth of battery deployment is increasing the importance of end of life battery management, recovery of critical raw materials and development of recycling capacity. Hydrometallurgical recycling is particularly relevant because it can recover lithium, nickel, manganese and cobalt from cathode materials through aqueous leaching and downstream purification or precipitation.

This project focuses on the process engineering and environmental assessment of a defined hydrometallurgical route for NMC622 battery material. The objective is not to model an entire commercial battery recycling plant, but to develop a transparent process screening model that connects process simulation, life cycle assessment and data driven sensitivity analysis.

---

## 2. Research Question

> Can hydrometallurgical recycling of spent NMC622 battery material produce an NMC622 precursor with lower environmental impacts than production of an equivalent virgin precursor, and which process parameters have the greatest influence on the result?

The project addresses four related questions:

1. What mass and energy flows are required to recover the target materials from NMC622 rich black mass?
2. What environmental impacts are associated with the recycling route?
3. How do those impacts compare with production of equivalent virgin NMC622 precursor from primary raw materials?
4. Which process parameters have the greatest influence on climate change and resource related impacts?

---

## 3. Chemistry Selection: NMC622

The project uses NMC622 as the defined cathode chemistry:

**LiNi0.6Mn0.2Co0.2O2**

NMC622 is selected because its composition is well defined, it contains lithium, nickel, manganese and cobalt, and hydrometallurgical recovery routes for NMC materials are well represented in the scientific literature.

The chemistry is fixed for the base case so that the feed composition, stoichiometric calculations, recovery calculations and product definition remain consistent throughout the project.

### 3.1 Theoretical elemental composition of pure NMC622

Using standard atomic weights:

| Element | Mass contribution in LiNi0.6Mn0.2Co0.2O2 | Theoretical mass fraction |
|---|---:|---:|
| Li | 6.941 g/mol | 7.16% |
| Ni | 35.216 g/mol | 36.33% |
| Mn | 10.988 g/mol | 11.33% |
| Co | 11.787 g/mol | 12.16% |
| O | 31.998 g/mol | 33.01% |
| Total | 96.930 g/mol | 100.00% |

These values represent pure NMC622 cathode active material. They do not represent the composition of spent black mass.

### 3.2 Black mass definition

The process feed is defined as **NMC622 rich spent black mass produced after battery mechanical preprocessing**.

Black mass can contain:

- NMC cathode active material
- graphite
- residual binder
- copper
- aluminium
- electrolyte residues
- moisture
- other metallic and non metallic impurities

The exact black mass composition will be taken from a peer reviewed literature source and documented in the process model. The theoretical NMC622 composition above will not be used as a substitute for measured black mass composition.

---

## 4. Battery Recycling Context

A lithium ion battery contains cathode and anode materials, electrolyte, separator, current collectors and structural components. The relative proportions depend on cell design, chemistry and battery level.

The project distinguishes between:

- Cell level composition
- Module and pack level composition
- Black mass composition after mechanical preprocessing

These levels are not combined in the process inventory.

The hydrometallurgical model begins with NMC622 rich black mass rather than a complete battery pack. Battery collection, pack dismantling and mechanical shredding are therefore not part of the foreground process model.

### 4.1 Materials targeted by the process

The foreground process targets:

- Nickel
- Manganese
- Cobalt
- Lithium

The process is designed around recovery of Ni, Mn and Co as an NMC622 precursor and recovery of lithium as a separate lithium product.

Copper, aluminium and other impurities are treated as impurity streams rather than target products of the hydrometallurgical foreground process.

### 4.2 Materials outside the base case

The following are outside the base case:

- Graphite recovery
- Electrolyte recovery
- Separator recovery
- Battery casing recovery
- Complete pack dismantling
- Reuse or second life applications
- Direct regeneration of the original cathode particles
- Final calcination and synthesis of finished NMC622 cathode active material

These topics may be discussed as industrial context, but they are not part of the modeled foreground process.

---

## 5. Why Hydrometallurgical Recycling?

Hydrometallurgical recycling uses aqueous chemical processing to transfer valuable battery metals into solution and subsequently recover them as purified products.

A representative NMC recycling route consists of:

1. Acid leaching
2. Solid and liquid separation
3. Impurity removal
4. Recovery of nickel, manganese and cobalt
5. Lithium recovery
6. Washing and drying of recovered products
7. Wastewater and residue treatment

Hydrometallurgical NMC recycling commonly uses acidic leaching followed by precipitation, solvent extraction or related separation processes. Literature also demonstrates direct recovery of Ni, Mn and Co as hydroxide precursor material rather than separating all three metals into individual products before precursor synthesis [2][3].

For this project, the base route uses sulfuric acid and hydrogen peroxide for reductive leaching:

**H2SO4 + H2O2**

The downstream route uses impurity removal followed by co precipitation of Ni, Mn and Co as an NMC622 precursor and separate lithium recovery.

This route is selected because it provides a clear connection between hydrometallurgical metal recovery and production of a material that can displace virgin NMC precursor.

---

## 6. EU Regulatory Framework

Regulation (EU) 2023/1542 establishes separate requirements for recycling efficiency, recovery of specific materials and recycled content. These metrics are distinct and are not interchangeable [4].

### 6.1 Recycling efficiency

For lithium based batteries, the regulation requires:

| Deadline | Minimum recycling efficiency |
|---|---:|
| 31 December 2025 | 65% by average weight |
| 31 December 2030 | 70% by average weight |

Recycling efficiency is a system level measure based on the average weight of material recovered from waste batteries.

### 6.2 Material recovery targets

The regulation also establishes recovery targets for individual materials:

| Material | By 31 December 2027 | By 31 December 2031 |
|---|---:|---:|
| Cobalt | 90% | 95% |
| Copper | 90% | 95% |
| Lead | 90% | 95% |
| Lithium | 50% | 80% |
| Nickel | 90% | 95% |

These targets are particularly relevant to the project because lithium, nickel and cobalt are explicitly recovered in the modeled process.

### 6.3 Recycled content

For industrial batteries above 2 kWh, electric vehicle batteries and SLI batteries covered by Article 8, the regulation establishes minimum shares of recovered material in active materials:

| Material | From 18 August 2031 | From 18 August 2036 |
|---|---:|---:|
| Cobalt | 16% | 26% |
| Lead | 85% | 85% |
| Lithium | 6% | 12% |
| Nickel | 6% | 15% |

The regulation also establishes documentation requirements for recycled content. Battery passport requirements include information such as material composition, carbon footprint information and recycled content [4].

These regulatory requirements provide the policy context for evaluating whether the modeled recycling route can achieve high recovery of critical battery materials while maintaining favorable environmental performance.

---

## 7. Goal and Scope

### 7.1 Goal

The goal is to evaluate a simplified hydrometallurgical process for recovering materials from NMC622 rich spent black mass and to quantify its environmental performance relative to production of equivalent virgin NMC622 precursor.

The project combines:

- Process simulation in DWSIM
- Life cycle assessment in OpenLCA
- Python based sensitivity analysis and visualization

### 7.2 Functional unit

The functional unit is:

> **1 kg of NMC622 precursor material, Ni0.6Mn0.2Co0.2(OH)2, produced at the recycling process gate.**

This functional unit represents the main recovered Ni, Mn and Co product from the recycling route.

The functional unit is a precursor material rather than finished NMC622 cathode active material because the base process does not include final lithiation and calcination.

### 7.3 Reference flow

The reference flow is:

> **The quantity of NMC622 rich spent black mass required to produce 1 kg of NMC622 precursor at the specified product recovery and composition.**

The reference flow will be calculated from the black mass composition and process recovery efficiencies.

This means that the amount of black mass required for the functional unit is not assumed to be exactly 1 kg.

### 7.4 Co product

Lithium recovered from the process will be represented as a separate lithium product, expected to be lithium carbonate where supported by the selected literature route.

The lithium product is a co product of the recycling process and must be accounted for consistently in the LCA. The base comparison will use system expansion or substitution so that recovered lithium can receive a credit for displacement of equivalent virgin lithium product, provided the recovered product meets the defined quality assumption.

---

## 8. System Boundary

The foreground recycling process uses a **gate to gate boundary**:

**NMC622 rich spent black mass entering the recycling process**

through

**hydrometallurgical processing**

to

**recovered precursor and lithium products leaving the recycling process.**

The LCA will also include relevant upstream background processes for:

- Electricity generation
- Sulfuric acid production
- Hydrogen peroxide production
- Sodium hydroxide production
- Sodium carbonate or other lithium precipitation reagent production
- Process water
- Transport where included in the defined scenario
- Virgin material production for the comparison system

### 8.1 Black mass treatment

Battery production, battery use, collection, dismantling and mechanical shredding are outside the foreground process.

The black mass enters the model as a waste derived feedstock under a cut off approach. No environmental burden from the original battery manufacturing or first use is assigned to the black mass in the base case.

The energy and materials required for producing black mass are therefore not included in the base case. This is a defined modeling choice and not an assumption that those operations have zero environmental impact.

### 8.2 Included foreground operations

The foreground process includes:

1. Black mass preparation for leaching
2. Acid leaching
3. Solid and liquid separation
4. Impurity removal
5. Ni, Mn and Co co precipitation
6. Precursor washing and drying
7. Lithium recovery
8. Wastewater and residue treatment
9. Product streams leaving the process

---

## 9. Process Route

The base case process route is:

```text
NMC622 rich spent black mass
              |
              v
        Acid leaching
       H2SO4 + H2O2
              |
              v
   Solid and liquid separation
              |             |
              |             +------> Solid residue
              v
          Leachate
              |
              v
     Impurity removal
    Fe / Al / Cu control
              |
              v
      Purified leachate
              |
              +----------------------+
              |                      |
              v                      v
   Ni-Mn-Co co precipitation     Lithium recovery
              |                      |
              v                      v 
     NMC622 precursor          Lithium product
              |
              v
   Wastewater and residue treatment
```

The exact reagent quantities, recovery efficiencies, temperatures, residence times and separation assumptions are defined in the process model documentation.

### 9.1 Leaching

Sulfuric acid and hydrogen peroxide are used as the base leaching system.

The leaching step transfers lithium, nickel, manganese and cobalt from the cathode material into an aqueous solution.

The DWSIM model will represent dissolution using literature based conversion or recovery parameters rather than claiming rigorous electrolyte equilibrium.

### 9.2 Impurity removal

The leachate can contain impurities including Fe, Al and Cu. These impurities can interfere with downstream precursor production and therefore require removal or control.

The process model will represent impurity removal using literature based separation efficiencies.

### 9.3 NMC622 precursor recovery

Ni, Mn and Co are recovered together as:

**Ni0.6Mn0.2Co0.2(OH)2**

The co precipitation step is selected because NMC precursor manufacturing commonly uses controlled precipitation of Ni, Mn and Co hydroxides from a mixed metal solution. Recent research has also demonstrated integrated hydrometallurgical recovery of NMC precursor from black mass [2].

The project does not claim that the resulting precursor automatically meets commercial battery grade specifications. Product purity and quality are treated as explicit modeling assumptions and are supported by literature where data are available.

### 9.4 Lithium recovery

Lithium remaining in the solution after transition metal recovery is recovered as a lithium product, with lithium carbonate used as the base case where supported by the selected process literature.

### 9.5 Wastewater and residues

The model includes simplified treatment of process wastewater and solid residues.

The purpose is to avoid terminating the material balance immediately after valuable metal recovery and to account for the main environmental consequences of neutralization and residue handling.

Detailed industrial wastewater treatment design is outside the scope of this portfolio study.

---

## 10. DWSIM Modeling Strategy

DWSIM is used as the process simulation platform for the foreground process.

The free or Community version is sufficient for the base project because the model does not depend on rigorous aqueous electrolyte thermodynamics.

The base DWSIM strategy is:

| Process step | DWSIM representation |
|---|---|
| Feed preparation | Material stream |
| Reagent addition | Mixer |
| Leaching | Conversion reactor |
| Heating and cooling | Heater and cooler |
| Solid and liquid separation | Solid or component separation |
| Impurity removal | Simplified conversion and separation |
| Ni, Mn, Co co precipitation | Simplified conversion or precipitation representation |
| Lithium recovery | Simplified conversion and solid separation |
| Wastewater treatment | Neutralization and separation representation |
| Product streams | Material streams |
| Energy balance | Energy streams and unit operation duties |

The DWSIM model will prioritize:

- Overall mass balance
- Elemental mass balance
- Metal recovery
- Reagent consumption
- Water consumption
- Energy consumption
- Product and waste quantities

The project will not claim rigorous calculation of pH dependent speciation, activity coefficients, precipitation equilibria or solvent extraction thermodynamics unless the required thermodynamic data and DWSIM capabilities are explicitly available.

DWSIM's current Electrolytes extension provides Electrolyte NRTL and Extended UNIQUAC models, including treatment of dissociation, salt precipitation and complexation, but these advanced property packages are part of the Patreon Edition [5]. The base project therefore remains compatible with the free version.

---

## 11. OpenLCA Strategy

OpenLCA is used to convert the process inventory into environmental impact results.

The DWSIM model provides the foreground inventory:

- Black mass input
- Chemicals
- Water
- Electricity
- Heating and cooling requirements
- Recovered precursor
- Lithium product
- Solid residue
- Wastewater

OpenLCA provides:

- Background life cycle inventory data
- Life cycle impact assessment
- Comparison with virgin material production
- Contribution analysis
- Scenario comparison

### 11.1 Background database

The preferred background database will be **ecoinvent** if legitimate access is available.

ecoinvent requires a valid license for use in openLCA. It should not be described as a free database [6].

If ecoinvent is not available, the project will use an appropriate freely available background database such as **BAFU:2026**, supplemented with literature derived inventory data where necessary. BAFU:2026 is currently available free of charge through openLCA Nexus [7].

Agribalyse 3.2 Core is also available free of charge, although its coverage and suitability for industrial metal supply chains must be checked before use [8].

The selected database, version, process names and geographic assumptions will be documented in the final LCA model.

---

## 12. Life Cycle Impact Assessment

The main LCIA method is:

**ReCiPe 2016 Midpoint, Hierarchist perspective**

The project focuses on a limited number of indicators rather than reporting the complete ReCiPe midpoint suite.

### Primary indicators

- Climate change
- Mineral resource scarcity

### Secondary indicators

- Fossil resource scarcity
- Water consumption
- Freshwater ecotoxicity

Energy demand will be reported separately as a process and inventory indicator where the selected database and method provide a consistent calculation.

The main headline result will be **kg CO2 equivalent per functional unit**.

---

## 13. Virgin Material Comparison

The recycling route will be compared against production of an equivalent virgin NMC622 precursor:

**Recycled NMC622 precursor**

versus

**Virgin NMC622 precursor produced from primary raw materials**

The comparison will use equivalent product composition and functional performance at the defined process gate.

The virgin system will include relevant upstream production of primary raw materials and precursor production.

The recycling system will include the defined foreground recycling process and its upstream background inputs.

The environmental benefit will be expressed as:

**Impact reduction = Virgin route impact - Recycling route impact**

and:

**Impact reduction (%) = (Virgin route impact - Recycling route impact) / Virgin route impact x 100**

Recovered lithium will be treated as a co product and credited through the selected substitution or system expansion approach.

---

## 14. Key Modeling Parameters

The following parameters are expected to have a strong influence on the result:

| Parameter | Role |
|---|---|
| NMC content of black mass | Determines recoverable metal inventory |
| Black mass moisture | Affects effective feed composition |
| H2SO4 consumption | Determines reagent burden and sulfate generation |
| H2O2 consumption | Determines reagent burden |
| Solid to liquid ratio | Affects water and downstream treatment requirements |
| Leaching temperature | Affects energy demand |
| Leaching efficiency | Determines dissolved metal quantities |
| Ni recovery | Determines precursor yield |
| Mn recovery | Determines precursor yield |
| Co recovery | Determines precursor yield |
| Li recovery | Determines lithium product yield |
| NaOH consumption | Affects purification and precipitation burden |
| Lithium precipitation reagent | Affects lithium recovery burden |
| Electricity consumption | Major process energy input |
| Electricity carbon intensity | Strongly affects climate impact |
| Water consumption | Affects water related impacts |
| Transport distance | Tests geographic sensitivity |
| Product purity | Determines whether recovered material can displace virgin material |

Numerical values and literature ranges for these parameters will be documented in the process model and life cycle inventory methodology.

---

## 15. Scenario and Sensitivity Framework

The project will use three principal scenarios.

### Base case

A literature based process using representative recovery efficiencies, reagent consumption and energy requirements.

### High recovery case

Higher metal recovery within a literature supported range.

### Low carbon electricity case

The same process operated with a lower carbon electricity mix.

The Python analysis will additionally vary individual parameters such as:

- Metal recovery
- H2SO4 consumption
- H2O2 consumption
- Electricity consumption
- Electricity carbon intensity
- Water consumption
- Transport distance

The main outputs will be:

- Climate impact
- Resource impact
- Energy demand
- Material recovery
- Percentage impact reduction relative to virgin production

---

## 16. Validation Strategy

The project will use several validation checks.

### 16.1 Mass balance

The DWSIM model must close the overall mass balance within a defined numerical tolerance.

### 16.2 Element balance

Li, Ni, Mn and Co will be tracked from the feed through the process and into:

- Recovered products
- Solid residues
- Wastewater
- Unrecovered streams

### 16.3 Recovery comparison

Simulated recovery efficiencies will be compared with published experimental values.

### 16.4 Inventory cross check

Major chemical and energy inputs will be compared with published hydrometallurgical LCA studies.

### 16.5 LCA plausibility check

The final impact results will be compared with published recycling LCA studies to identify major differences and explain the reasons for those differences.

The model is intended as a process screening and portfolio engineering model, not as an experimentally validated industrial plant model.

---

## 17. Data Quality and Reproducibility

Every major process parameter will be assigned a source category:

1. Experimental literature data
2. Peer reviewed LCA inventory data
3. Official database data
4. Engineering calculation
5. Explicit modeling assumption

The final project will record:

- Source
- Dataset or paper
- Parameter
- Unit
- Value
- Geographic scope
- Year where relevant
- Base case value
- Sensitivity range
- Reason for selection

This allows the DWSIM, Python and OpenLCA models to remain consistent.

---

## 18. Assumptions and Limitations

The base project has the following defined limitations:

1. The process starts from NMC622 rich black mass rather than complete end of life battery packs.
2. Battery collection, dismantling and mechanical shredding are outside the foreground system.
3. The original battery manufacturing and use phase are not assigned to the waste black mass under the cut off approach.
4. Black mass composition is literature based and may differ from a specific industrial recycler feed.
5. DWSIM uses simplified conversion and separation representations for complex aqueous chemistry.
6. Rigorous electrolyte speciation and precipitation equilibrium are not required for the base model.
7. Recovered precursor is assumed to be functionally capable of displacing equivalent virgin precursor, subject to the defined product quality scenario.
8. Final cathode synthesis, lithiation and calcination are outside the base process.
9. Wastewater and residue treatment are represented at screening level rather than as detailed plant designs.
10. Background LCA results depend on the selected database, version, geography and dataset choices.
11. The study does not claim experimental validation or commercial plant scale validation.
12. Results are intended for comparative process screening and engineering portfolio demonstration.

---

## 19. Project Deliverables

The project will produce:

1. A DWSIM process model
2. A documented process mass and energy balance
3. A literature based life cycle inventory
4. An OpenLCA model
5. A virgin material comparison
6. A Python sensitivity analysis
7. Material flow and Sankey visualization
8. Interactive or static environmental impact visualizations
9. A GitHub repository with reproducible documentation
10. A concise project summary suitable for a professional portfolio

---

## 20. Literature Basis

The literature review will prioritize peer reviewed research and official sources.

Key sources currently supporting the project include:

- Recent hydrometallurgical recycling research describing acid leaching, impurity removal, Ni-Mn-Co precursor recovery and lithium recovery [2][3].
- Environmental impact assessment of hydrometallurgical NMC recycling [9].
- Life cycle assessment research comparing recycling routes and identifying process hotspots [10].
- Research on process conditions and reagent requirements for NMC hydrometallurgy [11].
- Regulation (EU) 2023/1542 for recycling efficiency, material recovery and recycled content requirements [4].
- Official DWSIM documentation for process simulation capabilities [5].
- OpenLCA documentation for available background databases [6][7][8].

Detailed numerical process assumptions will be selected from the literature during development of `02_Process_Model_and_LCI_Methodology.md`.

---

## 21. References

1. International Energy Agency, Global EV Outlook 2025, Executive Summary.
   https://www.iea.org/reports/global-ev-outlook-2025/executive-summary

2. Particle engineering of recycled NMC precursors via
   integrated co-precipitation synthesis in the hydrometallurgical recycling of
   Li-ion batteries. Powder Technology, 2026.
   https://doi.org/10.1016/j.powtec.2026.122571

3. Hydrometallurgical recycling technologies for NMC Li-ion battery cathodes:
   current industrial practice and new R&D trends.
   https://www.sciencedirect.com/org/science/article/pii/S2753812523001489

4. Regulation (EU) 2023/1542 concerning batteries and waste batteries,
   consolidated text and Annex XII.
   https://eur-lex.europa.eu/eli/reg/2023/1542/2025-07-31/eng

5. DWSIM official website and Electrolytes extension documentation.
   https://dwsim.org/

6. openLCA and ecoinvent information.
   https://www.openlca.org/ecoinvent-3-12-available-for-openlca/

7. BAFU:2026 version 1, Swiss Federal Office for the Environment, available
   through openLCA Nexus.
   https://www.openlca.org/bafu2026-version-1-is-now-available-on-nexus/

8. Agribalyse 3.2 Core, available free through openLCA Nexus.
   https://www.openlca.org/agribalyse-3-2-core-is-now-available-for-free/

9. Environmental Impact Assessment of LiNi1/3Mn1/3Co1/3O2 Hydrometallurgical
   Cathode Recycling from Spent Lithium-Ion Batteries, ACS Sustainable Chemistry
   and Engineering.
   https://pubs.acs.org/doi/10.1021/acssuschemeng.2c01496

10. Using LCA to aid process development for hydrometallurgical recycling of
    end-of-life lithium-ion batteries.
    https://www.sciencedirect.com/science/article/pii/S0956053X25001680

11. Rajaeifar et al., Life cycle assessment of lithium-ion battery recycling
    using pyrometallurgical technologies, Journal of Industrial Ecology.
    https://onlinelibrary.wiley.com/doi/10.1111/jiec.13157

12. Unraveling the nature of sulfide ions in hydrometallurgical recycling of
    NCM622 cathode material, Energy Storage Materials, 2024.
    https://doi.org/10.1016/j.ensm.2023.103128

13. Recovery of NixMnyCoz(OH)2 and Li2CO3 from spent Li-ionB cathode leachates using
    non-Na precipitant-based chemical precipitation for sustainable recycling.
    https://www.sciencedirect.com/science/article/pii/S2666821123001394

---
