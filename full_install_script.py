
import sys
import os
from pathlib import Path
from typing import NamedTuple, Dict, List
import pip
import subprocess

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
    url: str
    branch: str
    setup_files: List[str] = ["."]

    def install(self, name):
        print(f"Installing {name} from {self.url}/{self.branch}")
        call(f"git clone {self.url} {name}")
        os.chdir(f"./{name}")
        call(f"git checkout {self.branch}")
        call("git pull")
        for setup_file in self.setup_files:
            call(f"pip install -e {setup_file}")
        os.chdir("./..")

orchestrator_git = GitRepo(
    "https://gitlab.com/opensourcelab/laborchestrator.git",
    "feature/release_V0_1_draft"
)
scheduler_git = GitRepo(
    "https://gitlab.com/opensourcelab/pythonlabscheduler.git",
    "feature/release_V0_1_draft"
)
tools_git = GitRepo(
    "https://gitlab.com/StefanMa/lara-tools.git",
    "main",
    setup_files=["lara_simulation/.", "utility"]
)
database_git = GitRepo(
    "https://gitlab.com/StefanMa/platform_status_db.git",
    "main"
)
lara_processes_git = GitRepo(
    "https://gitlab.com/lara-uni-greifswald/lara-processes.git",
    "feature/worker_implementation"
)
device_gits: Dict[str, GitRepo] = dict(
    cytomat=GitRepo("https://gitlab.com/opensourcelab/devices/incubators_shakers/thermo_cytomat2.git",
                          "feature/sila2_server", setup_files=["sila2_server/."]),
    barcode_reader=GitRepo("https://gitlab.com/opensourcelab/devices/barcodereader/omron-laserscanner-ms-3.git",
                          "feature/sila2_server", setup_files=["sila_server/."]),
    silafied_human=GitRepo("https://gitlab.com/StefanMa/silafiedhuman.git",
                          "main"),
    robotic_arm=GitRepo("https://gitlab.com/opensourcelab/devices/labrobots/thermo_f5.git",
                        "feature/sila_redo_impl", setup_files=["sila_server/."]),
    agilent_bravo=GitRepo("https://gitlab.com/opensourcelab/devices/liquidhandler/agilent-vworks.git",
                          "feature/sila2_server", setup_files=["sila_server/."]),
)

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
    setup_file = os.path.join(src_dir, 'setup.py')
    # this no longer works:
    #~ run_setup(setup_file,  script_args=['install', '--prefix', lib_dir ])
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '.'])


def make_dir_structure():
    print("Creating directory structure")
    call("mkdir devices")


def install_orchestrator():
    print("Installing laborchestrator...")
    orchestrator_git.install('orchestrator')

def install_devices():
    print("Installing sila2 servers for devices")
    os.chdir("./devices")
    for name, repo in device_gits.items():
        if query_yes_no(f"Install {name}?"):
            repo.install(name)
    os.chdir("./..")


def install_tools():
    print("Installing lara-tools...")
    name= "lara_server_tools"
    call(f"git clone {tools_git.url} {name}")
    os.chdir(f"./{name}/lara_simulation")
    call("pip install -e .")
    os.chdir(f"../utility")
    call("pip install -e .")
    os.chdir("./../..")


def run_tests():
    print("Testing installation")
    try:
        os.chdir('platform_status_database/platform_status_db')
        call("python manage.py makemigrations")
        call("python manage.py migrate")
        from platform_status_db.larastatus.status_db_implementation import StatusDBImplementation
        db_client = StatusDBImplementation()
        db_client.create_lara()
    finally:
        os.chdir("../..")

def installOnLinux():
    orchestrator_git.install('orchestrator')
    make_dir_structure()
    #if query_yes_no("Install scheduler?"):
    scheduler_git.install('scheduler')
    #if query_yes_no("Install lara-tools (needed to run&visualize simulated devices)?"):
    #install_tools()
    tools_git.install("lara_server_tools")
    #if query_yes_no("Install device servers?"):
    install_devices()

    database_git.install("platform_status_database")

    #if query_yes_no("Run pytest on every installed package? This might take about 1 or 2 minutes."):
    run_tests()


if __name__ == '__main__':
    printWelcomeMessage()
    installOnLinux()

    print("Enjoy!")

