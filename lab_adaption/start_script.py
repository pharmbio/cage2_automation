import traceback
import logging
from laborchestrator.old_dash_app import SMDashApp, OrchestratorInterface
from laborchestrator.orchestrator_implementation import Orchestrator
from platform_status_db.larastatus.status_db_implementation import StatusDBImplementation
import processes
import time
import os


def start():
    orchestrator = Orchestrator(reader='PythonLab', worker_type=MyWorker)

    # create and run dash app until eternity
    dash_app = SMDashApp(orchestrator, port=8050, process_module=processes)
    dash_app.run()

    #add database client
    database_client = StatusDBImplementation()
    orchestrator.inject_db_interface(database_client)

    #configure scheduler
    # try to find a running scheduler server and set its lab configuration:
    try:
        from pythonlabscheduler.sila_server import Client as SchedulerClient
        scheduler = SchedulerClient.discover(insecure=True, timeout=5)
        # get the absolute filepath
        config_file = os.path.join(os.path.dirname(__file__), "lab_config.yaml")
        with open(config_file, 'r') as reader:
            scheduler.LabConfigurationController.LoadJobShopFromFile(reader.read())
        print("Configured the lab of the scheduling service")
    except:
        print(traceback.print_exc())
        logging.warning(f"Could not find a running scheduler server. You will have to configure the lab manually.")

    while True:
        time.sleep(1)


if __name__ == "__main__":
    start()
