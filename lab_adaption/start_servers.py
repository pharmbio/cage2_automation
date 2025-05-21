"""
Script to start the example servers for human, greeter and generic robotic arm
"""

from sila2.server import SilaServer


def start_servers():
    print("starting servers")
    to_start: list[SilaServer] = []
    try:
        from human_server import Server as HumanServer

        to_start.append(HumanServer())
    except ModuleNotFoundError:
        print("Could not import human_server. Is it installed?")
    try:
        from genericroboticarm.sila_server import Server as ArmServer
        from genericroboticarm.robo_APIs.dummy_robot import DummyRobot
        from genericroboticarm.control.robo_dash import RoboDashApp

        robot = DummyRobot()
        dash_app = RoboDashApp(robo_interface=robot, port=8055)
        dash_app.run()
        to_start.append(ArmServer(robot))
    except ModuleNotFoundError:
        print("Could not import robotic_arm_server. Is it installed?")
    try:
        from sila2_example_server import Server as GreeterServer

        to_start.append(GreeterServer())
    except ModuleNotFoundError:
        print("Could not import example_server. Is it installed?")

    for i, server in enumerate(to_start):
        port = 50053 + i
        server.start_insecure("127.0.0.1", port)

    print("\nPress 'q' -> enter to exit.")
    while not input() == "q":
        pass

    for server in to_start:
        server.stop(grace_period=0.5)


if __name__ == "__main__":
    start_servers()
