# 6.009 Lab 2: Snekoban

import json
import typing

# NO ADDITIONAL IMPORTS!


direction_vector = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1),
}


def new_game(level_description):
    """
    Given a description of a game state, create and return a game
    representation of your choice.

    The given description is a list of lists of lists of strs, representing the
    locations of the objects on the board (as described in the lab writeup).

    For example, a valid level_description is:

    [
        [[], ['wall'], ['computer']],
        [['target', 'player'], ['computer'], ['target']],
    ]

    The exact choice of representation is up to you; but note that what you
    return will be used as input to the other functions.
    """
    # represent board as a dictionary
    board = {}
    # initialize all the future keys
    num_rows, num_cols = len(level_description), len(level_description[0])
    walls = [[False for _ in range(num_cols)] for _ in range(num_rows)]
    player_loc = [] # row, col pair
    target_locs = [] # will be a list of target coord tuples 
    computer_locs = [] # will be a list of location coord tuples

    # properly populate the properties
    for row in range(num_rows):
        for col in range(num_cols):
            tile = level_description[row][col]
            if "wall" in tile:
                walls[row][col] = True
            if "player" in tile:
                player_loc = [row, col]
            if "target" in tile:
                target_locs.append([row, col])
            if "computer" in tile:
                computer_locs.append([row, col])

    # populate the dictionary representing the game
    board["num_rows"] = num_rows
    board["num_cols"] = num_cols
    board["walls"] = walls
    board["player_loc"] = player_loc
    board["target_locs"] = target_locs
    board["computer_locs"] = computer_locs

    victory_check(board)

    return board



def victory_check(board):
    """
    Given a game representation (of the form returned from new_game), return
    a Boolean: True if the given game satisfies the victory condition, and
    False otherwise.
    """
    if len(board["computer_locs"]) == 0 or len(board["target_locs"]) == 0:
        return False
        
    else:
        set_computer_locs = set([tuple(coord) for coord in board["computer_locs"]])
        set_target_locs = set([tuple(coord) for coord in board["target_locs"]])
        return (set_computer_locs == set_target_locs)


def deep_copy_board(board):
    """
    Returns a "deep" copy of a given board. Does not need to remake the wall or target locations b/c
    the walls and targets never move.
    """
    player_loc_copy = board["player_loc"].copy()
    computer_locs_copy = [board["computer_locs"][r].copy() for r in range(len(board["computer_locs"]))]

    board_copy = {
        "num_rows": board["num_rows"],
        "num_cols": board["num_cols"],
        "walls": board["walls"],
        "player_loc": player_loc_copy,
        "target_locs": board["target_locs"],
        "computer_locs": computer_locs_copy
    }
    return board_copy

def step_game(board, direction):
    """
    Given a game representation (of the form returned from new_game), return a
    new game representation (of that same form), representing the updated game
    after running one step of the game.  The user's input is given by
    direction, which is one of the following: {'up', 'down', 'left', 'right'}.

    This function should not mutate its input.
    """
    # check that input is valid
    if direction not in direction_vector:
        raise NameError
    
    # establish some indices and truth values (whether there are objects in front of the player)
    next_board = deep_copy_board(board)
    r, c = next_board["player_loc"]
    dr, dc = direction_vector[direction]
    wall_next = board["walls"][r+dr][c+dc] # True if there is wall at next tile
    comp_next = [r+dr, c+dc] in board["computer_locs"] # True if there is computer at next tile
    comp_next_next = [r+2*dr, c+2*dc] in board["computer_locs"] # True if there is computer 2 tiles ahead
    try: # True if there is wall 2 tiles ahead
        wall_next_next = board["walls"][r+2*dr][c+2*dc]
    except:
        wall_next_next = False

    # attempt movement
    if not (wall_next or comp_next): # nothing ahead, move player
        next_board["player_loc"] = [r+dr, c+dc]
    elif wall_next: # blocked by wall
        pass
    elif comp_next:
        if not (wall_next_next or comp_next_next): # satisfies conditions to move computer and player
            cn_ind = board["computer_locs"].index([r+dr, c+dc]) # get index of next computer
            next_board["computer_locs"][cn_ind] = [r+2*dr, c+2*dc]
            next_board["player_loc"] = [r+dr, c+dc]

    return next_board
    


def dump_game(board:dict):
    """
    Given a game representation (of the form returned from new_game), convert
    it back into a level description that would be a suitable input to new_game
    (a list of lists of lists of strings).

    This function is used by the GUI and the tests to see what your game
    implementation has done, and it can also serve as a rudimentary way to
    print out the current state of your game for testing and debugging on your
    own.
    """
    # initialize empty external representation
    ext_repr = []
    
    # add walls
    for row in range(board["num_rows"]):
        new_row = []
        for col in range(board["num_cols"]):
            if board["walls"][row][col]:
                new_row.append(["wall"])
            else:
                new_row.append([])
        ext_repr.append(new_row)

    # add target, computer and player
    for coord in board["target_locs"]:
        ext_repr[coord[0]][coord[1]].append("target")
    for coord in board["computer_locs"]:
        ext_repr[coord[0]][coord[1]].append("computer")
    ext_repr[board["player_loc"][0]][board["player_loc"][1]].append("player")
    
    victory_check(board)

    return ext_repr


def same_board(board1, board2):
    """Checks if two given dictionaries represent the same board. Returns True if boards are the same, False elsewise"""
    # return dump_game(board1, end_check = False) == dump_game(board2, end_check = False)
    return hash_board(board1) == hash_board(board2)

def hash_board(board):
    """
    The hashable board representation is a nested tuple: ((player_loc), (computer locs))
    since the player and computer locations are enough uniquely determine a state within a game
    """
    return (tuple(board["player_loc"]), frozenset([tuple(coord) for coord in board["computer_locs"]]))

def solve_puzzle(board):
    """
    Given a game representation (of the form returned from new game), find a
    solution.

    Return a list of strings representing the shortest sequence of moves ("up",
    "down", "left", and "right") needed to reach the victory condition.

    If the given level cannot be solved, return None.

    Follows this process:
    initialize visited, queue
    while q or victory achieved:
        pop one path from q
        if terminal move leads to visited board, ignore
        if terminal move achieves victory state, break and return path
        add terminal board state to visited
        add each next viable, unvisited move set to q
    """
    def get_viable_next_moves(board):
        """
        Tests which moves are viable for advancing the game and returns dict with move : board pairs
        """
        viable = {}
        player_loc = board["player_loc"] # current player location
        # try all directions
        for dir in direction_vector:
            next_board = step_game(board, dir)
            if next_board["player_loc"] != player_loc: # move successful
                viable[dir] = next_board
        return viable
    
    queue = [([], board)] # list of board states to evaluate e.g. of an element: (["up", "left", "down"], latest_board)
    visited = set()
    
    while queue:
        curr_state = queue.pop(0) # pop from start
        if hash_board(curr_state[1]) not in visited: # if visited, skip
            if victory_check(curr_state[1]): # if win, return path
                return curr_state[0]

            visited.add(hash_board(curr_state[1])) # update visited

            # add next viable moves to q
            next_moves = get_viable_next_moves(curr_state[1]) # dict
            for dir in next_moves:
                new_path = curr_state[0].copy()
                new_path.append(dir)
                new_move = (new_path, next_moves[dir])
                queue.append(new_move)
    return None


if __name__ == "__main__":
#     level_descrip = [
#    [["wall"],  ["wall"],  ["wall"],      ["wall"],             ["wall"], ["wall"]],
#    [["wall"],  [],        ["target"],  [],                   [],       ["wall"]],
#    [["wall"],  [],        ["computer"],            ["player"], [],       ["wall"]],
#    [["wall"],  ["wall"],  ["wall"],      ["wall"],             ["wall"], ["wall"]]
# ] 
#     board1 = new_game(level_descrip)
#     solve_board1 = solve_puzzle(board1)
    # print(hash_board(board1))
#     print(solve_board1)
    pass

