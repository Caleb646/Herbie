from typing import Union
from heapq import heapify, heappush, heappop

from Mapp import Mapp

class Pathfinder:

    @staticmethod
    def a_star(
            mapp: Mapp, starting: tuple[int, int], target: tuple[int, int]
            ) -> list[tuple[int, int]]:
        
        num_rows = mapp.num_rows
        class Node:
            def __init__(
                    self, x: int, y:int, prev_node: Union["Node", None] = None
                    ) -> None:
                self.x = x
                self.y = y
                self.prev_node = prev_node
                self.hscore = 0
                self.gscore = 0
                self.fscore = 0

            def __eq__(self, onode: "Node") -> bool:
                return (self.x == onode.x and self.y == onode.y)

            def __gt__(self, other: "Node") -> bool:
                return (self.fscore > other.fscore)
            
            def __lt__(self, other: "Node") -> bool:
                return not (self.fscore > other.fscore or self.fscore == other.fscore)
            
            def calc_scores(
                    self, current_node: "Node", target_node: "Node"
                    ) -> "Node":
                self.hscore = self.get_distance(target_node)
                self.gscore = current_node.gscore + self.get_distance(current_node)
                self.fscore = self.gscore + self.hscore
                return self

            def get_distance(self, target_node: "Node") -> int:
                return (self.x - target_node.x)**2 + (self.y - target_node.y)**2

            @property
            def key(self) -> int:
                return self.y * num_rows + self.x

        def find_path(end_node: Node) -> list[tuple[int, int]]:
            path = [(end_node.x, end_node.y)]
            current_node = end_node.prev_node
            while current_node:
                path.append((current_node.x, current_node.y))
                current_node = current_node.prev_node
            path.reverse()
            return path

        target_node = Node(target[0], target[1])
        start_x, start_y = starting
        starting_node = Node(start_x, start_y)
        
        # x, y, f, g, h
        # g = current.g + distance(neighbor, current)
        # h = distance(current, target)
        # f = g + h
        open_list = [starting_node]
        heapify(open_list)
        #open_list = PriorityQueue()
        #open_list.put((0, starting_node))
        open_set = {starting_node.key : 0.0}
        closed_set = set()
        max_steps = 100_000
        #self.print_position()
        while len(open_list) > 0 and max_steps > 0:
        #while open_list.not_empty and max_steps > 0:
            #priority, current_node = open_list.get(block=False)
            current_node = heappop(open_list)
            if current_node == target_node:
                print("Found new path")
                return find_path(current_node)
            closed_set.add(current_node.key)
            for neig_x, neig_y in mapp.get_open_neighbors(current_node.x, current_node.y):
                neigh_node = Node(neig_x, neig_y, current_node).calc_scores(current_node, target_node)
                if neigh_node.key in closed_set:
                    continue  
                existing_gscore = open_set.get(neigh_node.key, None)
                if existing_gscore and neigh_node.gscore > existing_gscore:
                        continue
                #open_list.put((neigh_node.fscore, neigh_node))
                heappush(open_list, neigh_node)
                open_set[neigh_node.key] = neigh_node.gscore
            max_steps -= 1
        return []