## Overview
The Lotus framework facilitates interaction with the computer and the internet through natural language.
For more information see the "Wiki" section on the [Project management page](https://furtive-point-c71.notion.site/GPT-pyWrite-Lotus-7a44993ddb1b42edbba4d6275d7c9628?pvs=4).

<p align="center">
  <img src="https://github.com/Somerandomguy10111/webapp/blob/master/assets/images/logo.jpg" alt="Logo" width="200">
  <br>
  <em> Nelumbo Nucifera the most widely known Lotus Flower</em>
</p>

## Setup and usage for Ubuntu 22.04

Use the launch script in the root of the repo:
```
bash launch.sh --setup # For first time launch
bash launch.sh         # Standard launch
```

## Code rulebook

### I: Implicit contracts: Guarantee/Assume type hints

#### For Functions

Arguments: All function arguments must be type hinted.

- Passing the correct type in arguments is caller responsibility
  - Guarantee in every function call: Passed arguments are of the type they are hinted to be
  - Assume in every function definition: Arguments are of the type they are hinted to be.


Returns: Functions must either return the type they hint at or raise an Error (Returning and raising are mutually exclusive).

- All functions returns must be type labeled if they return anything but None
  - Functions without a type hint are implicitly understood as returning None
  - Functions that return cannot be explictly type hinted

- Return : Returning the correct type given correct arguments is responsibility of responder (callee)
  - Guarantee in every function definition: Returns an object of the type it hints.
  - Assume in every function call: Function returns an object of the type it hints.
  
#### For classes
All class attributes must be type hinted. Init must guarantee fulfilling the type hints after init finish and that type guaranteed must
be upheld at any point after.

- Guarantee at any point after `__init__` finished: Every class attribute fulfills its type hint 
- Assume at any point after `__init__`: Every attribute fulfills its type hint at any point after `__init__`.


### II: Naming (see also: [python-naming-convention](https://github.com/naming-convention/naming-convention-guides/tree/master/python))
- All functions are named as verbs and classes as nouns.
- Functions that return something are of the format `get_[object]` or if the function initializes and returns the object `create_[object]` or  `make_[object]`
- Getter methods/functions i.e. all functions prefixed with `get` do absolutely nothing except return and possibly print debug info
- Case and spacing conventions:
  - Modules (Python source file): lowercase w/ snake_case, 
  - functions,  lowercase w/ snake_case 
  - classes, everything else: lowercase w/ snake_case.
- Plural perfererentially `object_list`, not `objects`.
- Private attributes should be of the form `_attribute` so that they are properly hidden.


### III: Downward depenency arrangement

- Wherever possible arrange modules so that dependency/reference relation (y depends on x) points downward
- I.e. : y depends on x == y -> x == x is placed below y
- I.e.: Highest level modules/submodules first then the methods they depend on below
- Analogy: Software is a house of cards
  - The upper level modules 'rest' on the lower level modules, not the other way around
  - The rest of a house of cards can still stand if you take away its uppermost layer. But if you so much as nudge one
  of the cards on the lower level the whole thing might collapse. Software works in the same way and their arrangement will reflect that.
- Apply this both for text within a file and files within a directory

### IV: Imports
- **Intra-source dir imports**: Like this
```
from .this_file import that_class
```
- **Inter-source dir imports**: Like this
```
from [module] import that_class
```
This requires making use of init files to specify which objects from the module to expose
- **Import consolidation**: Consolidate imports from a single module in a single line if possible
- **Hierachical init files**:
  - The init file of module without subfolders should import individual symbols from files
  ```
  from .run import RUN
  from .file_io import FILE_IO
  from .mandate_ops import INITIALIZE_MANDATE, UPDATE_MANDATE
  from .search import SEARCH
  ```
  -The init files of modules with subdirectories should instead import the directories, but check that
no name collisions occur at runtime
```
from pyutils import check_subdir_namecollsions
check_subdir_namecollsions()

from .m0_toolbox import *
from .tool import Tool
```

- **Arrange imports by nearness**: First import packages, then own code arranged by how far away nearest common ancestor is
  - Seperate intra-dir imports by an empty line

### V: Other
- **kwargs only**: Pass arguments only by keyword
- **Minimal exposure/Maximal encapsulation**: Keep the API between modules as minimal as possible
- **Minimal nesting**: Max indentation level === 3
- **Small directories**: The ideal amount of elements in any given source dir, elements being either files or folders, is 2-3
, 4 is okay too and 5 is the upper limit 
- **Short Source file length**: Max ~200 loc, Ideally < 120 loc
- **Use logging**: Use logging instead of print statements
- **Use enumerate**: Use enumerate instead of range(len(...))