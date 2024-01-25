# coding=utf-8
# R2023 edition by wechatID：:czt_306

import c4d
import os
import random
import copy

food_icons = [1059243, 1021824, 12233,12144,1022798,
              1018102] + [1022964, 1022963, 1022962, 1022971, 1022968, 1022965, 1022967,1022966]

def load_bitmap(path):
    path = os.path.join(os.path.dirname(__file__), path)
    bmp = c4d.bitmaps.BaseBitmap()
    if bmp.InitWith(path)[0] != c4d.IMAGERESULT_OK:
        bmp = None
    return bmp

class iconArea(c4d.gui.GeUserArea):
    def __init__(self, GeDialog, doc):
        super().__init__()
        self.GetDialog = GeDialog
        self.doc = doc
        self.w, self.h = 45, 23
        self.wall_icon = 180000043
        self.body_icon = 1036557
        self.head_icon = 5150
        self.body_pos = [[23, 11], [22, 11], [21, 11], [20, 11]]
        self.last_key = [1, 0]  # [x,y]
        self.grassland = []  # [[x,y],[x,y],...]
        self.grassland_icon = 1028463
        self.food_pos = self.GetRandomPos()  # [x,y]
        self.food_icon = random.choice(food_icons)
        self.wall_pos = self.GetWallPos()
        self.temp_wall_pos = []  # [[x,y],[x,y],...]
        self.color = c4d.Vector(0.168)
        self.delta = 500
        self.score = 0
        self.level = self.score // 2000 + 1
        self.chance = 3
        self.unpause = True

    def drawInfo(self, x1, y1, x2, y2, msg):
        h = self.DrawGetFontHeight()
        score_w = self.DrawGetTextWidth('SCORE')
        score_value_w = self.DrawGetTextWidth(f'{self.score}')
        level_w = self.DrawGetTextWidth('LEVEL')
        level_value_w = self.DrawGetTextWidth(f'{self.level}')
        chance_w = self.DrawGetTextWidth('CHANCE')
        start_x = 12
        start_y = int(0.5 * h)
        self.DrawSetTextCol(self.color * 5, self.color * 1.2)
        self.DrawSetFont(c4d.FONT_STANDARD)
        self.DrawText('LEVEL', start_x, start_y)
        self.DrawText(f'{self.level}', start_x + level_w + 24, start_y)
        self.DrawText('SCORE', start_x + level_w + 24 + level_value_w + 64, start_y)
        self.DrawText(f'{self.score}', start_x + level_w + 24 + level_value_w + 64 + score_w + 24, start_y)
        self.DrawText('CHANCE', start_x + level_w + 24 + level_value_w + 64 + score_w + 24 + score_value_w + 64, start_y)
        self.DrawText(f'{self.chance}',
                      start_x + level_w + 24 + level_value_w + 64 + score_w + 24 + score_value_w + 64 + chance_w + 24,
                      start_y)

    def Timer(self, msg):
        keys = [c4d.KEY_DOWN, c4d.KEY_UP, c4d.KEY_RIGHT, c4d.KEY_LEFT]
        vector = [[0, 1], [0, -1], [1, 0], [-1, 0]]
        curr_index = vector.index(self.last_key)
        self.MoveBody(keys[curr_index], self.last_key)
        if self.food_icon == 1021824:
            self.CreateWallByEngineer()
        if self.food_icon == 1022798:
            self.FoodRandomMove()
        self.Redraw()

    def ReversalBody(self):
        self.body_pos.reverse()
        pos1, pos2 = self.body_pos[0:2]
        if pos1[0] == pos2[0]:
            if pos1[1] > pos2[1]:
                self.last_key = [0, 1]
            else:
                self.last_key = [0, -1]
        else:
            if pos1[0] > pos2[1]:
                self.last_key = [1, 0]
            else:
                self.last_key = [-1, 0]

    def GetRandomPos(self):
        while True:
            food_x = random.choice([i for i in range(1, self.w - 1)])
            food_y = random.choice([i for i in range(1, self.h - 1)])
            if [food_x, food_y] not in self.grassland or [food_x, food_y] not in self.body_pos:
                return [food_x, food_y]

    def GetNextPos(self, start, key):
        x0, y0 = start
        if key == c4d.KEY_DOWN:
            [x, y] = [x0, y0 + 1]
        elif key == c4d.KEY_UP:
            [x, y] = [x0, y0 - 1]
        elif key == c4d.KEY_LEFT:
            [x, y] = [x0 - 1, y0]
        elif key == c4d.KEY_RIGHT:
            [x, y] = [x0 + 1, y0]
        else:
            [x, y] = [x0 + self.last_key[0], y0 + self.last_key[1]]
        return [x, y]

    def FoodEffect(self):
        if self.food_icon == 1059243:
            # TODO:翻转
            self.ReversalBody()
            self.score += 200
        elif self.food_icon == 1021824:
            # TODO:工程师砌墙
            self.CreateWallByEngineer()
            self.score += 1000
        elif self.food_icon == 12233:
            # TODO:减速
            temp_delta = self.delta - 50
            self.delta = max(150,temp_delta)
            self.score += 100
        elif self.food_icon == 1018102:
            # TODO:清空砌墙
            temp_len = len(self.temp_wall_pos)
            split = temp_len * 0.5 if temp_len % 2 == 0 else (temp_len + 1) * 0.5
            for i in range(int(split)):
                self.temp_wall_pos.pop()
            self.score += 100
        elif self.food_icon == 12144:
            # TODO:截取一半
            temp_len = len(self.body_pos)
            if temp_len > 4:
                split = temp_len * 0.5 if temp_len % 2 == 0 else (temp_len + 1) * 0.5
                temp_wall = copy.deepcopy(self.body_pos[-int(split):])
                for i in range(int(split)):
                    self.body_pos.pop()
                self.temp_wall_pos += temp_wall
                self.score += 100
        else:
            self.score += 100

    def CreateWallByEngineer(self):
        self.temp_wall_pos.append(self.food_pos)
        while True:
            vector = random.choice([c4d.KEY_DOWN, c4d.KEY_UP, c4d.KEY_RIGHT, c4d.KEY_LEFT])
            x, y = self.GetNextPos(self.food_pos, vector)
            if [x, y] in self.temp_wall_pos:
                self.food_pos = [x, y]
            elif [x, y] in self.body_pos:
                self.food_pos = self.GetRandomPos()
                self.food_icon = random.choice(food_icons)
            elif [x, y] in self.wall_pos:
                self.food_pos = self.GetRandomPos()
                self.food_icon = random.choice(food_icons)
            else:
                self.food_pos = [x, y]
                break
        return True

    def FoodRandomMove(self):
        while True:
            vector = random.choice([c4d.KEY_DOWN, c4d.KEY_UP, c4d.KEY_RIGHT, c4d.KEY_LEFT])
            x, y = self.GetNextPos(self.food_pos, vector)
            if [x, y] not in self.temp_wall_pos:
                if [x, y] not in self.body_pos:
                    if [x, y] not in self.wall_pos:
                        self.food_pos = [x, y]
                        break
        return True

    def MoveBody(self, key, last_key):
        tempX, tempY = self.GetNextPos(self.body_pos[0], key)
        if self.food_pos == [tempX, tempY]:
            self.body_pos.insert(0, [tempX, tempY])
            self.FoodEffect()
            self.food_icon = random.choice(food_icons)
            self.food_pos = self.GetRandomPos()
        else:
            temp = self.isMoveOk(tempX, tempY)
            if temp == 1:
                self.body_pos.insert(0, [tempX, tempY])
                self.body_pos.pop()
                self.last_key = last_key
            elif temp == 2:
                pass
            else:
                if self.chance >= 0:
                    self.chance -= 1
                    self.ReversalBody()
                    self.score -= 200
                else:
                    c4d.gui.MessageDialog(f"非常遗憾，挑战失败！\nLEVEL:{self.level}\nSCORE:{self.score}", type=c4d.GEMB_OK)
                    self.GetDialog.Close()

    def InputEvent(self, msg):
        self.SetTimer(self.delta)
        if msg[c4d.BFM_INPUT_DEVICE] == c4d.BFM_INPUT_KEYBOARD:
            if msg[c4d.BFM_INPUT_CHANNEL] == c4d.KEY_ESC:
                self.GetDialog.Close()
            if msg[c4d.BFM_INPUT_CHANNEL] == c4d.KEY_DOWN:
                self.MoveBody(c4d.KEY_DOWN, [0, 1])
            if msg[c4d.BFM_INPUT_CHANNEL] == c4d.KEY_UP:
                self.MoveBody(c4d.KEY_UP, [0, -1])
            if msg[c4d.BFM_INPUT_CHANNEL] == c4d.KEY_LEFT:
                self.MoveBody(c4d.KEY_LEFT, [-1, 0])
            if msg[c4d.BFM_INPUT_CHANNEL] == c4d.KEY_RIGHT:
                self.MoveBody(c4d.KEY_RIGHT, [1, 0])
        self.Redraw()
        return True

    def GetWallPos(self):
        lst = []
        for i in range(self.h):
            for j in range(self.w):
                if i == 0 or i == self.h - 1:
                    lst.append([j, i])
                else:
                    if j == 0 or j == self.w - 1:
                        lst.append([j, i])
        return lst

    def isMoveOk(self, x, y):
        if x > 43 or x < 1:
            return 0
        elif y > 21 or y < 1:
            return 0
        elif [x, y] == self.body_pos[1]:
            return 2
        elif [x, y] in self.body_pos:
            return 0
        elif [x, y] in self.grassland:
            return 0
        elif [x, y] in self.temp_wall_pos:
            return 0
        elif self.isInTempWall():
            return 0
        else:
            return 1

    def isInTempWall(self):
        if not self.temp_wall_pos:
            return False
        for pos in self.temp_wall_pos:
            if pos in self.body_pos:
                return True
        return False

    def drawWall(self, x1, y1, x2, y2, msg):
        bmp = c4d.bitmaps.InitResourceBitmap(self.wall_icon)
        for x, y in self.wall_pos:
            self.DrawBitmap(bmp, x1 + x * 24, y1 + 24 * y + 24, 24, 24, 0, 0, 64, 64,
                            c4d.BMP_NORMAL | c4d.BMP_ALLOWALPHA)

    def drawBody(self, x1, y1, x2, y2, msg):
        for i, (x, y) in enumerate(self.body_pos):
            if i == 0:
                bmp = c4d.bitmaps.InitResourceBitmap(self.head_icon)
            else:
                bmp = c4d.bitmaps.InitResourceBitmap(self.body_icon)
            self.DrawBitmap(bmp, x1 + x * 24, y1 + 24 * y + 24, 24, 24, 0, 0, 64, 64,
                            c4d.BMP_NORMAL | c4d.BMP_ALLOWALPHA)

    def drawFood(self, x1, y1, x2, y2, msg):
        bmp = c4d.bitmaps.InitResourceBitmap(self.food_icon)
        x, y = self.food_pos
        self.DrawBitmap(bmp, x1 + x * 24, y1 + 24 * y + 24, 24, 24, 0, 0, 64, 64,
                        c4d.BMP_NORMAL | c4d.BMP_ALLOWALPHA)

    def drawTempWall(self, x1, y1, x2, y2, msg):
        bmp = c4d.bitmaps.InitResourceBitmap(self.wall_icon)
        for x, y in self.temp_wall_pos:
            self.DrawBitmap(bmp, x1 + x * 24, y1 + 24 * y + 24, 24, 24, 0, 0, 64, 64,
                            c4d.BMP_NORMAL | c4d.BMP_ALLOWALPHA)

    def DrawMsg(self, x1, y1, x2, y2, msg):
        self.OffScreenOn()
        self.SetClippingRegion(x1, y1, x2, y2)
        # 绘制窗口底色
        self.DrawSetPen(self.color)
        self.DrawRectangle(x1, y1, x2, y2)
        self.drawWall(x1, y1, x2, y2, msg)
        self.drawBody(x1, y1, x2, y2, msg)
        self.drawTempWall(x1, y1, x2, y2, msg)
        self.drawFood(x1, y1, x2, y2, msg)
        self.drawInfo(x1, y1, x2, y2, msg)

class MyDialog(c4d.gui.GeDialog):

    def __init__(self, doc):
        super().__init__()
        self.doc = doc
        self.area = iconArea(self, self.doc)
        self.SetTimer(self.area.delta)

    def CreateLayout(self):
        self.SetTitle("C4D贪吃蛇")
        self.AddUserArea(1000, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT)
        self.AttachUserArea(self.area, 1000)
        return True

    def Command(self, id, msg):
        return True

class GluttonousSnake(c4d.plugins.CommandData):
    PLUGIN_ID = 1061868
    PLUGIN_NAME = 'GluttonousSnake for C4D'
    PLUGIN_INFO = 0
    PLUGIN_ICON = load_bitmap('res/icons/GluttonousSnake.tif')
    PLUGIN_HELP = 'After launching the plug-in, click the window to officially start'

    def __init__(self):
        self.dialog = None

    def Register(self):
        return c4d.plugins.RegisterCommandPlugin(
            self.PLUGIN_ID, self.PLUGIN_NAME, self.PLUGIN_INFO, self.PLUGIN_ICON,
            self.PLUGIN_HELP, self)

    def Execute(self, doc):
        self.dialog = MyDialog(doc)
        self.dialog.Open(dlgtype=c4d.DLG_TYPE_MODAL, xpos=- 2, ypos=- 2, defaultw=1080 + 24, defaulth=600 + 24)
        return True

if __name__ == '__main__':
    GluttonousSnake().Register()
