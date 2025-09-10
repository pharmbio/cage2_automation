from lab_adaption.processes.basic_process import BasicProcess


class CleoCellProcess(BasicProcess):
    def __init__(self, priority=7):  # 0 has highest priority
        super().__init__(priority=priority, num_plates=4, process_name="CleoCellProcess")

    def init_service_resources(self):
        # setting start position of containers
        super().init_service_resources()
        #available_positions = [4, 6, 8, 10]
        for i, cont in enumerate(self.containers):
            cont.set_start_position(
                resource=self.incubator1, position=i)

    def process(self):
        wait_time = 20 * 60
        min_wait_time = wait_time
        max_wait_time = wait_time + 1*60
        for cont in self.containers:
            cont.wait_cost(40)
            self.robot_arm.move(cont, self.washer, lidded=False, read_barcode=True)
            cont.wait_cost(40)
            self.washer.fix_cells(labware=cont, protocol="fix_cells", label=f"fix_{cont.name}")
            cont.wait_cost(40)
            self.robot_arm.move(cont, self.hotel1, lidded=True)
            self.robot_arm.move(cont, self.washer, lidded=False)
            cont.wait_cost(40)
            self.washer.wash_cells(labware=cont, protocol="wash_cells", duration=180, relations=[
                ("min_wait", f"fix_{cont.name}", [min_wait_time]),
                ("max_wait", f"fix_{cont.name}", [max_wait_time]),
            ])
            cont.wait_cost(40)
            self.robot_arm.move(cont, self.sealer)
            cont.wait_cost(10)
            self.sealer.seal_plate(cont)
            self.robot_arm.move(cont, self.hotel1)
            self.robot_arm.move(cont, self.squid_pool)
            self.squid_pool.run_protocol(labware=cont, protocol="look_at_it", duration=60*60)
            self.robot_arm.move(cont, self.hotel1)

