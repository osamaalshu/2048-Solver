from __future__ import absolute_import, division, print_function
import copy
import time
import math
import random
from game import Game

MOVES = {0: 'up', 1: 'left', 2: 'down', 3: 'right'}
MAX_PLAYER, CHANCE_PLAYER = 0, 1

# Tree node. To be used to construct a game tree.


class Node:
    # Recommended: do not modify this __init__ function
    def __init__(self, state, player_type):
        self.state = (state[0], state[1])

        # to store a list of (direction, node) tuples
        self.children = []

        self.player_type = player_type

    # returns whether this is a terminal state (i.e., no children)
    def is_terminal(self):
        return len(self.children) == 0

# AI agent. Determine the next move.


class AI:
    # Recommended: do not modify this __init__ function
    def __init__(self, root_state, search_depth=3):
        self.root = Node(root_state, MAX_PLAYER)
        self.search_depth = search_depth
        self.simulator = Game(*root_state)

    # (Hint) Useful functions:
    # self.simulator.current_state, self.simulator.set_state, self.simulator.move

    # TODO: build a game tree from the current node up to the given depth

    def build_tree(self, node=None, depth=0):
        if node is None or depth == 0:
            return

        if node.player_type == MAX_PLAYER:

            for direction in MOVES:
                # reset the state to initial for each direction
                self.simulator.set_state(node.state[0], node.state[1])
                # check if action is valid
                if self.simulator.move(direction):
                    new_node = Node(
                        self.simulator.current_state(), CHANCE_PLAYER)
                    self.build_tree(new_node, depth-1)
                    node.children.append((direction, new_node))

        elif node.player_type == CHANCE_PLAYER:

            # Get all empty tiles
            empty_tiles = self.simulator.get_open_tiles()
            for i, j in empty_tiles:
                # reset the state to initial for each empty tile
                self.simulator.set_state(node.state[0], node.state[1])
                # set the empty tile to 2
                self.simulator.tile_matrix[i][j] = 2
                # create a new child node with the new state
                new_node = Node((self.simulator.tile_matrix,
                                self.simulator.score), MAX_PLAYER)
                self.build_tree(new_node, depth-1)
                node.children.append((None, new_node))

    # TODO: expectimax calculation.
    # Return a (best direction, expectimax value) tuple if node is a MAX_PLAYER
    # Return a (None, expectimax value) tuple if node is a CHANCE_PLAYER

    def expectimax(self, node=None):
        if node is None:
            return None, 0

        if node.is_terminal():
            return None, node.state[1]

        if node.player_type == MAX_PLAYER:
            best_move = None
            best_value = -math.inf
            for move, child in node.children:
                _, value = self.expectimax(child)
                if value > best_value:
                    best_move = move
                    best_value = value
            return best_move, best_value

        elif node.player_type == CHANCE_PLAYER:
            total_value = 0
            for move, child in node.children:
                _, value = self.expectimax(child)
                total_value += value
            return None, total_value / len(node.children)

    # Return decision at the root

    def compute_decision(self):
        self.build_tree(self.root, self.search_depth)
        direction, _ = self.expectimax(self.root)
        return direction

    # TODO (optional): implement method for extra credits

    def compute_decision_ec(self):
        self.build_tree(self.root, self.search_depth)
        best_direction, _ = self.expectimax_ec(self.root)
        return best_direction

   # TODO: expectimax calculation with heuristic function.
    # Return a (best direction, expectimax value) tuple if node is a MAX_PLAYER
    # Return a (None, expectimax value) tuple if node is a CHANCE_PLAYER

    def expectimax_ec(self, node=None):
        if node is None:
            return None, 0

        if node.is_terminal():
            return None, self.heuristic(node.state)

        if node.player_type == MAX_PLAYER:
            best_move = None
            best_value = -math.inf
            for move, child in node.children:
                _, value = self.expectimax_ec(child)
                if value > best_value:
                    best_move = move
                    best_value = value
            return best_move, best_value

        elif node.player_type == CHANCE_PLAYER:
            total_value = 0
            for move, child in node.children:
                _, expectimax_value = self.expectimax_ec(child)
                value = 1
                total_value += value * expectimax_value
            return None, (total_value / len(node.children))

    def heuristic(self, state):
        tile_matrix, score = state
        board_size = len(tile_matrix)

        # Calculate the score based on the number of empty tiles
        empty_tiles = len(self.simulator.get_open_tiles())
        score += empty_tiles * 500

        # Calculate the score based on the sum of the tiles and the maximum tile value
        max_tile = 0
        tile_sum = 0
        for row in tile_matrix:
            for tile in row:
                if tile > max_tile:
                    max_tile = tile
                tile_sum += tile
        score += tile_sum + max_tile ** 3

        # Calculate the score based on the monotonicity of the board
        monotonicity_score = 0
        for i in range(board_size):
            if all(tile_matrix[i][j] >= tile_matrix[i][j+1] for j in range(board_size-1)):
                monotonicity_score += sum(tile_matrix[i])
            if all(tile_matrix[j][i] >= tile_matrix[j+1][i] for j in range(board_size-1)):
                monotonicity_score += sum(row[i] for row in tile_matrix)
        score += monotonicity_score

        # Return the maximum score
        return score
