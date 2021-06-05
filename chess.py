import chessboard


def main():
    game_board = chessboard.ChessBoard()
    game_board.print()
    while True:
        print()
        user_input = input('Enter start and finish coords for move number {}: '.format(game_board.amount_of_moves + 1))
        while True:
            try:
                game_board.apply_input(user_input)
            except Exception as exc:
                print(str(exc))
                user_input = input("Please try again: ")
            else:
                game_board.print()
                break


main()
