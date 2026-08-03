# ADS Python API Probe

Generated: 2026-08-03T01:13:20
Python: `D:\Hardware\Keysight\ADS2026_Update1\tools\python\python.exe`
Keywords: `simulate, simulation, analysis, emsetup, setup, rfpro, xxpro, run`

## Keyword Child Modules

### `keysight.ads.emtools`
- `keysight.ads.emtools._setup_environment`
- `keysight.ads.emtools._setup_support`

## API Hits

### `keysight.ads.emtools`

| Object | Kind | Signature | Doc |
|---|---|---|---|
| `keysight.ads.emtools.EmproSetup` | class | `(filepath__or__empro_lcv_tuple: str \| tuple \| None = None) -> 'EmproSetup'` | Class to work on the EM view setup. |
| `keysight.ads.emtools.EmproSetup.default_filename` | function | `(self) -> str` | Returns the default EM view setup file name. |
| `keysight.ads.emtools.EmproSetup.design_refs` | property | `` | The design references -- layout and substrate -- of the EM view setup. :getter: Returns this setup's design references. :setter: Sets this setup's design references. |
| `keysight.ads.emtools.EmproSetup.tool` | property | `` | The tool for this EM view setup. :getter: Returns this setup's tool. :setter: Sets this setup's tool. |
| `keysight.ads.emtools.EmproSetup.write` | function | `(self, filepath_or_lcv: str \| tuple) -> None` | Writes the EM view setup data. Parameters ---------- filepath_or_lcv Either provide a tuple of strings -- library name, cell name and view name -- or provide the view's setup filepath. |
| `keysight.ads.emtools.find_emsetup_view_name` | function | `(layout_lcv: tuple[str, str, str]) -> str` | Find the active EM Setup view name from the Layout view. Parameters ---------- layout_lcv Tuple containing the library name, cell name and the layout view name. Returns ------- The EM Setup view name Raises ------ Run... |
| `keysight.ads.emtools.get_substrate_info` | function | `(emsetup_lcv: tuple[str, str, str]) -> tuple[str, str]` | Get the substrate info of the EM Setup view. Parameters ---------- emsetup_lcv Tuple containing the library name, cell name and the EM Setup view name. Returns ------- Tuple containing the substrate library name and t... |

### `keysight.edatoolbox.ads`

| Object | Kind | Signature | Doc |
|---|---|---|---|
| `keysight.edatoolbox.ads.ADS.import_brd` | function | `(self, workspace: str, brdFile: str)` | Import a brd file into an existing workspace. Parameters ---------- workspace : str Path to an existing workspace. brdFile : str Path to a brd file. Raises ------ AssertionError Workspace does not exist. RuntimeError ... |
| `keysight.edatoolbox.ads.ADSNotFound` | class | `` | Unspecified run-time error. |
| `keysight.edatoolbox.ads.CircuitSimulator.run` | function | `(self, commandline: Union[str, List[str]], working_dir: str = None)` | Run the circuit simulator with given commandline, for instance '-h' Parameters ---------- commandline: Union[str, List[str]] Either a well-formed string or a list of strings (=recommended). The list of strings is then... |
| `keysight.edatoolbox.ads.CircuitSimulator.run_netlist` | function | `(self, netlist: str, output_dir: str, working_dir: str = None, output_file: str = None, netlist_file: str = None, rel_data_dir: str = None, dataset_name: str = None, verilog_dir: str = None, pdk_dirs: List[str] = None, extra_args: List[str] = None)` | Run the provided netlist through the circuit simulator. Parameters ---------- netlist: str The netlist to run output_dir: str Where the data should be produced working_dir: str The optional working dir where the circu... |
| `keysight.edatoolbox.ads.DataDisplay.run_dds` | function | `(self, data_dir=None, dataset=None, datadisplay_file=None)` | Run ADS DataDisplay with optionally a dataset and dds-file. Parameters ---------- data_dir: str working directory where to run DataDisplay dataset: str name of the dataset file to load by default datadisplay_file: str... |
| `keysight.edatoolbox.ads.execute` | function | `(cmd, output_file, error_file=-2, working_directory=None, **kwargs)` | Run command with arguments. |
| `keysight.edatoolbox.ads.ExecutionError` | class | `(returncode, cmd, output=None, stderr=None)` | Raised when run() is called with check=True and the process returns a non-zero exit status. Attributes: cmd, returncode, stdout, stderr, output |
| `keysight.edatoolbox.ads.LicenseError` | class | `(error_string)` | Unspecified run-time error. |
| `keysight.edatoolbox.ads.OdbImportOptions.step_index` | int | `` | int([x]) -> integer int(x, base=10) -> integer Convert a number or string to an integer, or return 0 if no arguments are given. If x is a number, return x.__int__(). For floating-point numbers, this truncates towards ... |
| `keysight.edatoolbox.ads.SubstrateStack.BAL_NUM` | int | `` | int([x]) -> integer int(x, base=10) -> integer Convert a number or string to an integer, or return 0 if no arguments are given. If x is a number, return x.__int__(). For floating-point numbers, this truncates towards ... |

### `keysight.edatoolbox.multi_python`

| Object | Kind | Signature | Doc |
|---|---|---|---|
| `keysight.edatoolbox.multi_python.py_xxpro_multiprocess_execute` | function | `(fn, *args, **kwargs)` | * This function is deprecated * A function that lets a method fn be executed in a separate process, with the Python versions of xxPro. The call is synchronous, return values are ignored. >>> def foo(x): import empro; ... |
| `keysight.edatoolbox.multi_python.xxpro_context` | function | `(python_xxpro_location=None)` | Create a context manager that will yield an object to which functions can be sent to be executed in a separate process with the Python version of EMPro/RFPro/SIPro. Args: python_xxpro_location (str): The location of t... |

### `keysight.edatoolbox.xxpro`

| Object | Kind | Signature | Doc |
|---|---|---|---|
| `keysight.edatoolbox.xxpro.ADSNotFound` | class | `` | Unspecified run-time error. |
| `keysight.edatoolbox.xxpro.ADSNotFound.add_note` | method_descriptor | `(self, object, /)` | Exception.add_note(note) -- add a note to the exception |
| `keysight.edatoolbox.xxpro.ADSNotFound.args` | getset_descriptor | `` |  |
| `keysight.edatoolbox.xxpro.ADSNotFound.with_traceback` | method_descriptor | `(self, object, /)` | Exception.with_traceback(tb) -- set self.__traceback__ to tb and return self. |
| `keysight.edatoolbox.xxpro.get_ads_location` | function | `() -> str` | Returns the location of the latest installed ADS. |
| `keysight.edatoolbox.xxpro.get_python_xxpro_location` | function | `(from_ads=True) -> str` | Returns the location of the python installed with xxPro. Parameters ---------- from_ads : bool, default=True If True get xxPro from ADS install folder, otherwise look for EMPROHOME environment variable. |
| `keysight.edatoolbox.xxpro.get_xxpro_location` | function | `(from_ads=True) -> str` | Returns the location of the latest installed xxPro. Parameters ---------- from_ads : bool, default=True If True get xxPro from ADS install folder, otherwise look for EMPROHOME environment variable. |
| `keysight.edatoolbox.xxpro.LibraryCellView` | class | `(library: str, cell: str, view: str) -> None` | LibraryCellView(library: str, cell: str, view: str) |
| `keysight.edatoolbox.xxpro.load_pro_view` | function | `(xxpro_lcv: keysight.edatoolbox.ads.LibraryCellView)` | Load an xxpro LibraryCellView into the empro.activeProject. Parameters ---------- xxpro_lcv : LibraryCellView An xxpro LibraryCellView object. Raises ------ ImportError Failed to import empro module. |
| `keysight.edatoolbox.xxpro.os` | module | `` | OS routines for NT or Posix depending on what system we're on. This exports: - all functions from posix or nt, e.g. unlink, stat, etc. - os.path is either posixpath or ntpath - os.name is either 'posix' or 'nt' - os.c... |
| `keysight.edatoolbox.xxpro.re` | module | `` | Support for regular expressions (RE). This module provides regular expression matching operations similar to those found in Perl. It supports both 8-bit and Unicode strings; both the pattern and the strings being proc... |
| `keysight.edatoolbox.xxpro.subprocess` | module | `` | Subprocesses with accessible I/O streams This module allows you to spawn processes, connect to their input/output/error pipes, and obtain their return codes. For a complete description of this module see the Python do... |
| `keysight.edatoolbox.xxpro.sys` | module | `` | This module provides access to some objects used or maintained by the interpreter and to functions that interact strongly with the interpreter. Dynamic objects: argv -- command line arguments; argv[0] is the script pa... |
| `keysight.edatoolbox.xxpro.use_workspace` | function | `(workspace: str)` | Tell xxpro what workspace to use. Parameters ---------- workspace: str The full path of the workspace. |
| `keysight.edatoolbox.xxpro.XXProNotFound` | class | `` | Raise if cannot find SI/PI/RFPro. |
| `keysight.edatoolbox.xxpro.XXProNotFound.add_note` | method_descriptor | `(self, object, /)` | Exception.add_note(note) -- add a note to the exception |
| `keysight.edatoolbox.xxpro.XXProNotFound.args` | getset_descriptor | `` |  |
| `keysight.edatoolbox.xxpro.XXProNotFound.with_traceback` | method_descriptor | `(self, object, /)` | Exception.with_traceback(tb) -- set self.__traceback__ to tb and return self. |
