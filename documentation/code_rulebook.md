### I: Type Hinting
- All function arguments must be type hinted.
- All functions returns must be type labeled. If they return nothing, they must be labeled with `None`.
- Functions must either return the type they hint at or raise an Error (Returning and raising are mutually exclusive).
- All class attributes must be type hinted, except for inherited attributes which are already type hinted.


### II: Implicit contracts: Fulfill type hints

#### Functions
Passing the correct type in arguments is caller responsibility \
Returning the correct type given correct arguments is responsibility of responder (callee) 

- Guarantee in every function definition: Returns an object of the type it hints.
- Assume in every function call: Function returns an object of the type it hints.
- Assume in every function definition: Arguments are of the type they are hinted to be.
- Guarantee in every function call: Passed arguments are of the type they are hinted to be

#### Classes
Init must guarantee fulfilling the type hints after init finish. The attribute types cannot be changed after init is complete.

- Guarantee after `__init__` finished: Every class attribute fulfills its type hint
- Guarantee in every class: Attribute types are never changed
- Assume: Every attribute fulfills its type hint at any point after `__init__`.


### III: Naming (see also: [naming-convention](https://github.com/naming-convention/naming-convention-guides/tree/master/python))
- All functions are named as verbs and classes as nouns.
- Functions that return something are of the format `get_[object]` or if the function initializes and returns the object `create_[object]` or  `make_[object]` for classmethods \
- - Apart from `create_[object]` methods which both set and get, getters don't set and have absolutely no effect beyond their return statement \ 
and possibly debug prints
- However: The `set_[object]` syntax is entirely optional
- Plural with `object_list`, not `objects`.
- Private attributes should be of the form `_attribute` so that they are properly hidden. \
- Case and spacing conventions:
  - Modules (Python source file): lowercase w/ snake_case, 
  - functions,  lowercase w/ snake_case 
  - classes, everything else: lowercase w/ snake_case.


### IV: Downward depenency arrangement

- Wherever possible apply downward reliance arrangement: x <- y == x depends on y == x above of y in directory/file
- I.e.: Highest level modules/submodules first then the methods they depend on below
- The dependency direction is upwards i.e. further along dependency stream == upwards in directory/file
- Analogy: The rest of a house of cards can still stand if you take away its uppermost layer. But if you so much as nudge one
of the cards on the lower level the whole thing might collapse. Software works in the same way and their arrangement will reflect that.
  

### V: Other

- Pass arguments only by keyword
- Minimal exposure/Maximal encapsulation: Keep the API between modules as minimal as possible
- Nesting: Max indentation level === 3
- Source file length: Max ~200 loc, Multiple dependent classes within single file discouraged
- Classmethods always return class instances
- Commit messages header: Introduced, Extended, Rewrote
- Logging: \[Debug\] for control flow information; \[Error\] for Exceptions or unintended output, error message includes Exception

- No relative imports. Give the full path; otherwise, it will crash when importing the module from somewhere else. For example, don't do:
  ```
  python from Directive import Directive
  ```
  ,instead do:
   ```
   from s1_Directive.Directive import Directive
   ```