# Lab Automation



## LabOrchestrator environment guide

## Description
This package only consist of an installation script for several packages
in [opensoucelab](https://gitlab.com/opensourcelab/) which are intended to work
together with the [laborchestrator](https://gitlab.com/opensourcelab/laborchestrator) and documentation for how to use them. 
These packages contain a [scheduler](https://gitlab.com/opensourcelab/pythonlabscheduler),
a supporting [database](https://gitlab.com/StefanMa/platform_status_db),
some (LARA-specialized) [utility tools](https://gitlab.com/StefanMa/lara-tools) for starting sila servers, creating simulations and visualization,
a process description language named [PythonLab](https://gitlab.com/opensourcelab/pythonLab),
a collection of [SiLA-servers](https://gitlab.com/opensourcelab/devices) for certain lab devices (including simulations)
and finally a [specialization](https://gitlab.com/lara-uni-greifswald/lara-processes) of the laborchestrator for the Greifswald robot platform LARA

## Badges
On some READMEs, you may see small images that convey metadata, such as whether all the tests are passing for the project. You can use Shields to add some to your README. Many services also have instructions for adding a badge.

## Visuals
Depending on what you are making, it can be a good idea to include screenshots or even a video (you'll frequently see GIFs rather than actual videos). Tools like ttygif can help, but check out Asciinema for a more sophisticated method.

## Installation
0.  You need to have at least **python3.8** and **git** installed on your computer

1. Clone this repository, navigate into the folder and change to the develop branch. For example via Console/Powershell with
```bash
    git clone https://gitlab.com/opensourcelab/openlab-site/lab-automation.git
```
```bash
    cd lab-automation
```
```bash
    git checkout develop
```

2.  To install all packages, simply run the following command. You could add      `--develop` to install the (possibly unstable) development version

    ```bash
        python3.8 full_install_script.py
    ```

    This will guide you through the installation process. We strongly recommend to pick the virtual-environment option. 

3. Activate the newly created environment by executing

    ```bash
        source venv/lab_automation/bin/activate
    ``` 

4. Now (in case, you installed the platform_status_db), you should run 

    ```bash
        python full_install_script.py --init
    ``` 

    to initialize the django database and create admin  credentials. You will be asked a few options.
5. With 

    ```bash
        python3.8 full_install_script.py --test
    ```

you can run the automatic pytest tests for most packages.

5. At any point in time, you can update your installation with 

```bash
    python3.8 full_install_script.py --update
```

## Usage

The orchestrator can work without PythonLab and the database,
but to understand the software, it's recommended to use the greifswald-specialization, which uses both.

 - For a quickstart guide go [here](/docs/quickstart.md).

 - For a more detailed documentation of the _laborchestrator_ GUI go [here](/docs/usage.rst)

 - Use examples liberally, and show the expected output if you can. It's helpful to have inline the smallest example of usage that you can demonstrate, while providing links to more sophisticated examples if they are too long to reasonably include in the README.

## Support
For support, feel free to contact maaks@uni-greifswald.de. 

## Roadmap
If you have ideas for releases in the future, it is a good idea to list them in the README.

## Contributing
State if you are open to contributions and what your requirements are for accepting them.

For people who want to make changes to your project, it's helpful to have some documentation on how to get started. Perhaps there is a script that they should run or some environment variables that they need to set. Make these steps explicit. These instructions could also be useful to your future self.

You can also document commands to lint the code or run tests. These steps help to ensure high code quality and reduce the likelihood that the changes inadvertently break something. Having instructions for running tests is especially helpful if it requires external setup, such as starting a Selenium server for testing in a browser.

## Authors and acknowledgment
Maintained by Stefan Maak and Mark Dörr of the workinggroup of Prof. Bornscheuer in Uni Greifswald.

## License
MIT Licence.

## Project status
The project is still in an experimental state, but improves continuously.
We have unit tests and use the software is used to run experiments, 
but there are still lots of changes happening and bugs being discovered. 
