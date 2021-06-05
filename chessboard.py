from typing import List, Optional, Tuple


class Color:
    BLACK = "black"
    WHITE = "white"

    ALL = [BLACK, WHITE]

    @staticmethod
    def get_opposite_color(color: str) -> str:
        if color == Color.WHITE:
            return Color.BLACK
        else:
            return Color.WHITE


class Movement:
    def __init__(self, x: int, y: int, must_eat: bool = False, must_not_eat: bool = False, must_be_first: bool = False,
                 must_be_castling: bool = False):
        self.coordinates = (x, y)
        if must_not_eat and must_eat:
            raise Exception("Controversy: must_eat and must_not_eat both True")
        self.must_eat = must_eat
        self.must_not_eat = must_not_eat
        self.must_be_first = must_be_first
        self.must_be_castling = must_be_castling


class Figure:
    LETTER: str = None
    CAN_JUMP_OVER: bool = False
    WHITE_MOVEMENTS: List[Movement] = []
    BLACK_MOVEMENTS: List[Movement] = []
    TRANSFORMABLE: bool = False

    def __init__(self, color: str, move_count: int = 0):
        if color not in Color.ALL:
            raise Exception("Wrong color")
        self.color = color
        self.__move_count = move_count
        if color == Color.WHITE:
            self.movements = self.WHITE_MOVEMENTS or self.BLACK_MOVEMENTS
        else:
            self.movements = self.BLACK_MOVEMENTS or self.WHITE_MOVEMENTS

    def get_move(self, start_x: int, start_y: int, finish_x: int, finish_y: int) -> Movement:
        move = None
        for item in self.movements:
            if item.coordinates == (finish_x - start_x, finish_y - start_y):
                move = item
        if move is None:
            raise Exception("Restricted move")
        return move

    @property
    def move_count(self) -> int:
        return self.__move_count

    def get_letter(self):
        if self.color == Color.BLACK:
            return self.LETTER.lower()
        return self.LETTER.upper()

    def increment_move_count(self):
        self.__move_count += 1


class Pawn(Figure):
    LETTER = 'P'
    TRANSFORMABLE = True
    BLACK_MOVEMENTS = [Movement(0, 2, must_not_eat=True, must_be_first=True),
                       Movement(0, 1, must_not_eat=True),
                       Movement(1, 1, must_eat=True),
                       Movement(-1, 1, must_eat=True)]
    WHITE_MOVEMENTS = [Movement(0, -2, must_not_eat=True, must_be_first=True),
                       Movement(0, -1, must_not_eat=True),
                       Movement(1, -1, must_eat=True),
                       Movement(-1, -1, must_eat=True)]


class Rook(Figure):
    LETTER = 'R'
    WHITE_MOVEMENTS = [Movement(0, i) for i in range(-7, 8) if i != 0] + \
                      [Movement(i, 0) for i in range(-7, 8) if i != 0]


class Bishop(Figure):
    LETTER = 'B'
    WHITE_MOVEMENTS = [Movement(i, i) for i in range(-7, 8) if i != 0] + \
                      [Movement(i, -i) for i in range(-7, 8) if i != 0]


class Knight(Figure):
    LETTER = 'N'
    CAN_JUMP_OVER = True
    WHITE_MOVEMENTS = [Movement(j, i) for i in [-2, 2] for j in [-1, 1]] + \
                      [Movement(j, i) for i in [-1, 1] for j in [-2, 2]]


class Queen(Figure):
    LETTER = 'Q'
    WHITE_MOVEMENTS = MOVEMENTS = Rook.WHITE_MOVEMENTS + Bishop.WHITE_MOVEMENTS


class King(Figure):
    LETTER = 'K'
    WHITE_MOVEMENTS = [Movement(j, i) for i in [-1, 0, 1] for j in [-1, 0, 1] if i != 0 or j != 0] + \
                      [Movement(2, 0, must_be_castling=True),
                       Movement(-2, 0, must_be_castling=True)]


class ChessBoard:
    def __init__(self):
        self.board_size = (8, 8)
        self.board: List[List[Optional[Figure]]] = [[None for _ in range(8)] for _ in range(8)]
        self.__fill_board()
        self.amount_of_moves = 0

    def __fill_board(self):
        for i in range(8):
            self.board[i][1] = Pawn(Color.BLACK)
            self.board[i][6] = Pawn(Color.WHITE)
        for i, fig_cls in enumerate([Rook, Knight, Bishop]):
            self.board[i][0] = fig_cls(Color.BLACK)
            self.board[self.board_size[0] - 1 - i][0] = fig_cls(Color.BLACK)
            self.board[i][7] = fig_cls(Color.WHITE)
            self.board[self.board_size[0] - 1 - i][7] = fig_cls(Color.WHITE)
        self.board[3][0] = Queen(Color.BLACK)
        self.board[3][7] = Queen(Color.WHITE)
        self.board[4][0] = King(Color.BLACK)
        self.board[4][7] = King(Color.WHITE)

    def validate_move(self, start_x: int, start_y: int, finish_x: int, finish_y: int, dry_run=False):
        self.validate_out_of_board(start_x, start_y, finish_x, finish_y)
        start_figure = self.board[start_x][start_y]
        finish_figure = self.board[finish_x][finish_y]
        self.validate_start_figure(start_figure)
        move = start_figure.get_move(start_x, start_y, finish_x, finish_y)
        self.validate_first_move(start_figure, move)
        self.validate_finish_figure(start_figure, finish_figure, move, dry_run)
        self.validate_path(start_figure, start_x, start_y, move)
        if not dry_run and self.amount_of_moves % 2 != int(start_figure.color == Color.BLACK):
            raise Exception("Wrong color of figure for this move!")

    def validate_out_of_board(self, start_x: int, start_y: int, finish_x: int, finish_y: int):
        is_correct = 0 <= start_x < self.board_size[0] and \
                     0 <= finish_x < self.board_size[0] and \
                     0 <= start_y < self.board_size[1] and \
                     0 <= finish_y < self.board_size[1]
        if not is_correct:
            raise Exception('Out of board')

    @staticmethod
    def validate_start_figure(start_figure: Figure):
        if start_figure is None:
            raise Exception('Empty start cell')

    @staticmethod
    def validate_finish_figure(start_figure: Figure, finish_figure: Figure, move: Movement, dry_run: bool):
        if finish_figure and start_figure.color == finish_figure.color:
            raise Exception('One color figures on start and end positions')
        if not dry_run and move.must_eat and finish_figure is None:
            raise Exception('Cannot eat nothing')
        if move.must_not_eat and (finish_figure or dry_run):
            raise Exception('Cannot eat in such way')

    def validate_path(self, start_figure: Figure, start_x: int, start_y: int, move: Movement):
        if start_figure.CAN_JUMP_OVER:
            return
        dx = move.coordinates[0] // abs(move.coordinates[0]) if move.coordinates[0] else 0
        dy = move.coordinates[1] // abs(move.coordinates[1]) if move.coordinates[1] else 0
        cur_x = start_x + dx
        cur_y = start_y + dy
        while cur_x != start_x + move.coordinates[0] or cur_y != start_y + move.coordinates[1]:
            if self.board[cur_x][cur_y]:
                raise Exception('Figure is on the way')
            cur_x += dx
            cur_y += dy

    @staticmethod
    def validate_first_move(start_figure: Figure, move: Movement):
        if move.must_be_first and start_figure.move_count != 0:
            raise Exception('That not first move for this figure')

    def make_move(self, start_x: int, start_y: int, finish_x: int, finish_y: int, check_validate_move=True):
        if check_validate_move:
            self.validate_move(start_x, start_y, finish_x, finish_y)
        self.board[finish_x][finish_y] = self.board[start_x][start_y]
        self.board[start_x][start_y] = None
        self.board[finish_x][finish_y].increment_move_count()
        self.amount_of_moves += 1

    @staticmethod
    def translate_user_input(user_coord: str) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        exc = Exception('Invalid format')

        def convert_letter(letter):
            if not letter.isalpha():
                raise exc
            letter = letter.upper()
            return ord(letter) - ord('A')

        user_coord = user_coord.split()
        if len(user_coord) != 2 or len(user_coord[0]) != 2 or len(user_coord[1]) != 2:
            raise exc
        start_x = convert_letter(user_coord[0][0])
        finish_x = convert_letter(user_coord[1][0])
        if not (user_coord[0][1].isdigit() and user_coord[1][1].isdigit()):
            raise exc
        start_y = 8 - int(user_coord[0][1])
        finish_y = 8 - int(user_coord[1][1])
        return (start_x, start_y), (finish_x, finish_y)

    def apply_input(self, user_input: str):
        (start_x, start_y), (finish_x, finish_y) = self.translate_user_input(user_input)
        if not self.maybe_make_castling(start_x, start_y, finish_x, finish_y):
            if not self.maybe_make_transformation(start_x, start_y, finish_x, finish_y):
                self.make_move(start_x, start_y, finish_x, finish_y)
        color = self.board[finish_x][finish_y].color
        check = self.is_check(Color.get_opposite_color(color))
        mate = self.is_mate(Color.get_opposite_color(color))
        if check and mate:
            self.print()
            print('\nCheckmate to the {} King!'.format(Color.get_opposite_color(color)))
            print('{} wins!\n'.format(color).upper())
            exit(0)
        if check:
            print('\nAttention! Check to the {} King!\n'.format(Color.get_opposite_color(color)))

    def print(self):
        print(' ' * 3, 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', ' ' * 2)
        print()
        for i in range(self.board_size[0]):
            print(self.board_size[1] - i, ' ', end=' ')
            for j in range(self.board_size[1]):
                if self.board[j][i]:
                    print(self.board[j][i].get_letter(), end=' ')
                else:
                    print('.', end=' ')
            print(' ', self.board_size[1] - i)
        print()
        print(' ' * 3, 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', ' ' * 2)

    def is_figure_able_to_move(self, x: int, y: int):
        if not self.board[x][y]:
            raise Exception('Empty cell')
        for movement in self.board[x][y].movements:
            try:
                self.validate_move(x, y, x + movement.coordinates[0], y + movement.coordinates[1])
            except Exception:
                pass
            else:
                return True
        return False

    def is_cell_under_attack(self, x: int, y: int, color_of_attackers: str) -> bool:
        for i in range(self.board_size[0]):
            for j in range(self.board_size[1]):
                if i == x and j == y:
                    continue
                if self.board[i][j] and self.board[i][j].color == color_of_attackers:
                    try:
                        self.validate_move(i, j, x, y, dry_run=True)
                    except Exception:
                        pass
                    else:
                        return True
        return False

    def maybe_make_transformation(self, start_x: int, start_y: int, finish_x: int, finish_y: int) -> bool:
        figure = self.board[start_x][start_y]
        if figure is None or not figure.TRANSFORMABLE:
            return False
        if start_y == 1 and figure.color == Color.WHITE or start_y == 6 and figure.color == Color.BLACK:
            self.make_move(start_x, start_y, finish_x, finish_y)
            self.board[finish_x][finish_y] = Queen(figure.color, figure.move_count + 1)
            return True
        return False

    @staticmethod
    def rook_check_for_castling(figure: Figure, color: str):
        if type(figure) is not Rook:
            raise Exception('Cell is empty or figure is not Rook')
        if figure.color != color:
            raise Exception("Can't make castling with enemies Rook")
        if figure.move_count != 0:
            raise Exception("Rook has already done moves")

    def maybe_make_castling(self, start_x: int, start_y: int, finish_x: int, finish_y: int) -> bool:
        figure = self.board[start_x][start_y]
        if figure is None:
            return False
        move = figure.get_move(start_x, start_y, finish_x, finish_y)
        if not move.must_be_castling:
            return False
        dx = move.coordinates[0] // abs(move.coordinates[0])
        if self.is_cell_under_attack(start_x, start_y, Color.get_opposite_color(figure.color)):
            raise Exception('King is under attack')
        for factor in range(1, abs(move.coordinates[0]) + 1):
            x = dx * factor
            if self.is_cell_under_attack(start_x + x, start_y, Color.get_opposite_color(figure.color)) or \
                    self.board[start_x + x][start_y] is not None:
                raise Exception('Cell need to be free is under attack or is not empty')
        if figure.move_count != 0:
            raise Exception('King has already done moves')
        rook_right = self.board[self.board_size[0] - 1][finish_y]
        rook_left = self.board[0][finish_y]
        if dx > 0:
            self.rook_check_for_castling(rook_right, figure.color)
            self.make_move(start_x, start_y, finish_x, finish_y, check_validate_move=False)
            self.make_move(self.board_size[0] - 1, finish_y, finish_x - 1, finish_y, check_validate_move=False)
        else:
            self.rook_check_for_castling(rook_left, figure.color)
            self.make_move(start_x, start_y, finish_x, finish_y, check_validate_move=False)
            self.make_move(0, finish_y, finish_x + 1, finish_y, check_validate_move=False)
        return True

    def find_king(self, color) -> Tuple[int, int]:
        for i in range(self.board_size[0]):
            for j in range(self.board_size[1]):
                if type(self.board[i][j]) is King and self.board[i][j].color == color:
                    return i, j

    def is_check(self, color: str) -> bool:
        x, y = self.find_king(color)
        return self.is_cell_under_attack(x, y, Color.get_opposite_color(color))

    def is_mate(self, color: str) -> bool:
        for i in range(self.board_size[0]):
            for j in range(self.board_size[1]):
                if self.board[i][j] and self.board[i][j].color == color and self.check_moves(i, j):
                    return False
        return True

    def check_moves(self, x: int, y: int) -> bool:
        for move in self.board[x][y].movements:
            try:
                self.validate_move(x, y, x + move.coordinates[0], y + move.coordinates[1])
            except Exception as exc:
                continue
            finish_figure = self.board[x + move.coordinates[0]][y + move.coordinates[1]]
            start_figure = self.board[x][y]
            self.board[x][y] = None
            self.board[x + move.coordinates[0]][y + move.coordinates[1]] = start_figure
            back = self.is_check(start_figure.color)
            self.board[x][y] = start_figure
            self.board[x + move.coordinates[0]][y + move.coordinates[1]] = finish_figure
            if not back:
                return True
        return False
