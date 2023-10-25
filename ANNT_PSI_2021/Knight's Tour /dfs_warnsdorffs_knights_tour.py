from collections import defaultdict
import os
from typing import List, Tuple, Optional
from plot_knights_tour import plot_knight_tour
import argparse

MOVE_OFFSETS = (
    (-1, -2),
    (1, -2),
    (-2, -1),
    (2, -1),
    (-2, 1),
    (2, 1),
    (-1, 2),
    (1, 2),
)

def add_edge(graph, vertex_a, vertex_b):
    """
    Add an edge to the graph between vertex_a and vertex_b.
    
    Parameters:
        - graph (dict): The graph to which the edge should be added.
        - vertex_a (tuple): One vertex of the edge.
        - vertex_b (tuple): The other vertex of the edge.
    """
    graph[vertex_a].add(vertex_b)
    graph[vertex_b].add(vertex_a)

def build_graph(board_size: int) -> defaultdict:
    """
    Construct a graph based on a chessboard of given size.
    
    Parameters:
        - board_size (int): Size of the side of the square chessboard.
        
    Returns:
        - defaultdict: Graph representing legal moves on the chessboard.
    """
    graph = defaultdict(set)
    for row in range(board_size):
        for col in range(board_size):
            for to_row, to_col in legal_moves_from(row, col, board_size):
                add_edge(graph, (row, col), (to_row, to_col))
    return graph

def legal_moves_from(row: int, col: int, board_size: int) -> Tuple[int, int]:
    """
    Generator for all legal moves from a given position on the board.
    
    Parameters:
        - row (int): Starting row.
        - col (int): Starting column.
        - board_size (int): Size of the side of the square chessboard.
        
    Yields:
        - tuple: A tuple representing the legal move from the starting position.
    """
    for row_offset, col_offset in MOVE_OFFSETS:
        move_row, move_col = row + row_offset, col + col_offset
        if 0 <= move_row < board_size and 0 <= move_col < board_size:
            yield move_row, move_col

def warnsdorffs_heuristic(graph: defaultdict) -> callable:
    """
    Warnsdorff's heuristic for the knight's tour problem. Computes the degree of a vertex.
    
    Parameters:
        - graph (defaultdict): Graph representing the chessboard.
        
    Returns:
        - callable: A function that computes the degree of a vertex in the graph.
    """
    def compute_degree(vertex):
        return len(graph[vertex])
    return compute_degree

def first_true(sequence: List[bool]) -> Optional[bool]:
    """
    Returns the first True value in the sequence, or None if there isn't one.
    
    Parameters:
        - sequence (List[bool]): Sequence of boolean values.
        
    Returns:
        - bool/None: The first True value or None.
    """
    for item in sequence:
        if item:
            return item
    return None

def find_knights_tour(board_size: int = 8, 
                      start_row: int = 0, 
                      start_col: int = 0, 
                      heuristic: callable = warnsdorffs_heuristic,
                      visualize: bool = True, 
                      output_filename_animation: str = 'animated_knight_tour.gif') -> List[Tuple[int, int]]:
    """
    Finds a solution for the knight's tour problem using a given heuristic and visualizes the solution if specified.
    
    Parameters:
        - board_size (int, optional): Size of the chessboard. Defaults to 8.
        - start_row (int, optional): Row of the starting position. Defaults to 0.
        - start_col (int, optional): Column of the starting position. Defaults to 0.
        - heuristic (callable, optional): Heuristic function to use. Defaults to warnsdorffs_heuristic.
        - visualize (bool, optional): Whether to visualize the solution. Defaults to True.
        - output_filename_animation (str, optional): Filename for the saved animation. Defaults to 'animated_knight_tour.gif'.
        
    Returns:
        - List[Tuple[int, int]]: A list of tuples representing the solution path.
    """
    graph = build_graph(board_size)
    total_squares = board_size * board_size

    def traverse(path, current_vertex):
        if len(path) + 1 == total_squares:
            print("Found Knight's Tour")
            return path + [current_vertex]

        yet_to_visit = graph[current_vertex] - set(path)
        if not yet_to_visit:
            return False

        next_vertices = sorted(yet_to_visit, key=heuristic(graph))
        return first_true(
            traverse(path + [current_vertex], vertex) for vertex in next_vertices
        )

    solution = traverse([], (start_row, start_col))
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir + '/solutions', f"{board_size}x{board_size}_{start_row}-{start_col}.txt")

    with open(output_path, "w") as output:
        output.write("\n".join("{},{}".format(x[0], x[1]) for x in solution))

    if visualize:
        plot_knight_tour(solution, output_filename=output_filename_animation)

    return solution


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find a solution for the knight's tour problem.")
    
    parser.add_argument("--board_size", type=int, default=8, help="Size of the chessboard.")
    parser.add_argument("--start_row", type=int, default=0, help="Row of the starting position.")
    parser.add_argument("--start_col", type=int, default=0, help="Column of the starting position.")
    parser.add_argument("--visualize", action="store_true", help="Whether to visualize the solution.")
    parser.add_argument("--output_filename_animation", type=str, default="animated_knight_tour.gif", help="Filename for the saved animation.")
    
    args = parser.parse_args()
    
    solution = find_knights_tour(
        board_size=args.board_size,
        start_row=args.start_row,
        start_col=args.start_col,
        visualize=args.visualize,
        output_filename_animation=args.output_filename_animation
    )