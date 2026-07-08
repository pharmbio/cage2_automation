Laboratory workflows are expressed as *processes* and use the [PythonLab package](pythonlab.md) to express the steps.
A process defines the labware that is used and what the interactions should be. 

## Basic process
If you are planning to define multiple processes within the same lab it is advised to start with a basic process that
subsequent processes can inherit from. This is the basis that other processes can build on.

```python title="BasicProcess"
--8<-- "lab_adaption/processes/basic_process.py"
```

In this case, `BasicProcess` defines a number of resources that are present in this setup. There are 3 hotels for
storage, a robot arm to move plates, a human being and a "greeter" entity. It also initialized an arbitrary amount of
plates. The names in your `BasicProcess` need to match with the names defined in your `platform_config`.

## Simple one-step process
The process `GreeterTest` defines a simple process that only includes one step.
The `process` function implements the actual steps that should be executed. In this case, it is only one call to the 
`Greeter` SiLA server

```python title="GreeterTest"
--8<-- "lab_adaption/processes/greeter_test.py"
```

## A more elaborate process
`InterestingExample` is a more elaborate process with multiple interactions.

```python title="InterestingExample"
--8<-- "lab_adaption/processes/interesting_example.py"
```

One by one, it reads the barcodes of the containers and holds it up for a human being to inspect. Based on their answer,
the container is moved either to hotel 1 or 3.

## Inspecting processes
Pythonlab converts process descriptions to a graph-based workflow. [Quickstart](quickstart.md) shows how you can access
the UI to inspect the workflow graph.