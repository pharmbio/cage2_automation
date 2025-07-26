from pythonlab.resource import ServiceResource, LabwareResource


class EchoServiceResource(ServiceResource):
    """
    Implementation of an Echo550 for pythonLab
    """
    def execute_transfer_protocol(self, protocol: str, source_plate: LabwareResource,
                                  target_plate: LabwareResource, **kwargs):
        if "duration" not in kwargs:
            kwargs["duration"] = 120
        kwargs["fct"] = "execute_protocol"
        kwargs["protocol"] = protocol
        self.proc.add_process_step(self, [source_plate, target_plate], **kwargs)
