# pythonLab

This is the specification and development repository of
**pythonLab**, a universal, extendable and safe language for laboratory processes.
Since this process language needs many characteristics of a programming language, like conditions (if ...), loops (for/while), variables, etc. we do not want to re-invent the wheel twice but rather use the **python syntax**, which is very popular in science.

Also processes are defined in python, they are not **excecuted** but **parsed into directed graphs** 

## Examples

### Simple linear workflow

<details>
<summary>Show code</summary>

``` python
protocol_path = "protocols/evacuation_speroids.lhc"
self.robot_arm.move(cont, self.dispenser)
self.dispenser.run_protocol(labware=cont, protocol=protocol_path)
```

</details>

This process is parsed into the following workflow graph:

<details>
<summary>Show graph</summary>

![Simple linear workflow](docs/images/workflows/simple_linear_workflow.svg)

</details>

### Implicit movements for reagents and multi labware steps

<details>
<summary>Show code</summary>

``` python        
bravo_positions = [4, 6, 7, 8]
for i in range(len(growth_plates)):
    self.robot_arm.move(cont, target_loc=self.pipetter, lidded=False, position=bravo_positions[i])
self.pipetter.executeProtocol(growth_plates[0], protocol=sup_rem_protocol, duration=200,
                              reagents=growth_plates[1:],
self.pipetter.executeProtocol(growth_plates, protocol=lysis_protocol, duration=240,
                            reagents=[self.lysis_buffer],
                            reagent_pos=[3])          
for cont in growth_plates:
    self.robot_arm.move(cont, self.incubator2, lidded=True)                           
```

</details>

The reagent plates in `reagents=[...]` are moved to and from the liquid handler implicitly:

<details>
<summary>Show graph</summary>

![Implicit reagent movement workflow](docs/images/workflows/implicit_reagent_movement_workflow.svg)

</details>

### Simple for-loop

<details>
<summary>Show code</summary>

``` python
for plate in self.target_plates:
    self.robot_arm.move(plate, self.echo, role="destination", read_barcode=True, lidded=False)
    self.echo.execute_transfer_protocol(self.source_plate, plate, protocol)
    self.robot_arm.move(plate, self.hotel2, lidded=True)
```

</details>

This process is parsed into the following workflow graph:

<details>
<summary>Show graph</summary>

![Simple for-loop workflow](docs/images/workflows/simple_for_loop_workflow.svg)

</details>

### Single conditional

<details>
<summary>Show code</summary>

``` python
def is_acceptable(answer) -> bool:
    return answer.Response.value >= 5

cont = self.containers[0]
self.robot_arm.move(cont, self.human)
answer = self.human.request_number(cont, message="assign quality score")
acceptable = self.is_acceptable(answer)
if acceptable:
    self.robot_arm.move(cont, self.incubator1)
else:
    self.robot_arm.move(cont, self.hotel1)
```

</details>

This process is parsed into the following workflow graph:

<details>
<summary>Show graph</summary>

![Single conditional workflow](docs/images/workflows/single_conditional_workflow.svg)

</details>

### Nested for-loop and timing comstraints

<details>
<summary>Show code</summary>

``` python
meas_time = 65
meas_points = [0, 5, 15, 30]
for cont in self.containers:
    self.robot_arm.move(cont, self.reader)
    self.reader.single_read(cont, method="protocol", label=f"read_{cont.name}_{0}")
    for i in range(1, len(meas_points)):
        self.robot_arm.move(cont, self.incubator1)
        self.incubator1.incubate(cont, duration=10, temperature=295, shaking_frequency=400)
        self.robot_arm.move(cont, self.reader)
        wait = 60*(meas_points[i] - meas_points[i-1]) - meas_time
        self.reader.single_read(cont, method="protocol", label=f"read_{cont.name}_{i}",
                                relations=[("min_wait", f"read_{cont.name}_{i-1}", [wait]),
                                            ("max_wait", f"read_{cont.name}_{i-1}", [wait+20])
                                            ]
        )
    self.robot_arm.move(cont, self.hotel)
```

</details>

This process is parsed into the following workflow graph:

<details>
<summary>Show graph</summary>

![Nested for-loop workflow](docs/images/workflows/nested_for_loop_workflow.svg)

</details>

### Nested for-loop with conditional and break

<details>
<summary>Show code</summary>

``` python
# cultured plates in incubator 37°, 200rpm, 45-90 min until aver_OD is >= 0.4.
for cont in cultured_plates:
    for j in range(3):
        self.robot_arm.move(cont, target_loc=self.reader2, lidded=False)
        od = self.reader2.single_read(cont, method=od_600)
        if j < max_cult_intervals - 1:
            aver_od = self.compute_average(od)
            if aver_od > 0.4:
                break
            else:
                # incubate for another interval
                self.robot_arm.move(cont, target_loc=self.incubator2, lidded=True)
                self.incubator2.incubate(cont, duration=cult_time_interval, temperature=cult_temp,
                                         shaking_frequency=cult_shaking_freq)    
    self.robot_arm.move(cont, target_loc=self.pipetter, lidded=False, position=3)   
```

</details>

This process is parsed into the following workflow graph:

<details>
<summary>Show graph</summary>

![Nested for-loop with conditional and break workflow](docs/images/workflows/nested_conditional_break_workflow.svg)

</details>

## Key (desired) Features 

  * easy and simple to learn and write (close to simple English)
  * clear, human readable syntax
  * machine readable and writeable syntax
  * universal - applicable for most laboratory operations
  * transferable from one lab to another
  * [*Turing-complete*](https://en.wikipedia.org/wiki/Turing_completeness), including conditions and loops
  * easy extendible - prepared for the constant development of science
  * close to real laboratory work
  * vendor independent
  * safe to execute
  * converter from other lab description languages to pythonLab easy to implement

## Applications of pythonLab

  * general lab processes, common in any natural sciences lab (very broad application)
  * description of lab automation workflows
  * workflows on the lab devices (e.g. HPLC processes - sometimes also called 'methods', plate reader processes etc.)
  * data evaluation workflows

## Architecture of pythonLab

pythonLab processes are denoted in a python like syntax, but they are **not** directly executed by a *python interpreter*. They are rather parsed into a *workflow graph*, which can be used by a *Scheduler* to calculate 
an optimal schedule (=order of execution). This order of execution might be different from the initial notation. An *Orchestrator* executes then the schedule and supervises the device communication, e.g. to SiLA servers/devices.

![pythonLab Architecture](docs/images/pythonLab_architecture_overview.svg)

## [Specification](https://opensourcelab.gitlab.io/pythonLab/specification/0_specification_base.html)

Please find a draft of the pythonLab specification in [docs/specification](https://pythonlabor.gitlab.io/pythonLab/specification/specification.html) (very early stage !).

Very briefly, the generic lab description language should have many features a common programming language has and following the desired *Turning-completeness*, like:  

- variables  (x = value)
- conditions (if, else, ...)
- loops      (for ... while ....)
- functions / methods and subroutines 
- modules
- namespaces and versions for unique addressing of a process step
- (at a later stage of language development: object orientation)

**!! This is a proposal - we would like to discuss it with a wide range of scientist to find the best common ground** 

## [Documentation](https://opensourcelab.gitlab.io/pythonLab/)

The pythonLab Documentation can be found in [docs](https://pythonlabor.gitlab.io/pythonLab/)

## Why python ?

Python is a programming language that is very common in modern scientific laboratories and covers all the desired characteristics we expect of a user-friendly lab process programming language.

The syntax is very simple, and intuitive to learn.
Syntax validation comes for free: the python interpreter already does it.

Standardisation of a minimal set of functionally will be achieved by standardised packages provided by this site (or any publicly available site).
Defined namespaces and versioning allow unique addressing of a process step. 
e safe execution environment.

## Related projects

Here is an incomplete list of related OpenSource projects - please let us know, if we missed a relevant project. 

###  [Autoprotocoll](http://autoprotocol.org)

  * Syntax: JSON based 
  * (-) not *Turing complete*
  * (-) hard to write and read by humans

###  [LabOP](https://bioprotocols.github.io/labop/)

  * Syntax: RDF / python
  * (-) not *Turing complete* (?)
  * (-) hard to write and read by humans

### [RoboLiq](https://ellis.github.io/roboliq/protocol/index.html)

  * Syntax: yaml / Javascript
  * (-) not *Turing complete*
  * (-) hard to write and read by humans
  * (-) design not clearly specified

## Repository Maintainer:

* Stefan Maak (stefan.maak@uu.se)
