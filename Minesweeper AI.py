"""
Minesweeper AI
Tom's original
works on my macbook pro,
does not guarantee that it works on other computers
solves Google's minesweeper, does not work on other versions
"""
from PIL.ImageGrab import grab
import numpy as np
import cv2
from time import sleep
import pyautogui
from sys import exit

class Grid:
    board_x = 0
    board_y = 0
    board_w = 0
    board_h = 0

    d = 0 #48 58 88

    rows = 0
    columns = 0

    mines_remaining = 99

    def __init__(self, x, y, index):
        self.x = x
        self.y = y
        self.index = index
        self.row = index // Grid.columns
        self.column = index % Grid.columns
        self.flipped = False
        self.flagged = False
        self.num = -1
        self.cent_x = x + Grid.d // 2
        self.cent_y = y + Grid.d // 2
        self.adj_grids = []
        for i in [-Grid.columns-1,-Grid.columns,-Grid.columns+1,-1,1,Grid.columns-1,Grid.columns,Grid.columns+1]:
            n = self.index + i
            if n >= 0 and n < Grid.rows * Grid.columns and abs(self.column - n % Grid.columns) <= 1:
                self.adj_grids.append(n)
        self.prob = 0

    def adj_unflagged(self):
        l = []
        for i in self.adj_grids:
            if grids[i].flipped == False and grids[i].flagged == False:
                l.append(i)
        return l

    def n_mines(self):
        n = 0
        for i in self.adj_grids:
            if grids[i].flagged == True:
                n += 1
        return n

    def adj_nums(self):
        l = []
        for i in self.adj_grids:
            if i in nums:
                l.append(i)
        return l

    def calculate(self):
        unflagged = self.adj_unflagged()
        for i in unflagged:
            grids[i].prob = (self.num - self.n_mines()) * 100 / len(unflagged)
        mines_found = 0
        for i in self.adj_unflagged():
            if grids[i].prob == 0:
                grids[i].click()
            elif grids[i].prob == 100:
                grids[i].right_click()
                mines_found += 1
        return mines_found

    def click(self):
        pyautogui.click((self.cent_x+Grid.board_x)/2,(self.cent_y+Grid.board_y)/2)
        self.flipped = True
    
    def right_click(self):
        pyautogui.rightClick((self.cent_x+Grid.board_x)/2,(self.cent_y + Grid.board_y)/2)
        self.flagged = True

    def subset_elimination(self):
        mines_found = 0
        for i in self.adj_nums():
            list1 = self.adj_unflagged()
            list2 = grids[i].adj_unflagged()
            if not (i not in list1 for i in list2):
                unique = list(set(list1) - set(list2))
                diff = (self.num - self.n_mines()) - (grids[i].num - grids[i].n_mines())
                if len(unique) == diff:
                    for j in unique:
                        grids[j].right_click()
                        mines_found += 1
                elif diff == 0:
                    for j in unique:
                        grids[j].click()
        return mines_found

    def touching(self):
        l = []
        for i in [-Grid.columns,-1,1,Grid.columns]:
            n = self.index + i
            if n >= 0 and n < Grid.rows * Grid.columns and abs(self.column - n % Grid.columns) <= 1:
                l.append(n)
        return l

    def find_path(n, previous, useful_unflagged):
        base_case = True
        both_ways = False
        l = []
        previous.append(n)
        for k in grids[n].adj_nums():
            for i in grids[k].adj_unflagged():
                if not i in previous and i in useful_unflagged:
                    base_case = False
                    temp = Grid.find_path(i, previous, useful_unflagged)
                    if both_ways:
                        for j in temp:
                            l.insert(0, j)
                    else:
                        l = temp
                        l.insert(0, n)
                    both_ways = True
        if base_case:
            return [n]
        return l

    def has_to(self, locations, virtual_mines):
        for i in self.adj_nums():
            spots_left = 0
            n = 0
            for j in grids[i].adj_grids:
                if j in locations:
                    spots_left += 1
                if j in virtual_mines:
                    n += 1
            mines_to_be_placed = grids[i].num - grids[i].n_mines() - n
            if spots_left - mines_to_be_placed == 0:
                return True
        return False

    def possible(self, virtual_mines):
        for i in self.adj_nums():
            n = 0
            for j in grids[i].adj_grids:
                if j in virtual_mines:
                    n += 1
            if grids[i].num - grids[i].n_mines() - n == 0:
                return False
        return True

    def tank_solver(locations, virtual_mines, dict, mines_remaining):
        if mines_remaining < 0:
            return 0
        if not locations:
            for i in virtual_mines:
                dict[i] += 1
            return 1
        n = 0
        if not grids[locations[0]].has_to(locations, virtual_mines):
            temp = locations.pop(0)
            n += Grid.tank_solver(locations, virtual_mines, dict, mines_remaining)
            locations.insert(0, temp)
        if grids[locations[0]].possible(virtual_mines):
            virtual_mines.append(locations[0])
            temp = locations.pop(0)
            n += Grid.tank_solver(locations, virtual_mines, dict, mines_remaining - 1)
            locations.insert(0, temp)
            virtual_mines.remove(locations[0])
        return n

def screen_shot():
    im = grab()
    im_np = np.array(im)
    im_np = cv2.cvtColor(im_np, cv2.COLOR_RGB2BGR)
    return im_np

def proc_img():
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    _, thresh = cv2.threshold(blur, 183, 255, cv2.THRESH_BINARY_INV)

    if Grid.board_x == 0:
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        x = 0
        for contour in contours:
            area = cv2.contourArea(contour)
            if area in [646379, 905279, 1197799]:
                x, y, w, h = cv2.boundingRect(contour)
                break
        if x == 0:
            print("board not found")
            return [], False
        Grid.board_x = x
        Grid.board_y = y
        Grid.board_w = w
        Grid.board_h = h

    roi = img[Grid.board_y:Grid.board_y+Grid.board_h,Grid.board_x:Grid.board_x+Grid.board_w]
    roi_blur = blur[Grid.board_y:Grid.board_y+Grid.board_h,Grid.board_x:Grid.board_x+Grid.board_w]
    _, roi_thresh = cv2.threshold(roi_blur, 190, 255, cv2.THRESH_BINARY_INV) #184, 190
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    roi_thresh = cv2.dilate(roi_thresh, kernel, iterations=1)

    if Grid.d == 0:
        contours, _ = cv2.findContours(roi_thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 2000 and area < 8000:
                _, _, w, _ = cv2.boundingRect(contour)
                break
        rows = round(roi.shape[0]/(w+2))
        columns = round(roi.shape[1]/(w+2))
        Grid.d = w
        Grid.rows = rows
        Grid.columns = columns
        for i in range(rows):
            for j in range(columns):
                grids.append(Grid(1+j*(w+2), 1+i*(w+2), i*columns+j))
    #unflipped: 101 214 179, 94  208 172 137 224 198 131 220 192
    #0:         163 195 223, 157 185 210
    #1:         203 116 56
    #2:         114 166 145, 111 161 139
    #3:         63  71  196, 62  70  195
    #4:         158 119 170, 155 114 163
    #5:         54  149 240
    #6:         163 173 134, 160 167 127
    #7:         119 137 152, 115 131 144
    r_mp = {223:0,210:0,56:1,145:2,139:2,196:3,195:3,170:4,163:4,240:5,134:6,127:6,152:7,144:7}
    nums = []
    new_board = True
    for i in grids:
        g = roi.item(i.cent_y, i.cent_x, 1)
        r = roi.item(i.cent_y, i.cent_x, 2)
        if g not in [214, 208, 224, 220]:
            i.flipped = True
            new_board = False
            if r in r_mp:
                if i.num == -1:
                    i.num = r_mp[r]
                if r_mp[r] and i.adj_unflagged():
                    nums.append(i.index)
            else:
                print("abnormal board at", i.column, i.row)
                print(roi.item(i.cent_y, i.cent_x, 0))
                print(roi.item(i.cent_y, i.cent_x, 1))
                print(roi.item(i.cent_y, i.cent_x, 2))
                cv2.destroyAllWindows()
                exit()
    if new_board == True:
        for i in grids:
            i.num = -1
            i.prob = 0
            i.flipped = False
            i.flagged = False
        index = int(Grid.rows / 2 * Grid.columns + Grid.columns / 2)
        grids[index].click()
        sleep(0.15)

    for i in grids:
        cv2.rectangle(roi, (i.x, i.y), (i.x + Grid.board_w, i.y + Grid.board_h), (0, 255, 0), 2)
        cv2.putText(roi,str(i.num),(i.cent_x,i.cent_y),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,0,0),1,cv2.LINE_AA)
    cv2.imshow("Screen(Computer Vision)", roi)
    cv2.waitKey(1)
    return nums, True

def solve():
    mines_found = 0
    for i in nums:
        mines_found += grids[i].calculate()
        mines_found += grids[i].subset_elimination()

    useful_unflagged = []
    for i in grids:
        if i.num > 0:
            for j in i.adj_unflagged():
                if not j in useful_unflagged:
                    useful_unflagged.append(j)
    list_locations = []
    while useful_unflagged:
        list_locations.append(Grid.find_path(useful_unflagged[0], [], useful_unflagged))
        useful_unflagged = [j for j in useful_unflagged if j not in list_locations[-1]]
    for j in list_locations:
        dict = {k : 0 for k in j}
        arrangements = Grid.tank_solver(j, [], dict)
        for k in dict:
            if dict[k] == arrangements:
                grids[k].right_click()
                n += 1
                mines_found += 1
            elif dict[k] == 0:
                grids[k].click()
                n += 1
    if n == 0:
        remaining_tiles = []
        for i in grids:
            if i.flipped == False and i.flagged == False:
                remaining_tiles.append(i.index)
        if len(remaining_tiles) > 10:
            return 0
        else:
            dict = {i : 0 for i in remaining_tiles}
            Grid.end_game(remaining_tiles, [], dict, Grid.mines_remaining - mines_found)
            for i in dict:
                if dict[i] == min(dict.values()):
                    grids[i].click()
                    n += 1
    print(n)
    return mines_found

sleep(1)
grids = []
pyautogui.PAUSE = 0
cv2.namedWindow("Screen(Computer Vision)", cv2.WINDOW_NORMAL)
found = False
while True:
    sleep(0.8)
    if found:
        pyautogui.moveTo(460, 80)
    img = screen_shot()
    nums, found = proc_img()
    if found:
        Grid.mines_remaining -= solve()