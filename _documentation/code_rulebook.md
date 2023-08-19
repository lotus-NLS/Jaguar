# TODO: Code rulebook as md, can link other md also
# TODO: Top level readme

I: Functions
-> All function arguments must be type hinted
-> All functions must be type labeled. If they return nothing they must be labeled with None
-> Functions must either return the type the hint at or raise an Error (Returning and raising are mutually exclusive)
-> Pass arguments only by keyword

II: Classes
-> All class attributes must be type hinted, except for inherited attributes which are already type hinted


III: Implicit contracts: Fulfill type hints
-> Gurantee in every init: Every class attribute fulfills its type hint at any point after init
-> Assume in every class instance scope: Every attribute fulfills its type hint at any point after init
-> Guarantee in every function definition: Returns object of type it hints
-> Assume in every function call: Function returns object of type it hints
-> Assume in every function definition: Arguments are of the type they are hinted to be
-> Guarantee in every function call: Passed arguments are of the type they are hinted to be


IV: Naming (see also: https://github.com/naming-convention/naming-convention-guides/tree/master/python)
-> All functions are named as verbs and classes as nouns
-> Functions that return something are of the format get_[object].
Ideally the name of the function should make the type of the returned object apparent already
-> Plural with "object_list" not "objects"
-> Private attributes should be of the form "_[attribute]" so that they are properly hidden
-> Modules (python source file): lowercase w/ snake_case
   functions                    : lowercase w/ snake_case,
   Classes                      : PascalCase
   everything else              : lowercase w/ snake_case


V: Making changes
-> Any change that you make has to either not influence the contract of that section of code or
the changes to the contract have to be carried through upstream




VI: Debugging
-> Trace from entry point
-> Check submodule contracts


VII: Other
-> No relative imports. Give full path, otherwise it will crash when importing the module from somewhere else
e.g. don't do:
from Directive import Directive
but
from s1_Directive.Directive import Directive