
import sys
import os
from pathlib import Path
from typing import NamedTuple, Dict, List
import subprocess
from argparse import ArgumentParser

from distutils.util import strtobool

# checking python version
major_version = sys.version_info.major
minor_version = sys.version_info.minor

# this works only with python >= 3.8
print(f"You are running python {major_version}.{minor_version}")

HOME_DIR = str(Path.home())

REPO_DIR = os.path.dirname(os.path.realpath(__file__))  # current directory of this repository


def printWelcomeMessage():
    installer_welcome_txt = (
        "______________________________________________________\n\n"
         " ___  ____  __      __    ___  \n"
         "/ __)(_  _)(  )    /__\  (__ \ \n"
         "\__ \ _)(_  )(__  /(__)\  / _/ \n"
         "(___/(____)(____)(__)(__)(____)\n\n"
         #"This is the SiLA2 Python3 installer\n"
         #"It will guide you through the complete installation \n"
         #"of the core parts of SiLA2-python ...\n"
         #"[type: ?    - for further information\n"
         #"       help - to list all input options    ]\n"
         "This script will guide you through the installation of the laborchestrator\n"
         "and the matching software-packages designed to work with it.\n"
         "______________________________________________________\n"
    )
    print(installer_welcome_txt)


class GitRepo(NamedTuple):
    name: str
    url: str
    branch: str
    setup_files: List[str] = ["."]

    def install(self, update=False, test=False):
        print(f"Installing {self.name} from {self.url}/{self.branch}")
        if self.name in os.listdir() or update:
            os.chdir(f"{self.name}")
            call("git pull")
        else:
            call(f"git clone {self.url} {self.name}")
            os.chdir(f"{self.name}")
            call(f"git checkout {self.branch}")
            call("git pull")
            for setup_file in self.setup_files:
                call(f"pip install -e {setup_file}")
        if test:
            call('pytest')
        os.chdir("..")

orchestrator_git = GitRepo(
    "orchestrator", "https://gitlab.com/opensourcelab/laborchestrator.git",
    "feature/release_V0_1_draft"
)
scheduler_git = GitRepo(
    "scheduler", "https://gitlab.com/opensourcelab/pythonlabscheduler.git",
    "feature/release_V0_1_draft",
    setup_files=['.', 'sila_server/.']
)
tools_git = GitRepo(
    "lara_server_tools", "https://gitlab.com/StefanMa/lara-tools.git",
    "main",
    setup_files=["lara_simulation/.", "utility"]
)
database_git = GitRepo(
    "platform_status_database", "https://gitlab.com/StefanMa/platform_status_db.git",
    "main"
)
lara_processes_git = GitRepo(
    "lara_implementation", "https://gitlab.com/lara-uni-greifswald/lara-processes.git",
    "feature/worker_implementation"
)
pythonlab_git = GitRepo(
    "pythonlab", "https://gitlab.com/opensourcelab/pythonLab.git",
    "feature/reader_develop_integration"
)
device_gits: List[GitRepo] = [
    GitRepo('cytomat', "https://gitlab.com/opensourcelab/devices/incubators_shakers/thermo_cytomat2.git",
                          "feature/sila2_server", setup_files=["sila2_server/."]),
    GitRepo("barcode_reader", "https://gitlab.com/opensourcelab/devices/barcodereader/omron-laserscanner-ms-3.git",
                          "feature/sila2_server", setup_files=["sila_server/."]),
    GitRepo("silafied_human", "https://gitlab.com/StefanMa/silafiedhuman.git",
                          "main"),
    GitRepo('robotic_arm', "https://gitlab.com/opensourcelab/devices/labrobots/thermo_f5.git",
                        "feature/sila_redo_impl", setup_files=["sila_server/."]),
    GitRepo('agilent_bravo', "https://gitlab.com/opensourcelab/devices/liquidhandler/agilent-vworks.git",
                          "feature/sila2_server", setup_files=["sila_server/."]),
    GitRepo('storage_carousel', "https://gitlab.com/opensourcelab/devices/container_storage/thermo_whitetree_carousel.git",
                             "feature/sila2_server", setup_files=["sila2_server/."]),
    GitRepo('reader', "https://gitlab.com/opensourcelab/devices/spectrometer/thermo-skanit6.git",
                   "feature/sila2_server", setup_files=["sila2_server/."]),
    GitRepo('centrifuge', "https://gitlab.com/opensourcelab/devices/centrifuges/hettich_rotanta_460r.git",
                       "feature/sila2_server", setup_files=["sila2_server/."]),

]

# --------------- installation helper functions, please do not modify -----------------------------
def query_yes_no(question, default_answer="yes", help=""):
    """Ask user at stdin a yes or no question

    :param question: question text to user
    :param default_answer: should be "yes" or "no"
    :param help: help text string
    :return:  :type: bool
    """
    if default_answer == "yes":
        prompt_txt = "{question} [Y/n] ".format(question=question)
    elif default_answer == "no":  # explicit no
        prompt_txt = "{question} [y/N] ".format(question=question)
    else:
        raise ValueError("default_answer must be 'yes' or 'no'!")

    while True:
        try:
            answer = input(prompt_txt)
            if answer:
                if answer == "?":
                    print(help)
                    continue
                else:
                    return strtobool(answer)
            else:
                return strtobool(default_answer)
        except ValueError:
            sys.stderr.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")
        except KeyboardInterrupt:
            sys.stderr.write("Query interrupted by user, exiting now ...")
            exit(0)

def query(question, default_answer="", help=""):
    """Ask user a question

    :param question: question text to user
    :param default_answer: any default answering text string
    :param help:  help text string
    :return: stripped answer string
    """
    prompt_txt = "{question} [{default_answer}] ".format(question=question, default_answer=default_answer)

    while True:
        answer = input(prompt_txt).strip()

        if answer:
            if answer == "?":
                print(help)
                continue
            else:
                return answer
        else:
            return default_answer

def call(command=""):
    ''' Convenient command call: it splits the command string into tokens (default separator: space)

    :param command: the command to be executed by the system
    '''
    try:
        cmd_lst = command.split()
        subprocess.run(cmd_lst, check=True)
    except subprocess.CalledProcessError as err:
        sys.stderr.write('CalledProcessERROR:{}'.format(err))


def run(command="", parameters=[]):
    '''This version is closer to the subprocess version

    :param command: the command to be executed by the system
    :param parameters: parameters of this command
    '''
    try:
        subprocess.run([command] + parameters, check=True, shell=True)
    except subprocess.CalledProcessError as err:
        sys.stderr.write('ERROR:', err)


def runSetup(src_dir="", lib_dir=""):
    """running a setup.py file within a pyhton script
       it requires a lot of things set...
       :param src_dir: directory containing the setup.py file
       :param lib_dir: directory containing the target lib directory
    """
    # all path settings seem to be required by run_setup and setup.py
    os.environ["PYTHONPATH"] = os.path.join(lib_dir, 'lib', 'python3.8', 'site-packages')
    sys.path.append(lib_dir)
    os.chdir(src_dir)
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '.'])


def make_dir_structure():
    if not "devices" in os.listdir():
        print("Creating directory structure")
        os.mkdir("devices")


def install_devices(test=False, update=False):
    print("Installing sila2 servers for devices")
    os.chdir("devices")
    for repo in device_gits:
        if update or query_yes_no(f"Install {repo.name}?"):
            repo.install(test=test, update=update)
    os.chdir("..")


def initialize():
    print("Testing installation")
    try:
        print(os.listdir())
        os.chdir(database_git.name)
        sys.path.append(os.path.abspath(os.curdir))
        os.chdir('platform_status_db')
        print("Migrating database")
        call("python manage.py migrate")
        if query_yes_no("Create the lara example in the database?"):
            from platform_status_db.larastatus.status_db_implementation import StatusDBImplementation
            db_client = StatusDBImplementation()
            db_client.create_lara()
        print("Please follow the dialog to create admin-credentials for the database.(It can then be accessed on"
              "http://127.0.0.1:8000/)")
        call("python manage.py createsuperuser")
    finally:
        os.chdir("..")
        os.chdir("..")


def installOnLinux(test=False, update=False):
    orchestrator_git.install(test=test, update=update)
    make_dir_structure()
    #if query_yes_no("Install scheduler?"):
    scheduler_git.install(test=test, update=update)
    #if query_yes_no("Install lara-tools (needed to run&visualize simulated devices)?"):
    tools_git.install(test=test, update=update)
    #if query_yes_no("Also install the lara-greifswald specialization?"):
    lara_processes_git.install(test=test, update=update)
    #if query_yes_no("Install device servers?"):
    install_devices(test=test, update=update)
    #if query_yes_no("Install supporting database for orchestrator?"):
    database_git.install(test=test, update=update)
    #if query_yes_no("Install PythonLab process description language? ( It is cool;-) )"):
    pythonlab_git.install(test=test, update=update)


def parse_args():
    parser = ArgumentParser(prog="install_script", description="Guides through the installation of the laborchestrator and its utils")
    parser.add_argument("--init", action="store_true", help="initializes the database", default=False)
    parser.add_argument("--test", action="store_true", help="tests the installation", default=False)
    parser.add_argument("--update", action="store_true", help="updates all installed git repositories", default=False)

    return parser.parse_args()



if __name__ == '__main__':
    printWelcomeMessage()
    args = parse_args()
    if args.init:
        initialize()
    else:
        installOnLinux(test=args.test, update=args.update)

    print("Enjoy!")

