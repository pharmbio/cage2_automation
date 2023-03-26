
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

def installAndImport(package):
    """ This imports a package and
        if not available, installs it first

        :return: The sucessfully imported package
    """
    import importlib
    try:
        importlib.import_module(package)
    except ImportError:
        import pip
        #~ pip.main(['install', package])
        print(f"Module {package} not installed! I'm going to install it now...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
    finally:
        globals()[package] = importlib.import_module(package)
        return globals()[package]

def installSiLAVenv(venv_module_name="venv"):
    """ :param venv_module_name: The module to use for creating the virtual environment
                            Possible values: 'venv' for the venv module that ships with python (default, works on Linux)
                                             'virtualenv' (works on Windows)
    """
    if query_yes_no("Install a virtual Python environment (highly recommended) ?",
                     help="HELP: This is the recommended installation mode for testing SiLA2-Python"):

        venv_dir = query("Please specify a directory for your virtual python3 environment",
                         default_answer=os.path.join(os.path.abspath(os.curdir), "venv", "lab_automation"),
                         help="HELP: specify the target directory for the virtual python3 environment")

        create_venv_anyway = True

        if os.path.exists(venv_dir):
            create_venv_anyway = query_yes_no("\nWARNING !! Virtual environment exists: [{}], shall I create it anyway ?".
                                              format(venv_dir), default_answer='no',
                                              help="HELP: create the python 3 virtual environment anyway ?")

        if create_venv_anyway:
            venv_module = installAndImport(venv_module_name)

            print("\t...creating virtual environment using '{module}' in dir [{dir}]".format(
                module=venv_module_name,
                dir=venv_dir
            ))
            if venv_module is not None:
                if venv_module_name == 'venv':
                    venv_module.create(venv_dir, system_site_packages=False, clear=False, symlinks=False, with_pip=True)
                elif venv_module_name == 'virtualenv':
                    venv_module.create_environment(venv_dir, site_packages=False, clear=False, symlink=False)

        print("* Activating virtual environment [{}]".format(
            venv_dir))  # this is done by prepending python3 path to system path
        os.environ['PATH'] = os.pathsep.join([os.path.join(venv_dir, 'bin'), os.environ['PATH']])

        activate_cmd = f"source {venv_dir}/bin/activate"

        if os.name == 'nt':
            print("* Activating virtual environment on windows [{}]".format(
                venv_dir))  # this is done by prepending python3 path to sytem path

            activate_this = os.path.join(venv_dir, "Scripts", "activate_this.py")
            exec(open(activate_this).read(), {'__file__': activate_this})

            # on Windows you need to use quotes when there are spaces in the path
            activate_cmd = f"\"{os.path.join(venv_dir, 'Scripts', 'activate.bat')}\""
            activate_cmd_ps = os.path.join(venv_dir, 'Scripts', 'Activate.ps1')
            activate_cmd += f"\n Powershell users, please use: \"{activate_cmd_ps}\" \n"

        print(" ")
        print("--------------------------------------------------------------------")
        print( "ATTENTION: Please do not forget to activate the virtual environment by calling: \n"
              f"{activate_cmd} \n"
               "- to deactivate the venv, simply type:\n"
               "deactivate \n")
        print("--------------------------------------------------------------------")
        print(" ")

        return venv_dir

class GitRepo(NamedTuple):
    name: str
    url: str
    branch: str
    develop_branch: str
    setup_files: List[str] = ["."]

    def install(self, update=False, test=False, develop=False):
        if develop:
            branch = self.develop_branch
        else:
            branch = self.branch
        if self.name in os.listdir():
            os.chdir(f"{self.name}")
            call("git pull")
        else:
            print(f"Installing {self.name} from {self.url}/{branch}")
            call(f"git clone {self.url} {self.name}")
            os.chdir(self.name)
            call(f"git checkout {branch}")
            call("git pull")
            for setup_file in self.setup_files:
                call(f"pip install -e {setup_file}")
        if test:
            call('pytest')
        os.chdir("..")

orchestrator_git = GitRepo(
    "orchestrator", "https://gitlab.com/opensourcelab/laborchestrator.git",
    "feature/release_V0_1_draft", "feature/release_V0_2_develop"
)
scheduler_git = GitRepo(
    "scheduler", "https://gitlab.com/opensourcelab/pythonlabscheduler.git",
    "feature/release_V0_1_draft", "feature/release_V0_2_develop",
    setup_files=['.', 'sila_server/.']
)
tools_git = GitRepo(
    "lara_server_tools", "https://gitlab.com/StefanMa/lara-tools.git",
    "main", "develop",
    setup_files=["lara_simulation/.", "utility"]
)
database_git = GitRepo(
    "platform_status_database", "https://gitlab.com/StefanMa/platform_status_db.git",
    "main", "develop"
)
lara_processes_git = GitRepo(
    "lara_implementation", "https://gitlab.com/lara-uni-greifswald/lara-processes.git",
    "feature/release_V0_1_draft", "feature/release_V0_2_develop"
)
pythonlab_git = GitRepo(
    "pythonlab", "https://gitlab.com/opensourcelab/pythonLab.git",
    "feature/release_V0_1_draft", "feature/release_V0_2_develop"
)
device_gits: List[GitRepo] = [
    GitRepo('cytomat', "https://gitlab.com/opensourcelab/devices/incubators_shakers/thermo_cytomat2.git",
                          "develop", "feature/release_V0_2_develop", setup_files=["sila2_server/."]),
    GitRepo("barcode_reader", "https://gitlab.com/opensourcelab/devices/barcodereader/omron-laserscanner-ms-3.git",
                          "develop", "feature/release_V0_2_develop", setup_files=["sila2_server/."]),
    GitRepo("silafied_human", "https://gitlab.com/StefanMa/silafiedhuman.git",
                          "main", 'develop'),
    GitRepo('robotic_arm', "https://gitlab.com/opensourcelab/devices/labrobots/thermo_f5.git",
                        "develop", "feature/release_V0_2_develop", setup_files=["sila2_server/."]),
    GitRepo('agilent_bravo', "https://gitlab.com/opensourcelab/devices/liquidhandler/agilent-vworks.git",
                          "develop", "feature/release_V0_2_develop", setup_files=["sila2_server/."]),
    GitRepo('storage_carousel', "https://gitlab.com/opensourcelab/devices/container_storage/thermo_whitetree_carousel.git",
                             "develop", "feature/release_V0_2_develop", setup_files=["sila2_server/."]),
    GitRepo('reader', "https://gitlab.com/opensourcelab/devices/spectrometer/thermo-skanit6.git",
                   "develop", "feature/release_V0_2_develop", setup_files=["sila2_server/."]),
    GitRepo('centrifuge', "https://gitlab.com/opensourcelab/devices/centrifuges/hettich_rotanta_460r.git",
                       "develop", "feature/release_V0_2_develop", setup_files=["sila2_server/."]),
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


def install_devices(test=False, update=False, develop=False):
    test=False  # not good, yet
    print("Installing sila2 servers for devices")
    os.chdir("devices")
    for repo in device_gits:
        #if update or test or query_yes_no(f"Install {repo.name}?"):
            repo.install(test=test, update=update, develop=develop)
    os.chdir("..")


def initialize():
    print("Testing installation")
    try:
        print(os.listdir())
        os.chdir(database_git.name)
        sys.path.append(os.path.abspath(os.curdir))
        os.chdir('platform_status_db')
        print(os.listdir())
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


def installOnLinux(test=False, update=False, develop=False):
    orchestrator_git.install(test=test, update=update, develop=develop)
    make_dir_structure()
    #if query_yes_no("Install scheduler?"):
    scheduler_git.install(test=test, update=update, develop=develop)
    #if query_yes_no("Install lara-tools (needed to run&visualize simulated devices)?"):
    tools_git.install(test=test, update=update, develop=develop)
    #if query_yes_no("Also install the lara-greifswald specialization?"):
    lara_processes_git.install(test=test, update=update, develop=develop)
    #if query_yes_no("Install device servers?"):
    install_devices(test=test, update=update, develop=develop)
    #if query_yes_no("Install supporting database for orchestrator?"):
    database_git.install(test=test, update=update, develop=develop)
    #if query_yes_no("Install PythonLab process description language? ( It is cool;-) )"):
    pythonlab_git.install(test=test, update=update, develop=develop)


def parse_args():
    parser = ArgumentParser(prog="install_script", description="Guides through the installation of the laborchestrator and its utils")
    parser.add_argument("--init", action="store_true", help="initializes the database", default=False)
    parser.add_argument("--test", action="store_true", help="tests the installation", default=False)
    parser.add_argument("--update", action="store_true", help="updates all installed git repositories", default=False)
    parser.add_argument("--develop", action="store_true", help="uses the latest development version (probably unstable)", default=False)

    return parser.parse_args()


if __name__ == '__main__':
    printWelcomeMessage()
    args = parse_args()
    if args.init:
        initialize()
    else:
        installSiLAVenv()
        installOnLinux(test=args.test, update=args.update, develop=args.develop)

    print("Enjoy!")

