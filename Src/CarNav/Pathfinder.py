from typing import Union, List, Tuple
from heapq import heapify, heappush, heappop

from Mapp import Mapp
from CMath import Math, Position

class Pathfinder:

    @staticmethod
    def a_star(
            mapp: Mapp, starting: Position, target: Position
            ) -> List[Position]:
        
        num_rows = mapp.num_rows
        class Node:
            def __init__(
                    self, x: int, y:int, heading: float = 0, prev_node: Union["Node", None] = None
                    ) -> None:
                self.x = x
                self.y = y
                self.heading = heading # 0, 45, 90, 135, 180, 225, 270, 315, 0
                self.prev_node = prev_node
                self.angle_score = 0
                self.hscore = 0
                self.gscore = 0
                self.fscore = 0

            def __eq__(self, other: "Node") -> bool:
                return (self.x == other.x and self.y == other.y)

            def __gt__(self, other: "Node") -> bool:
                return (self.fscore > other.fscore)
            
            def __lt__(self, other: "Node") -> bool:
                return not (self.fscore > other.fscore or self.fscore == other.fscore)
            
            def calc_scores(
                    self, current_node: "Node", target_node: "Node"
                    ) -> "Node":             
                # current_node is the node we are coming from and self is the node
                # we are potentially moving to.
                self.angle_score = abs(Math.calc_turning_angle(
                    Position(current_node.x, current_node.y, current_node.heading),
                    Position(self.x, self.y),
                    should_round = True
                    )) / 45
                self.hscore = self.get_distance(target_node)
                self.gscore = current_node.gscore + self.get_distance(current_node) #+ self.angle_score
                self.fscore = self.gscore + self.hscore + self.angle_score
                return self

            def get_distance(self, target_node: "Node") -> int:
                return (self.x - target_node.x)**2 + (self.y - target_node.y)**2

            @property
            def key(self) -> int:
                return int(float(self.y) * num_rows + float(self.x) + self.heading)

        def find_path(end_node: Node) -> List[Position]:
            path = [Position(end_node.x, end_node.y)]
            current_node = end_node.prev_node
            while current_node:
                path.append(Position(current_node.x, current_node.y))
                current_node = current_node.prev_node
            path.reverse()
            return path

        target_node = Node(int(target.x), int(target.y)) 
        start_x, start_y, start_heading = starting
        starting_node = Node(int(start_x), int(start_y), start_heading) 
        # x, y, f, g, h
        # g = current.g + distance(neighbor, current)
        # h = distance(current, target)
        # f = g + h
        open_list = [starting_node]
        heapify(open_list)
        open_set = {starting_node.key : 0.0}
        closed_set = set()
        max_steps_start = 1_000
        max_steps = max_steps_start
        while len(open_list) > 0 and max_steps > 0:
            current_node = heappop(open_list)
            if current_node == target_node:
                return find_path(current_node)
            closed_set.add(current_node.key)
            for neig_x, neig_y in mapp.get_open_neighbors(current_node.x, current_node.y):
                neigh_heading = Math.calc_new_heading_from_position(
                    Position(current_node.x, current_node.y, current_node.heading), 
                    Position(neig_x, neig_y)
                    )
                neigh_node = Node(
                    int(neig_x),
                    int(neig_y),
                    neigh_heading,
                    current_node    
                    ).calc_scores(current_node, target_node)
                
                if neigh_node.key in closed_set:
                    continue  
                existing_gscore = open_set.get(neigh_node.key, None)
                if existing_gscore and neigh_node.gscore > existing_gscore:
                        continue
                heappush(open_list, neigh_node)
                open_set[neigh_node.key] = neigh_node.gscore
            max_steps -= 1
        print(f"Failed to find path within maximum steps: {max_steps_start}")
        return []