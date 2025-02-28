from dataclasses import dataclass

from engine.l1_agents import Task


@dataclass
class Node:
    content : str
    task : Task


@dataclass
class Edge:
    content : str
    source : Node
    target : Node

@dataclass
class Workflow:
    nodes : list[Node]
    edges : list[Edge]

