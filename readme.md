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

## Codebase

<details>
<summary>rulebook</summary>


### I: Implicit contracts: Guarantee/Assume type hints

#### For Functions

Arguments: All function arguments must be type hinted.

- Passing the correct type in arguments is caller responsibility
  - Guarantee in every function call: Passed arguments are of the type they are hinted to be
  - Assume in every function definition: Arguments are of the type they are hinted to be.

Returns: Functions must either return the type they hint at or raise an Error (Returning and raising are mutually exclusive).

- All functions returns must be type labeled if they return anything but None; Functions without a type hint are implicitly understood as returning None
- Return : Returning the correct type, given correct arguments is responsibility of callee
  - Guarantee in every function definition: Returns an object of the type it hints or raises Exception
  - Assume in every function call: Function returns an object of the type it hints or raises Exception
  
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
  - classes, everything else: CamelCase


### III: Downward depenency arrangement

- Wherever possible arrange modules so that dependency/reference relation (y depends on x) points downward i.e. if y depends on x then  x is placed below y
- I.e.: Highest level modules/submodules first then the methods they depend on below; In doing so, minimize the vertical distance between modules
- Apply this both for text within a file and files within a directory

### IV: Imports

- Style
```
from .this_file import that_class ## Intra source-dir imports
from [module] import that_class   ## Inter source-dir imports using __init__
```
This requires making use of init files to specify which objects from the module to expose

- **Import consolidation**: Consolidate imports from a single module in a single line if possible
- **Hierachical __init_**: Source directories are stacked by importing everything:
```
from [source_dir1] import *
from [source_dir2] import *
from pyutils import check_subdir_namecollsions
check_subdir_namecollsions()
```
Stacked imports must be checked for name_collsions, since that can't be detected natively by the IDE
- **Ordering**: First import stdlib/pypi packages, then own code arranged by how far away nearest common ancestor

### V: Other
- **kwargs only**: Pass arguments only by keyword
- **minimal nesting**: Max indentation level === 3
- **small directories**: Each dir ideally contains only 2-4 files/folders; max 5 files/folders
, 4 is okay too and 5 is the upper limit 
- **Short Source file length**: Max ~200 loc, Ideally < 120 loc
- **Short function length**: Max ~30 loc, ideally <= 15 loc
- **Pythonic patterns**:
	- logging package or custom logging functions instead of print
	- enumerate instead of range(len(...))
	- use dict and list comprehension in favour of more explicit syntax

</details>

<details>
<summary>dev guide</summary>

### Interface/Implementation segregation
- Plural perfererentially `object_list`, not `objects`.
- Private attributes should be of the form `_attribute` so that they are properly hidden.
- **Minimal exposure/Maximal encapsulation**: Keep the API between modules as minimal as possible


### Testing suite
- 


### Architecture
- Hierachy
	- Organize the program into levels of hierachy, follwing a stepdown rule: Each function is composed only of statements from the next lower level of abstraction; 
	- Mixing levels of abstraction should be avoided


</details>

