from dataclasses import dataclass

from engine.l1_agents import Task


@dataclass
class Node:
    content : str
    max_steps : int
    task : Task

@dataclass
class Edge:
    content : str
    source : Node
    target : Node

@dataclass
class Workflow:
    start_node: Node
    nodes : list[Node]
    edges : list[Edge]

