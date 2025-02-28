from dataclasses import dataclass


@dataclass
class Node:
    content : str


@dataclass
class Edge:
    content : str
    source : Node
    target : Node

@dataclass
class Graph:
    nodes : list[Node]
    edges : list[Edge]

    