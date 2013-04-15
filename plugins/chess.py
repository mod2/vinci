# -*- coding: utf-8 -*-
# Chess plugin
#
# Turns a FEN chess board representation into a graphical board.
import re


def process(content, entry, notebook_url):
    """Convert FEN:<fen> to an HTML chess board."""
    regex = re.compile(r'^FEN:(.*)$', flags=re.MULTILINE)
    content = regex.sub(fen_gen, content)

    return content


def fen_gen(match):
    """Generates a HTML chess board from a fen string.
    Should be called from the re.sub method.
    """
    fen = FEN(fen_str=match.group(1).strip())
    color = 'light'
    rank = 8
    html = '<table class="chess" border="0" cellspacing="0" cellpadding="0">'
    for row in fen.graphical_board:
        html += '<tr><th>%s</th>' % (rank)
        rank -= 1
        for col in row:
            cell = col[0]
            team = col[1]
            html += '<td class="%s %s">%s</td>' % (color, team, cell)
            color = 'light' if color == 'dark' else 'dark'
        html += '</tr>'
        color = 'light' if color == 'dark' else 'dark'
    html += '<tr><th></th><th>a</th><th>b</th><th>c</th><th>d</th><th>e</th> \
            <th>f</th><th>g</th><th>h</th></tr>'
    return html + '</table> <div class="fen">FEN: %s</div>' % (fen.fen_str)


class FEN(object):
    def __init__(self, fen_str=None):
        super(FEN, self).__init__()
        self.fen_str = fen_str
        self.fen_board = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR'
        self.active_color = 'w'
        self.fen_castling = 'KQkq'
        self.en_passant = '-'
        self.halfmove_clock = 0
        self.fullmove_number = 1

        if fen_str is not None:
            temp = fen_str.split(' ')
            self.fen_board = temp[0]
            self.active_color = temp[1]
            self.fen_castling = temp[2]
            self.en_passant = temp[3]
            self.halfmove_clock = int(temp[4])
            self.fullmove_number = int(temp[5])
        else:
            self.fen_str = " ".join([self.fen_board,
                                     self.active_color,
                                     self.fen_castling,
                                     self.en_passant,
                                     str(self.halfmove_clock),
                                     str(self.fullmove_number)])

        self.board = self._generate_board()
        self.graphical_board = self._generate_graphical_board(True)
        self.turn = 'White' if self.active_color == 'w' else 'Black'

    def display_board(self,
                      row_del="\n",
                      cell_del=' ',
                      with_rank=False,
                      graphical=False):
        """Print the board in a user friendly way."""
        board = self.graphical_board if graphical else self.board
        rows = [cell_del.join(cells) for cells in board]
        if with_rank:
            rank = 1
            for row in rows:
                row = str(rank) + cell_del + row
                rank += 1
        return row_del.join(rows)

    def _generate_board(self):
        rows = self.fen_board.split('/')
        board = []
        for row in rows:
            cells = list(row)
            row = []
            for cnum, cell in enumerate(cells):
                if cell.isdigit():
                    row.extend(' '*int(cell))
                else:
                    row.append(cell)
            board.append(row)

        return board

    def _generate_graphical_board(self, status=False):
        graphical_board = []
        for row in self.board:
            new_row = []
            for cell in row:
                new_row.append(self._get_graphical_piece(cell, status))
            graphical_board.append(new_row)

        return graphical_board

    def __repr__(self):
        return "%s('%s')" % ('fen', self.fen_str)

    def __str__(self):
        return self.fen_str

    def _get_graphical_piece(self, piece, status=False):
        LETTER_PIECES = ['K', 'Q', 'B', 'N', 'R', 'P', 'k', 'q', 'b', 'n',
                         'r', 'p', ' ']
        GRAPHICAL_PIECES = [u'♔', u'♕', u'♗', u'♘', u'♖', u'♙', u'♚', u'♛',
                            u'♝', u'♞', u'♜', u'♟', ' ']
        rtn = GRAPHICAL_PIECES[LETTER_PIECES.index(piece)]
        if status:
            rtn = [GRAPHICAL_PIECES[LETTER_PIECES.index(piece.lower())],
                   'w' if piece in LETTER_PIECES[:6] else 'b']
        return rtn
