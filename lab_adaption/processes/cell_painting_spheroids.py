"""
Duplicate this file and add/modify the missing parts to create new processes
"""

from lab_adaption.processes.basic_process import BasicProcess


class CellPaintingSpheroids(BasicProcess):
    def __init__(self):
        super().__init__(
            priority=0,
            num_plates=10,
            process_name="CellPaintingSpheroids",
        )

    def init_service_resources(self):
        # setting start position of containers
        super().init_service_resources()
        for i, cont in enumerate(self.containers):
            cont.set_start_position(self.incubator1, i)

    def process(self):
        incubation_time = 20 * 60  # in seconds
        wash1 = ""
        wash_prime = "0_W_D_prime_PBS.LHC"
        wash_before_pfa = "3_W_1X_beforePFA_leaves20ul_PBS.LHC"
        disp1 = ""
        disp_pfa_prime = "4.0_D_SA_PRIME_PFA.LHC"
        disp_pfa = "4.1_D_SA_60ul_PFA.LHC"
        wash_before_triton = "5_W_2X_beforeTX_leaves20ul_PBS.LHC"
        disp2= ""
        disp_triton_prime = "6.0_D_P1_PRIME_Triton.LHC"
        disp_triton = "6.1_D_P1_60ul_Triton.LHC"
        wash_before_stains = "7_W_1X_beforeStains_leaves11ul_PBS.LHC"
        disp3 = ""
        disp_stains_prime = "8.0_D_P2_MIX_PRIME.LHC"
        disp_stains_prep = "8.0b_D_P2_purge_then_predispense.LHC"
        disp_stains = "8.1_D_P2_20ul_stains.LHC"

        for cont in self.containers:
            # PFA
            self.robot_arm.move(cont, self.washer, lidded=False)
            #self.washer.run_protocol(protocol=wash_prime, labware=cont, duration=50)
            #self.washer.run_protocol(protocol=wash_before_pfa, labware=cont, duration=60)
            self.washer.run_protocol(protocol=wash1, labware=cont, duration=110)
            self.robot_arm.move(cont, self.dispenser, lidded=False)
            #self.dispenser.run_protocol(protocol=disp_pfa_prime, labware=cont, duration=40)
            #self.dispenser.run_protocol(protocol=disp_pfa, labware=cont, duration=50)
            self.dispenser.run_protocol(protocol=disp1, labware=cont, duration=90)
            self.robot_arm.move(cont, self.incubator1, lidded=True)
            self.incubator1.incubate(cont, duration=incubation_time, temperature=37)

            # Triton
            self.robot_arm.move(cont, self.washer, lidded=False)
            self.washer.run_protocol(protocol=wash_before_triton, labware=cont, duration=120)
            self.robot_arm.move(cont, self.dispenser, lidded=False)
            #self.dispenser.run_protocol(protocol=disp_triton_prime, labware=cont, duration=40)
            #self.dispenser.run_protocol(protocol=disp_triton, labware=cont, duration=50)
            self.dispenser.run_protocol(protocol=disp2, labware=cont, duration=90)
            self.robot_arm.move(cont, self.incubator1, lidded=True)
            self.incubator1.incubate(cont, duration=incubation_time, temperature=37)

            # Stains
            self.robot_arm.move(cont, self.washer, lidded=False)
            self.washer.run_protocol(protocol=wash_before_stains, labware=cont, duration=120)
            self.robot_arm.move(cont, self.dispenser, lidded=False)
            #self.dispenser.run_protocol(protocol=disp_stains_prime, labware=cont, duration=30)
            #self.dispenser.run_protocol(protocol=disp_stains_prep, labware=cont, duration=120)
            #self.dispenser.run_protocol(protocol=disp_stains, labware=cont, duration=50)
            self.dispenser.run_protocol(protocol=disp3, labware=cont, duration=200)
            self.robot_arm.move(cont, self.incubator1, lidded=True)
            self.incubator1.incubate(cont, duration=incubation_time, temperature=37)
