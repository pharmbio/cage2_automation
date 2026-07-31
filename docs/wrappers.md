# Wrappers
Wrappers are the interface between the lab orchestrator and the actual devices. They translate the high-level commands
defined in PythonLab to specific SiLA commands. Wrappers need to contain the code that calls the SiLA servers. 

## The wrapper structure

```python
class MyWrapper(DeviceInterface):
    @staticmethod
    def get_SiLA_handler(
        step: ProcessStep, 
        cont: ContainerInfo,
        sila_client: ShakerClient,
        **kwargs,
    ) -> Observable:
        ...
```

All wrappers need to inherit from `DeviceInterface`, which for now needs to be copied from
[this repository](https://gitlab.com/OpenLabAutomation/adaption-template/-/blob/main/lab_adaption/device_wrappers/device_interface.py).

## Examples

### Basic example
`GreeterWrapper` connects to a simple SiLA server that prints a greeting whenever it is called.

```python title="GreeterWrapper"
--8<-- "lab_adaption/device_wrappers/greeter_wrapper.py"
```

### Human interaction
`HumanWrapper` shows how human interaction can be integrated into your workflows. Interacts with the 
[Silafied Human server](https://gitlab.com/OpenLabAutomation/device-integration/silafiedhuman)

```python title="HumanWrapper"
--8<-- "lab_adaption/device_wrappers/human_wrapper.py"

```