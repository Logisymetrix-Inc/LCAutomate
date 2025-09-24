# Logisymetrix-OpenLCA

* August 25, 2025 - `LCAutomate` name change
* September 5, 2025 - "Simple input data structure" released
* September 19, 2025 - "Data quality and uncertainty calculation", "Meta-data fields" released

## Description
The UBC-Logisymetrix-OpenLCA project currently contains:
* LCAutomate
* olca__patched
* Workbench

### LCAutomate
`LCAutomate` is an automation of process creation and impact assessment calculations within OpenLCA for large numbers of datasets.  We are currently in phase 3 of the automation project: `Automation code` -> `autolca` -> `LCAutomate`.  At the end of phase 3 you will see these features:
* Windows installer
* User interface
* Simple input data structure
* Usable calculation results
* Comprehensive error detection and handling

### Workbench
The workbench will be replaced with the "Usable calculation results" feature.
~~The workbench consists of a main Jupyter notebook and some supporting files.  This notebook can be used to do analysis and visualization of the JSON output from the automation step above.  It is liberally documented.  The nugget there is the flexible ingestion of JSON files into Pandas DataFrames.~~

## Installation and usage
Note that as of September, 2023, UBC-Logisymetrix-OpenLCA is supported only on Windows.

### Requirements
* Windows 10 or higher:
  * see https://www.howtogeek.com/197559/how-to-install-windows-10-on-your-pc/, for example
* Python 3.12 or higher:
* OpenLCA 2.4 or higher
  * see https://www.openlca.org/download/
  * use the installer: `openLCA_Windows_x64.exe`
    * if you already have an older version of openLCA installed, uninstall it first
    * typically, this also means a DB backup and upgrade will be done when you start the new version
  * Note that as of September 5, 2025 all testing is done against OpenLCA 2.5

### Step-by-step installation instructions
#### Install Chocolatey package manager
*Optional: perform this step only if Chocolatey is not already on your system or if you want to update it.*

Chocolatey is a package manager and does a better job of installing packages than directly from the package sites. See https://stackoverflow.com/questions/52578270/install-python-with-cmd-or-powershell
* For UBC users, run the `Make Me Admin` program
  * click the search icon and type "make me admin"
* Open Command Prompt using `Run as Administrator`
  * click the search icon and type "command"
  * Windows will suggest Command Prompt with the `Run as Administrator` option
  * ![Open command prompt](Documentation/images/command-prompt.png)
  * Test if Chocolatey is already installed:
    ```
    choco --version
    ```
* If you get a version number, skip to the next step and install Python
  * note, you could also upgrade: `choco upgrade chocolatey`
* Otherwise, download and install Chocolatey using the following command:
  ```
  @"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))" && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"
  ```
* This command takes some time to complete if Chocolatey has not already been installed

#### Install Python
*Optional: perform this step only if Python is not already on your system or if you want to update it.*

Python is needed on your machine as it is the language of the LCAutomate software.
* As above, open Command Prompt using `Run as Administrator`
* Check if Python is installed using:
  ```
  python --version
  ```
* If if is installed and the version is at least 3.12, go to the next step and install Git Bash
* Otherwise, download and install Python using the following command:
  ```
  choco install -y python3
  ```
* This command also takes some time to complete if the latest Python is not installed on your machine.
* It is possible that you will be instructed to reboot your machine at this point, and you should do so.
* Reopen Command Prompt and type:
  ```
  python --version
  ```
* The response should be something like `Python 3.13.2`
* Sometimes it is necessary to also install the Python package manager `pip`:
  ```
  python -m ensurepip
  ```

#### Install Git Bash
*Optional: perform this step only if Git Bash is not already on your system or if you want to update it.*

Git Bash is a Linux terminal emulator.  LCAutomate is currently supported only within a Linux environment.  Git Bash is not the only Linux emulator, you may use whatever is your favourite.
See https://www.geeksforgeeks.org/how-to-install-git-on-windows-using-chocolatey/.
* Look for the Git Bash application using the search icon and typing "git bash"
* If it is not installed, open Command Prompt using `Run as Administrator`
* Type the following command to install git (which includes Git Bash):
  ```
  choco install -y git.install
  ```
* Allow Windows time to complete this command
* Click the search icon and type "git bash"

#### Download the latest version of the openlca project
* If this is the first time you are using the new `LCAutomate` part of the UBC-Logisymetric-OpenLCA project, please create a folder with a path something like this (call this "*Logisymetrix home*"):
  * note, it does not have to be on the C drive
    ```
    C:\Users\[your user name]\Documents\Projects\Logisymetrix
    ```
* It is not necessary to use the path suggested above, any path will do
* If this is not the first time, back up the openlca-main folder at this location (if it exists - older versions may be called "openlca")
  * backup really means "rename"
* Go to the __[UBC-Logisymetrix-OpenLCA project](https://gitlab.com/logisymetrix-home/openlca)__ GitLab repository
* Click on the `Code` button, then choose `Download source code > zip`
* Unzip `openlca-main.zip` in `Downloads` - this will produce the folder `openlca-main`
* Open this folder and you may find another folder called `openlca-main` here
  * if so, move the inner `openlca-main` folder to *Logisymetrix home*
  * otherwise, move the parent `openlca-main` folder to *Logisymetrix home*

#### Set up LCAutomate
* Open Git Bash
  * *note that Copy and Paste must be done with a right click in Git Bash*
  * *also, editing of command lines cannot be done using the mouse, just with the keyboard*
* Navigate to the openlca-main location:
  * find the "path" to this location in the `File explorer` by clicking on the folder icon in the dropdown at the top left and copying the path using CTRL-C, on Windows 10 it looks like this:
  * ![Get path](Documentation/images/file-path.PNG)
  * then use the `cd` command in Git Bash:
    * type cd ""
    * type the back arrow once to place the cursor between the quotes
    * paste the path between the quotes by right-clicking and selecting Paste:
    * ![Navigate](Documentation/images/navigate.PNG)
* Do the setup:
  ```
  source ./setup.sh
  ```
* It is important to do the setup step, first thing, each time you open a new Git Bash window

### LCAutomate usage
As of September 5, 2025 we are at the stage where `LCAutomate` is still a command-line interface (CLI) but it has a new, simplified input data structure.  The simplification arises from the fact that the automation is now based on "template processes" created within OpenLCA before using `LCAutomate`.  One of the many benefits of this is that now most OpenLCA data and meta-data fields get replicated.

#### Replication of data and meta-data fields
Not all OpenLCA data and meta-data fields are replicated due to limitations of the OpenLCA API and with OpenLCA itself.  For the fields that are replicated (see below), you simply have to change the value in the template process and all processes replicated from it will contain the same fields.  This is in the context of the OpenLCA UI.
##### **These fields are replicated**:
* General Info
  * General Info > General Info
    * Version
    * Tags
  * General Info > Time
    * Start date
    * End date
    * Description
  * General Info > Geography
    * Location
    * Description
  * General Info > Technology
    * Description
  * General Info > Data quality
    * Process schema
    * Data quality entry
    * Flow schema
    * Social schema
* Inputs/Outputs
  * Costs/Revenues
  * Uncertainty
  * Data quality entry
* Documentation
  * Documentation > LCI method
    * Process type
    * LCI method
    * Modelling constants
  * Documentation > Data source information
    * Data completeness
    * Data selection
    * Data treatment
    * Sampling procedure
    * Data collection period
  * Documentation > Sources
  * Documentation > Administrative information
    * Project
    * Intended application
    * Data set owner
    * Data generator
    * Publication
    * Creation data
    * Access and use restrictions
* Parameters
  * Input parameters
  * Dependent parameters
* Allocation
##### **These fields are NOT replicated**
* <span style="color:gray">General Info
  * General Info > General Info
    * Infrastructure process - deprecated</span>
* <span style="color:gray">Inputs/Outputs
  * Avoided waste - this is not saved by OpenLCA
  * Location - this value is inherent to each particular Flow and can be changed directly on the Flow</span>
* <span style="color:gray">Documentation
  * Documentation > Data source information
    * Use advice - is not available in the OpenLCA API
  * Documentation > Reviews - cannot be added to a newly created Process via the API
  * Documentation > Compliance declarations - cannot be added to a newly created Process via the API
  * Documentation > Administrative information
    * Copyright - this value does not get replicated on a newly created Process, even though all other Administrative information is</span>
* <span style="color:gray">Parameters
  * Parameters > Global parameters - cannot be set in the OpenLCA UI</span>
* <span style="color:gray">Social aspects - cannot be set in the OpenLCA UI</span>

* <span style="color:gray">Direct impacts - cannot be set in the OpenLCA UI</span>

#### Simplified input data structure
Input files will all be under a single folder, let's refer to this as the "*Input root folder*".  There must be an Excel spreadsheet called `Processes to be replicated.xlsx`.  The structure of this file is as follows:

##### Processes to be replicated.xlsx
* Note that there is a single sheet in this file which must be called `Main`

| Top-level? | Template process name               | Template process UUID                | Replication base name      | Replication file                                |
| ---        | ---                                 | ---                                  | ---                        | ---                                             |
| x          | Barley production_Template          | 3e65f9db-5c2a-4e29-a695-81edd881b7f1 | Barley production          | Repl...files\Barley production_Replication.xlsx |
|            | Energy use consumption mix_template | 2b92b26c-05b3-466c-b8a9-404fa0b504f3 | Energy use consumption mix | Repl...files\Energy use...mix_Replication.xlsx  |
|            | ...                                 | ...                                  | ...                        | ...                                             |

See [Processes to be replicated.xlsx](https://gitlab.com/logisymetrix-home/openlca/-/blob/test-simplified-input/resources/CRSC_Barley_No_SOC-simplified/Processes%20to%20be%20replicated.xlsx?ref_type=heads) for an example.

##### Rules for `Processes to be replicated.xlsx`:
* Only one top-level process, mark this one with an "x"
* Template processes must already exist in OpenLCA
* The "Replication base name" will be combined with the data column names (found in the replication files, discussed below) to create new processes, product systems and calculation files
* Replication files must exist before running LCAutomate.  Their location in your local file system is given with respect to the *Input root folder*.

##### Replication files
There must be one replication file for each of the template processes listed in `Processes to be replicated.xlsx`.  This is the list of "exchanges" for the process.  The replication file must contain one line for each exchange in the process.  This information can be seen in OpenLCA: Process > Inputs/Outputs.
* Note that there are possibly 3 sheets in a replication file:
  * `Amounts`
  * `Physical Allocations`
  * `DQIs`

##### Replication file > Amounts sheet
Rules for the `Amounts sheet`:
* Currently, the amount in each data column must contain a number.  Use 0.00 to mark amounts that are not/applicable

| Direction | Is reference? | Flow                                     | Description | Category                             | RU 5 | RU 6 | ... | RU 42 |
| ---       | ---           | ---                                      | ---         | ---                                  | ---  | ---  | --- | ---   |
| Input     |               | diesel, burned in agricultural machinery |             | Ecoinvent 3.11...for crop activities | 0.45 | 0.39 | ... | 0.33  |
| Input     |               | electricity, medium voltage              | Alberta     | Ecoinvent 3.11...non-hazardous waste | 0.00 | 0.00 | ... | 0.03  |
| ...       |               | ...                                      | ...         | ...                                  | ...  | ...  | ... | ...   |
| Output    | x             | barley grain                             | ...         | Ecoinvent 3.11...crops and oil seeds | 0.46 | 0.40 | ... | 0.34  |
| ...       |               | ...                                      | ...         | ...                                  | ...  | ...  | ... | ...   |

##### Replication file > Physical allocations sheet
Rules for the `Physical allocations` sheet:
* Physical allocation amounts are added only to applicable exchanges.  Others are left blank.

| Direction | Is reference? | Flow                                     | Description | Category                             | RU 5 | RU 6 | ... | RU 42 |
| ---       | ---           | ---                                      | ---         | ---                                  | ---  | ---  | --- | ---   |
| ...       |               | ...                                      | ...         | ...                                  | ...  | ...  | ... | ...   |
| Output    | x             | barley grain                             | ...         | Ecoinvent 3.11...crops and oil seeds | 0.95 | 0.94 | ... | 0.58  |
| Output    |               | Barley straw                             | ...         | Alliance grant.../Consumption mixes  | 0.05 | 0.06 | ... | 0.42  |
| ...       |               | ...                                      | ...         | ...                                  | ...  | ...  | ... | ...   |

See these examples:
* [Barley production_Replication.xlsx](https://gitlab.com/logisymetrix-home/openlca/-/blob/main/resources/CRSC_Barley_No_SOC-simplified/Replication%20data%20files/Barley%20production_Replication.xlsx?ref_type=heads)
* [Energy use consumption mix_Replication.xlsx](https://gitlab.com/logisymetrix-home/openlca/-/blob/main/resources/CRSC_Barley_No_SOC-simplified/Replication%20data%20files/Energy%20use%20consumption%20mix_Replication.xlsx?ref_type=heads)

##### Replication file > DQIs sheet
Rules for the `DQIs` sheet:
* 6 sub-columns are added for each data column:
  * `Reliability`
  * `Completeness`
  * `Temporal correlation`
  * `Geographical correlation`
  * `Further technological correlation`
  * `Base uncertainty`
* The first 5 are integers from 1 to 5.  The last, `Base uncertainty` is a floating point number.
* See, for example, OpenLCA > Indicators and parameters > Data quality systems > ecoinvent data quality system for a full description
* Data quality indicators (`DQIs`) are added only to applicable exchanges.  Others are left blank.  That is, either all 6 DQI fields are filled or none for all data columns for a particular exchange.

| Direction | Is ref? | Flow      | Desc... | Category     | RU 5 |     |     |     |     |      | RU 6 | ... |
| ---       | ---     | ---       | ---     | ---          | ---  | --- | --- | --- | --- | ---  | ---  | --- |
|           |         |           |         |              | Reliability | Completeness | Temporal correlation | Geographical correlation | Further technological correlation | Base uncertainty | Reliability| ... |
| Input     |         | diesel... |         | Ecoinvent... | 1    | 5   | 5   | 1   | 5   | 1.05 | 1    | ... |
| ...       |         | ...       | ...     | ...          | ...  | ... | ... | ... | ... | ...  | ...  | ... |

See these examples:
* [Barley production_Replication.xlsx](https://gitlab.com/logisymetrix-home/openlca/-/blob/main/resources/CRSC_Barley_No_SOC-simplified/Replication%20data%20files/Barley%20production_Replication.xlsx?ref_type=heads)
* [Energy use consumption mix_Replication.xlsx](https://gitlab.com/logisymetrix-home/openlca/-/blob/main/resources/CRSC_Barley_No_SOC-simplified/Replication%20data%20files/Energy%20use%20consumption%20mix_Replication.xlsx?ref_type=heads)

##### General rules for replication files:
* Direction and Is reference? : these are required as manual input because they cannot be retrieved from the OpenLCA database by LCAutomate
* Flow, Description, Category: these are used to match the replication data from the file with the exchange in the database.  Note that exchanges do not come with UUIDs and the order that LCAutomate is able to retrieve them is not the same as what is displayed in OpenLCA.  Therefore it is necessary to match each line of the replication file to an exchange in the process via (Flow, Description, Category).  Note that in most cases the flow name is sufficient.  However, there are cases where the Flow and Category are the same for multiple exchanges.  These must be differentiated using the Description field.  In a case like this, modify the Description for the exchange in OpenLCA and put this value in the replication file.

#### Step-by-step usage instructions
* Start OpenLCA:
  * right-click appropriate database > Open database
  * Tools > Developer tools > Console
  * Tools > Developer tools > IPC Server > click the `run` button
    * if you get an error here, it could be because you have something running on your machine at port 8080
    * see https://stackoverflow.com/questions/48198/how-do-i-find-out-which-process-is-listening-on-a-tcp-or-udp-port-on-windows

* When necessary, you can get help for the usage of the LCAutomate CLI:
  ```
  LCAutomate -h
  ```
  * which produces:
    ```
    usage: LCAutomate [-h] [-i INPUT_ROOT_FOLDER] [-r] [-c {SIMPLE_CALCULATION,CONTRIBUTION_ANALYSIS,UPSTREAM_ANALYSIS,REGIONALIZED_CALCULATION,MONTE_CARLO_SIMULATION}] [-im IMPACT_ASSESSMENT_METHOD]
                      [-n NUMBER_OF_ITERATIONS]
                      {model,process-hierarchy,product-system,calculation}

    positional arguments:
      {model,process-hierarchy,product-system,calculation}
                            Perform the chosen LCAutomate operation

    options:
      -h, --help            show this help message and exit
      -i, --input-root-folder INPUT_ROOT_FOLDER
                            Root folder for automation
      -r, --restart         Restart this operation, ignoring previous state (default False)
      -c, --calculation-type {SIMPLE_CALCULATION,CONTRIBUTION_ANALYSIS,UPSTREAM_ANALYSIS,REGIONALIZED_CALCULATION,MONTE_CARLO_SIMULATION}
                            Calculation type for the calculation operation (default 'UPSTREAM_ANALYSIS')
      -im, --impact-assessment-method IMPACT_ASSESSMENT_METHOD
                            Impact assessment method for the calculation operation (default 'CML-IA baseline')
      -n, --number-of-iterations NUMBER_OF_ITERATIONS
                            Number of iterations for Monte Carlo simulation (default 10) (ignored for other calculation types)
    ```

* Create model:
  * The process-hierarchy model is based on the template processes, for example:
  * <img src="Documentation/images/Template-processes.PNG"  width="280">
  * In Git Bash, type this command:
    ```
    LCAutomate -i <Input root folder> model
    ```
  * Note that *Input root folder* can be a relative path to the folder (relative to where the command is run) or an absolute path
  * This creates a model of the process-hierarchy and caches the information for the subsequent steps

* Create process-hierarchies:
  * In Git Bash, type this command:
    ```
    LCAutomate -i <Input root folder> process-hierarchy
    ```
  * This produces a large number of replicated processes:
  * <img src="Documentation/images/Replicated-processes.PNG"  width="220">
  * If you look at the exchanges in one of the replicated processes, you should see the amounts substituted in:
  * <img src="Documentation/images/Substituted-amounts.PNG"  width="440">
  * Also, you can see that the correct upstream providers are linked:
  * <img src="Documentation/images/Linked-providers.PNG"  width="700">

* Create product systems:
  * In Git Bash, type this command:
    ```
    LCAutomate -i <Input root folder> product-system
    ```
  * This produces a product system for each of the replicated top-level processes:
  * <img src="Documentation/images/Product-system.PNG"  width="550">

* Do calculations:
  * In Git Bash, type this command:
    ```
    LCAutomate -i <Input root folder> calculation
    ```
  * This produces the JSON files that we are familiar with in the `__calculation__` sub-folder:
  * ![Calculation files](Documentation/images/Calculation-files.PNG)

#### Restarting steps in the process
For all steps but `model`, if you re-run the step it will tell you that the results are already there.  This can save some time.  However, if you run the `model` step, it will invalidate all the previous results.  Also, if you want to restart any step you can add the flag `--restart`.  Example:
```
LCAutomate -i <Input root folder> calculation --restart
```

#### Using different impact assessment methods for calculation
For the `calculation` step, there is now an `--impact-assessment-method` argument.  It defaults to "CML-IA baseline".  You must use the `--restart` flag if you want to change the impact assessment method.  For example:
```
LCAutomate -i <Input root folder> calculation --restart --impact-assessment-method "IPCC 2021 AR6"
```

#### Using different calculation types
Also, in the calculation step, ther is a `--calculation-type` argument.  It defaults to "UPSTREAM_ANALYSIS".  Note that if you choose "MONTE_CARLO_SIMULATION", you need to supply the number of iterations.  This is done via the `--number-of-iterations` argument, which defaults to 10.  It will produce the regular set of results files, one per iteration.  Statistics on these results files is not currently implemented.

#### Testing LCAutomate
*This step is optional*

Some basic testing was added in the 2025-09-05 release.  In order to run these tests, do the following
* In Git Bash, navigate to *Logisymetrix home*/openlca (or wherever the code is located)
* In Git Bash, type these commands:
  ```
  source test/test_suite_runner.sh test/test_suites/model_tests.txt
  ```
  ```
  source test/test_suite_runner.sh test/test_suites/process_hierarchy_tests.txt
  ```
  ```
  source test/test_suite_runner.sh test/test_suites/product_system_tests.txt
  ```
  ```
  source test/test_suite_runner.sh test/test_suites/calculation_tests.txt
  ```
Remember that OpenLCA must be running, the "Alliance Grant_Master Database_For LCAutomate" database must be open and the IPC server must be running.

### Workbench usage
*Note: this will be replaced when the "Usable calculation results" code is released.*

The Logisymetrix-OpenLCA Workbench is written more generally and can work with any JSON files.  This release contains a Workbench Notebook that can be used with conventional egg production analysis as described here.
#### Step-by-step workbench usage instructions
* Run Anaconda Navigator
* launch JupyterLab
* within JupyterLab, navigate to `openlca-main\src\Workbench`
* double-click `ingest-elementary-flows-2024_01_14.ipynb`
* follow the directions therein

# Ideas
These are the various items that have been discussed to date:
1. ~~Add elementary flows to the automation code, currently there are only process flows~~ - 2024-01-21
1. Organize the existing elements into a proper data processing pipeline.  Generalization of data formats and processing steps is required.  For example, there is a need for items like:
    * data cleaning
    * data preparation
    * outlier identification and removal
    * statistical analysis
1. Connect the input of the OpenLCA processing pipeline to the Qualtrics API to access the Qualtrics survey format data.

# Roadmap
This is the actual roadmap:
* ~~Data quality entry and uncertainty calculation~~  - 2025-09-19
* ~~Add remaining data/metadata fields for OpenLCA~~  - 2025-09-19
* Windows installer
* User interface (UI)
* ~~Simple input data structure~~  - 2025-09-05
* Usable calculation results
* Comprehensive error detection and handling
