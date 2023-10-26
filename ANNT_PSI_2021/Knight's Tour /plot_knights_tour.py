import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

def parse_solution_from_file(filename):
    """
    Reads a knight's tour solution from a file and converts it into a list of coordinate pairs.
    
    Parameters:
        - filename (str): The name of the file containing the solution.
        
    Returns:
        - list[tuple[int, int]]: A list of coordinate pairs representing the knight's moves.
    """
    with open(filename, 'r') as f:
        return [tuple(map(int, line.split(','))) for line in f.readlines()]

def plot_knight_tour(solution, output_filename='animated_knight_tour.gif'):
    """
    Plots and saves an animated GIF of the knight's tour based on the provided solution.
    
    Parameters:
        - solution (list[tuple[int, int]]): A list of coordinate pairs representing the knight's moves.
        - output_filename (str, optional): The filename for the saved GIF. Defaults to 'animated_knight_tour.gif'.
    """
    
    # Determine the size of the chessboard from the solution
    board_dimension = int(np.sqrt(len(solution)))
    
    # Initialize the canvas with a margin around the chessboard
    canvas_size = int(1.5 * board_dimension)
    canvas = np.ones((canvas_size, canvas_size, 3))

    # Calculate where the chessboard starts and ends on the canvas
    chessboard_start = (canvas_size - board_dimension) // 2
    chessboard_end = chessboard_start + board_dimension

    # Fill the canvas with alternating black and white squares
    for i in range(chessboard_start, chessboard_end):
        for j in range(chessboard_start, chessboard_end):
            if (i + j) % 2:
                canvas[i, j] = [0, 0, 0]  # Black square

    frames = []

    # Create frames for each move in the solution
    for index, coord in enumerate(solution):
        fig, ax = plt.subplots(figsize=(8, 8))

        # Color the path the knight has moved so far
        for past_coord in solution[:index]:
            x, y = past_coord
            x += chessboard_start
            y += chessboard_start
            if (x + y) % 2:  # Black square
                canvas[x, y] = [0, 0.5, 0]  # Dark Green
            else:  # White square
                canvas[x, y] = [0, 1, 0]  # Green

        ax.imshow(canvas, origin='upper')
        
        # Mark the current position of the knight with a 'K'
        k_y, k_x = coord
        k_x += chessboard_start
        k_y += chessboard_start
        ax.text(k_x, k_y, 'K', color='black' if (k_x + k_y) % 2 == 0 else 'white', 
                ha='center', va='center', fontsize=12, fontweight='bold')

        # Draw a rectangle around the chessboard
        rect = plt.Rectangle((chessboard_start - 0.5, chessboard_start - 0.5), 
                             board_dimension, board_dimension, fill=False, color='black', linewidth=2)
        ax.add_patch(rect)

        # Add labels for the rows and columns of the chessboard
        letters = [chr(97 + i) for i in range(board_dimension)]
        numbers = list(range(1, board_dimension + 1))
        for i, letter in enumerate(letters):
            ax.text(chessboard_start + i, chessboard_end + 0.2, letter, ha='center', va='bottom', fontsize=12)
            ax.text(chessboard_start - 0.8, chessboard_end - 1 - i, str(numbers[i]), ha='right', va='center', fontsize=12)
        
        # Add title to the frame
        starting_square = f"{letters[solution[0][1]]}{numbers[-solution[0][0]-1]}"
        ax.text(chessboard_start + board_dimension/2 - 0.25, chessboard_start - 1.5, f"Knight's Tour ({starting_square})", ha='center', va='top', fontsize=14, fontweight='bold')

        ax.axis('off')
        fig.tight_layout(pad=0)

        # Convert the current frame to an array and add it to the frames list
        fig.canvas.draw()
        frame = np.frombuffer(fig.canvas.buffer_rgba(), dtype=np.uint8).reshape(fig.canvas.get_width_height()[::-1] + (4,))
        frames.append(frame[..., :3])

        plt.close(fig)

    # Save the frames as an animated GIF
    frames = [Image.fromarray(frame) for frame in frames]
    frames[0].save('animations/' + output_filename, save_all=True, append_images=frames[1:], duration=500, loop=0)
