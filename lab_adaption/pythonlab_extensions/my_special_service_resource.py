from pythonlab.resource import ServiceResource, LabwareResource


class MySpecialServiceResource(ServiceResource):
    """
    Implementation of an Echo550 for pythonLab
    """

    def my_special_functionality(
        self,
        labware: LabwareResource,
        my_required_parameter: int,
        my_optional_task: str | None = None,
        **kwargs,
    ):
        # add parameters as needed by the sila wrapper
        # all will be accessible in step.data in WorkerInterface.execute_process_step()
        if my_optional_task:
            kwargs["extra"] = my_optional_task
        kwargs["my_key"] = my_required_parameter

        # optional: guess the duration
        kwargs["duration"] = 30 + 10 * my_required_parameter

        # this is important for building the internal graph structure
        self.proc.add_process_step(self, [labware], **kwargs)
