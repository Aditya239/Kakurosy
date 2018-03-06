import sys
import random
from Tkinter import Tk, Canvas, Frame, Button, BOTH, TOP, BOTTOM
from datetime import datetime

random.seed(datetime.now())

MARGIN = 20
SIDE = 50
WIDTH = HEIGHT = MARGIN * 2 + SIDE * 9

class KakuroError(Exception):
    """
    An application specific error.
    """
    pass

class KakuroUI(Frame):
    """
    The Tkinter UI: draw the board and accept input
    """
    def __init__(self, parent, game):
        self.game = game
        print self.game.data_fills
        Frame.__init__(self, parent)
        self.parent = parent
        self.row, self.col = -1, -1
        self.initUI()

    def initUI(self):
        self.parent.title("Kakuro | Puzzle: "+str(self.game.gameId))
        self.pack(fill=BOTH, expand=1)
        self.canvas = Canvas(self, width=WIDTH, height=HEIGHT, highlightthickness=0)
        self.canvas.pack(fill=BOTH, side=TOP)
        clear_button = Button(self, text="Clear answers", command=self.clear_answers)
        clear_button.pack(fill=BOTH, side=BOTTOM)

        self.draw_grid()
        self.draw_puzzle()

        self.canvas.bind("<Button-1>", self.cell_clicked)
        self.canvas.bind("<Up>", self.Upkey_pressed)
        self.canvas.bind("<Down>", self.Downkey_pressed)
        self.canvas.bind("<Right>", self.Rightkey_pressed)
        self.canvas.bind("<Left>", self.Leftkey_pressed)
        self.canvas.bind("<Key>", self.key_pressed)

    def draw_grid(self):
        for i in xrange(10):
            stretch = 0
            if i % 9 == 0:
                stretch = 1
            self.canvas.create_line(
                MARGIN + i * SIDE, MARGIN - stretch,
                MARGIN + i * SIDE, HEIGHT - MARGIN + stretch,
                width=2
            )

            self.canvas.create_line(
                MARGIN, MARGIN + i * SIDE,
                        WIDTH - MARGIN, MARGIN + i * SIDE,
                width=2
            )

        for i in xrange(9):
            for j in xrange(9):
                if [i, j] not in self.game.data_fills:
                    self.canvas.create_rectangle(MARGIN + j * SIDE + 1, MARGIN + i * SIDE + 1,
                                                 MARGIN + j * SIDE + SIDE - 2, MARGIN + i * SIDE + SIDE - 2,
                                                 outline="gray", fill="gray")
                    self.canvas.create_line(
                        MARGIN + j * SIDE, MARGIN + i * SIDE,
                        MARGIN + j * SIDE + SIDE, MARGIN + i * SIDE + SIDE,
                        width=2
                    )

    def draw_puzzle(self):
        self.canvas.delete("numbers")
        for elem in self.game.data_totals:
            i = elem[2]
            j = elem[3]
            if elem[1] == 'v':
                modif = -1
            else:
                modif = 1
            self.canvas.create_text(
                MARGIN + j * SIDE + SIDE / 2 + modif * SIDE / 4,
                MARGIN + i * SIDE + SIDE / 2 + (-modif) * SIDE / 4,
                text=elem[0], tags="numbers",
                fill="black"
            )
        for elem in self.game.data_filled:
            i = elem[0]
            j = elem[1]
            self.canvas.create_text(
                MARGIN + j * SIDE + SIDE / 2,
                MARGIN + i * SIDE + SIDE / 2,
                font=("Purissa", 20),
                text=elem[2], tags="numbers",
                fill="slate gray"
            )

    def draw_cursor(self):
        self.canvas.delete("cursor")
        if self.row >= 0 and self.col >= 0:
            self.canvas.create_rectangle(
                MARGIN + self.col * SIDE + 1,
                MARGIN + self.row * SIDE + 1,
                MARGIN + (self.col + 1) * SIDE - 1,
                MARGIN + (self.row + 1) * SIDE - 1,
                outline="red", tags="cursor"
            )

    def draw_victory(self):
        self.canvas.create_oval(
            MARGIN + SIDE * 2, MARGIN + SIDE * 2,
            MARGIN + SIDE * 7, MARGIN + SIDE * 7,
            tags="victory", fill="dark orange", outline="orange"
        )
        self.canvas.create_text(
            MARGIN + 4 * SIDE + SIDE / 2,
            MARGIN + 4 * SIDE + SIDE / 2,
            text="Correct!", tags="victory",
            fill="white", font=("Ubuntu", 32)
        )

    def cell_clicked(self, event):
        if self.game.game_over:
            return
        x, y = event.x, event.y
        if (x > MARGIN and x < WIDTH - MARGIN and
                y > MARGIN and y < HEIGHT - MARGIN):
            self.canvas.focus_set()
            row, col = (y - MARGIN) / SIDE, (x - MARGIN) / SIDE
            self.row, self.col = row, col
        else:
            self.row, self.col = -1, -1
        self.draw_cursor()

    def key_pressed(self, event):
        if self.game.game_over:
            return
        if self.row >= 0 and self.col >= 0 and event.char in "1234567890" and event.char!='' and [self.row, self.col] in self.game.data_fills:
            found_flag = False
            for ind, item in enumerate(self.game.data_filled):
                if item[0]==self.row and item[1]==self.col:
                    found_flag = True
                    self.game.data_filled[ind][2] = int(event.char)
            if(not found_flag):
                self.game.data_filled = self.game.data_filled + [[self.row, self.col, int(event.char)]]
            self.draw_puzzle()
            self.draw_cursor()
            if self.game.check_win():
                self.draw_victory()

    def Upkey_pressed(self, event):
        if self.game.game_over:
            return
        if self.row > 0 and self.col >= 0:
            self.row = self.row - 1
            self.draw_cursor()

    def Downkey_pressed(self, event):
        if self.game.game_over:
            return
        if self.row >= 0 and self.col >= 0 and self.row < 8:
            self.row = self.row + 1
            self.draw_cursor()

    def Rightkey_pressed(self, event):
        if self.game.game_over:
            return
        if self.row >= 0 and self.col >= 0 and self.col <8:
            self.col = self.col + 1
            self.draw_cursor()

    def Leftkey_pressed(self, event):
        if self.game.game_over:
            return
        if self.row >= 0 and self.col > 0:
            self.col = self.col - 1
            self.draw_cursor()

    def clear_answers(self):
        self.game.set_answer_to_puzzle()
        self.canvas.delete("victory")
        self.draw_puzzle()

class KakuroGame(object):
    """
    A Kakuro game. Stores gamestate and completes the puzzle as needs be
    """
    def __init__(self):
        self.data_filled = []
        self.data_fills = []
        self.data_totals = []
        puzzlebank = []
        try:
            file = open("savedpuzzles.txt", "r")
        except IOError:
            print "Could not acquire read access to file: savedpuzzles.txt"
            sys.exit()
        with file:
            for line in file:
                if line.rstrip("\r\n").isdigit():
                    puzzlebank = puzzlebank + [int(line)]
            file.close()
        numpuzzles = len(puzzlebank)
        print "There seem to be "+str(numpuzzles)+" unique puzzles!"
        print "Randomly picking one..."
        ctr = 0
        currprob = 1.0/(numpuzzles-ctr)
        currguess = random.random()
        while (currguess>currprob and ctr < numpuzzles-1):
            ctr = ctr + 1
            currprob = 1.0 / (numpuzzles-ctr)
            currguess = random.random()
        self.gameId = puzzlebank[ctr]
        print "Selected puzzle: Number "+str(puzzlebank[ctr])

        file = open("savedpuzzles.txt", "r")
        readstatus = 0
        for line in file:
            if readstatus == 0 and line.rstrip("\r\n").isdigit():
                if int(line) == puzzlebank[ctr]:
                    readstatus = 1
                    continue
            if readstatus == 1 and line.rstrip("\r\n").isdigit():
                break
            elif readstatus == 1:
                line = line.rstrip("\r\n")
                if line[0] == 'e':
                    self.data_fills = self.data_fills + [[int(line[1]), int(line[2])]]
                else:
                    self.data_totals = self.data_totals + [[int(line[:-3]), line[-3], int(line[-2]), int(line[-1])]]
        file.close()
        self.game_over = False

    def check_win(self):
        return False

if __name__ == '__main__':
    game = KakuroGame()
    root = Tk()
    ui = KakuroUI(root, game)
    root.geometry("%dx%d" % (WIDTH, HEIGHT + 40))
    root.mainloop()
