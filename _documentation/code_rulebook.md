### I: Type Hinting
- All function arguments must be type hinted.
- All functions returns must be type labeled. If they return nothing, they must be labeled with `None`.
- Functions must either return the type they hint at or raise an Error (Returning and raising are mutually exclusive).

- All class attributes must be type hinted, except for inherited attributes which are already type hinted.


### II: Implicit contracts: Fulfill type hints

#### Functions
Passing the correct type in arguments is caller responsibility \
Returning the correct type given correct arguments responsibility of responder 

- Guarantee in every function definition: Returns an object of the type it hints.
- Assume in every function call: Function returns an object of the type it hints.
- Assume in every function definition: Arguments are of the type they are hinted to be.
- Guarantee in every function call: Passed arguments are of the type they are hinted to be.

#### Classes
Init must guarantee fulfilling the type hints after init finish. The attribute types cannot be changed after init is complete.

- Guarantee after `__init__` finished: Every class attribute fulfills its type hint
- Guarantee in every class: Attribute types are never changed
- Assume: Every attribute fulfills its type hint at any point after `__init__`.


### III: Naming (see also: [naming-convention](https://github.com/naming-convention/naming-convention-guides/tree/master/python))
- All functions are named as verbs and classes as nouns.
- Functions that return something are of the format `get_[object]` or `create_[object]` if the function returns the object and also does something else. Ideally, the name of the function should make the type of the returned object apparent already.
- Plural with `object_list`, not `objects`.
- Private attributes should be of the form `_attribute` so that they are properly hidden. \
- Case and spacing conventions:
  - Modules (Python source file): lowercase w/ snake_case, 
  - functions,  lowercase w/ snake_case 
  - classes, everything else: lowercase w/ snake_case.


### IV: Making changes
- Any change that you make has to either not influence the contract of that section of code or the changes to the contract have to be carried through upstream.


### V: Debugging
- Trace from the entry point.
- Check submodule contracts.


### VI: Other

- Pass arguments only by keyword.
- Nesting: Max indentation level === 3

- No relative imports. Give the full path; otherwise, it will crash when importing the module from somewhere else. For example, don't do:
  ```
  python from Directive import Directive
  ```
  ,instead do:
   ```
   from s1_Directive.Directive import Directive
   ```