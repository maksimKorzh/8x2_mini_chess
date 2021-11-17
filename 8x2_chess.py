##############################################
#
#               8x2 Mini chess
#
#                     by
#
#              Code Monkey King
#
##############################################

##############################################
#
#                PIECE ENCODING
#
#               0 - White king
#               1 - White queen
#               2 - White rook
#               3 - White bishop
#               4 - Black king
#               5 - Black queen
#               6 - Black rook
#               7 - Black bishop
#               8 - Empty square
#               9 - Offboard
#
##############################################

##############################################
#
#             BOARD REPRESENTATION
#                (8x4 mailbox)
#   
#             9 9 9 9 9 9 9 9 9 9
#             9 0 2 8 8 8 8 7 5 9
#             9 1 3 8 8 8 8 6 4 9
#             9 9 9 9 9 9 9 9 9 9
#
#             x x x x x x x x x x
#             x K R . . . . B q x
#             x Q B . . . . r k x
#             x x x x x x x x x x
#
##############################################

# colors
WHITE = 0
BLACK = 1
NO_COLOR = -1

# side to move
side = WHITE

# board
board = [
    9, 9, 9, 9, 9, 9, 9, 9, 9, 9,
    9, 0, 2, 8, 8, 8, 8, 7, 5, 9,
    9, 1, 3, 8, 8, 8, 8, 6, 4, 9,
    9, 9, 9, 9, 9, 9, 9, 9, 9, 9
]

# piece square table
pst = [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0,-1, 0, 5, 6, 7, 8, 0,-1, 0,
    0,-1, 0, 8, 7, 6, 5, 0,-1, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0
]

# move offsets (rules of the game)
offsets = [
  [1, -1, 10, -10, 11, -11, 9, -9],  # white king
  [1, -1, 10, -10, 11, -11, 9, -9],  # white queen
  [1, -1, 10, -10],                  # white rook
  [11, -11, 9, -9],                  # white bishop
  [1, -1, 10, -10, 11, -11, 9, -9],  # black king
  [1, -1, 10, -10, 11, -11, 9, -9],  # black queen
  [1, -1, 10, -10],                  # black rook
  [11, -11, 9, -9]                   # black bishop
]

# board coordinates
coordinates = [
    "xx", "xx", "xx", "xx", "xx", "xx", "xx", "xx", "xx", "xx",
    "xx", "a2", "b2", "c2", "d2", "e2", "f2", "g2", "h2", "xx",
    "xx", "a1", "b1", "c1", "d1", "e1", "f1", "g1", "h1", "xx",
    "xx", "xx", "xx", "xx", "xx", "xx", "xx", "xx", "xx", "xx",
]

# piece to color mapping
colors = [WHITE, WHITE, WHITE, WHITE, BLACK, BLACK, BLACK, BLACK, NO_COLOR, NO_COLOR]

# ASCII pieces
pieces = 'KQRBkqrb.x'

# material score weights
weights = [10000, 500, 900, 300, -10000, -500, -900, -300, 0, 0]

# best move in the position
best_source = -1
best_target = -1

# print board routine
def print_board():
    for row in range(4):
        for col in range(10):
            square = row * 10 + col
            piece = board[square]
            if col == 0 and row in [1, 2]: print(' ' + str(3 - row), end='')
            if piece != 9: print(' ' + pieces[piece], end='')
        if row != 3: print()
    
    print('   a b c d e f g h\n')

# generate moves
def generate_moves():
    global side
    move_list = []
    
    # loop over the board squares
    for square in range(len(board)):
        # init a piece
        piece = board[square]
        
        # skip the pieces that doesn't belong to the side to move
        if colors[piece] != side: continue
        
        # loop over move direction offsets
        for offset in offsets[piece]:
            target_square = square
            
            # loop over the attack ray within a given direction offset
            while True:
                target_square += offset
                captured_piece = board[target_square]
                
                # prevent from going offboard
                if captured_piece == 9: break
                
                # do not capture own pieces
                if colors[captured_piece] == side: break
                
                # king capture drops the current branch in a search
                if captured_piece in [0, 4]: return []
                
                # populate a move
                move_list.append({
                    'source': square, 'target': target_square,
                    'piece': piece, 'captured': captured_piece
                })
                             
                # stop iterating if captured opponent's piece
                if colors[captured_piece] == side ^ 1: break
                
                # prevent all pieces but a rook from sliding
                if piece not in [2, 6]: break

    # returns move list
    return move_list

# make move
def make_move(move):
    global side
    
    board[move['target']] = move['piece']
    board[move['source']] = 8
    side ^= 1

# take back
def take_back(move):
    global side
    
    board[move['target']] = move['captured']
    board[move['source']] = move['piece']
    side ^= 1

# search for best move
def search(depth):
    global side
    global best_source
    global best_target
    
    # escape condition: evalauate leaf nodes
    if depth == 0: return evaluate();
    
    # best score so far
    best_score = -10000;
    
    # best move so far
    current_best_source, current_best_target = -1, -1
    
    # generate moves
    move_list = generate_moves()
    
    # king has been captured
    if not len(move_list): return 10000

    # loop over moves in a move list
    for move in move_list:
        make_move(move)
        score  = -search(depth - 1)
        take_back(move)

        # negamax brute force search algorithm
        if score > best_score:
                best_score = score
                current_best_source = move['source']
                current_best_target = move['target']
    
    # associate best move with a best score
    best_source = current_best_source
    best_target = current_best_target
    
    # return the score of the best move
    return best_score

# static position evaluation
def evaluate():
    # static evaluation score
    score = 0
    
    # loop over the board quares
    for square in range(len(board)):
        piece = board[square]
        
        # material score
        if piece not in [8, 9]: score += weights[piece]
        
        # positional score
        if colors[piece] == BLACK: score -= pst[square]
        if colors[piece] == WHITE: score += pst[square]

    # returns negative score for black and positive for white pieces
    return -score if side else score

# main
def play():
    print_board()

    # game loop
    while True:
        # user prompt
        raw = input('   Your move: ')
        
        # skip if less than 4 chars
        if len(raw) < 4: continue
        
        # parse user move
        user_source = coordinates.index(raw[0] + raw[1])
        user_target = coordinates.index(raw[2] + raw[3])
        
        # make user move
        make_move({
            'source': user_source, 'target': user_target,
            'piece': board[user_source], 'captured': board[user_target]
        }); print_board()
        
        # make computer search for the best move
        score = search(5)
        
        # make computer move
        make_move({
            'source': best_source, 'target': best_target,
            'piece': board[best_source], 'captured': board[best_target]
        }); print_board(); print('Score:', score)
        
        # end the game if either of sides gets mated
        if abs(score) == 10000: print('   Checkmate!'); break

# play the game  
play()

















