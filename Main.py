from copy import copy

import pygame
import sys
import random
import time
from dataclasses import dataclass

#введение переменных
pygame.init()
screen_x = 300
screen_y = 675
cell = 25
fps = 60
count = 0
length_field = 10
alfabet = {chr(i): i - 96 for i in range(97, 107)}
choices = []
direction = '_'
player_picking = []
player_direction = '_'
player_cell = []
#0 - player
#1 - computer
turn = 0

#создание массива для хранения данных о игровом поле
grid_player = []
grid_computer = []
# 0, _ - область не занята
# 1, _ - область занята кораблем
# 2, _ - область вокруг корабля
# _, 0 - область не выбранная игроком или компьютером
# _, 1 - область выбранная игроком или компьютером
for i in range(length_field + 2):
    grid_player.append([])
    grid_computer.append([])
    for j in range(length_field + 2):
        grid_computer[i].append([0, 0])
        grid_player[i].append([0, 0])

#создание игрового поля
screen = pygame.display.set_mode((screen_x, screen_y))
pygame.display.set_caption("SeaFight from Tema_RBV")
clock = pygame.time.Clock()


def draw_nums():
    # буквы и цифры
    font = pygame.font.SysFont('couriernew', 20, bold=True)
    for i, j in alfabet.items():
        text = font.render(f'{i.upper()}', True, (0, 0, 0))
        screen.blit(text, ((0.2 + j) * cell, 1))
        screen.blit(text, ((0.2 + j) * cell, 277))
        num = font.render(f'{j}', True, (0, 0, 0))
        screen.blit(num, (7, j * cell))
        screen.blit(num, (7, (j + 11) * cell))

    # удаление числа 10 (залезает на синий квадрат)
    pygame.draw.rect(screen, pygame.Color(222, 248, 100),
                     pygame.Rect(0, 10 * cell, cell, cell), 0)
    pygame.draw.rect(screen, pygame.Color(222, 248, 100),
                     pygame.Rect(0, 21 * cell, cell, cell), 0)

    # запись числа 10
    font = pygame.font.SysFont('couriernew', 20, bold=True)
    num = font.render('10', True, (0, 0, 0))
    screen.blit(num, (0, 10 * cell))
    screen.blit(num, (0, 21 * cell))


def draw_wire():
    # создание серой сетки
    rect = pygame.Rect(0, 0, cell, cell)
    for i in range(int(screen_x / cell)):
        for j in range(int(screen_y / cell)):
            pygame.draw.rect(screen, pygame.Color(145, 145, 145), pygame.Rect(i * cell, j * cell, cell, cell), 1)

    # создание синих рамок
    pygame.draw.rect(screen, pygame.Color(70, 125, 234),
                     pygame.Rect(cell, cell, cell * length_field, cell * length_field),
                     3)
    pygame.draw.rect(screen, pygame.Color(70, 125, 234),
                     pygame.Rect(cell, 12 * cell, cell * length_field, cell * length_field), 3)


def draw_screen():
    #заливка
    screen.fill(pygame.Color(222, 248, 116, 100))

    draw_nums()

    #синие поля
    pygame.draw.rect(screen, pygame.Color(70, 200, 235),
                     pygame.Rect(cell, cell, cell * length_field, cell * length_field),
                     0)
    pygame.draw.rect(screen, pygame.Color(70, 200, 235),
                     pygame.Rect(cell, 12 * cell, cell * length_field, cell * length_field), 0)

    draw_wire()


draw_screen()


#создание класса для фигур кораблей, методы подразумевают
#что действия выполняются относительно главного квадрата
#с координатой х, у, который является верхним левым квадратом
#относительно всей фигуры
@dataclass
class Geometry:
    length: int
    direction: str

    #х и у являются координатами в синем квадрате
    def check_intersection(self, x: int, y: int, grid: list = grid_player, result=False):
        global grid_computer, grid_player
        for i in range(self.length + 1):
            if self.direction == 'hor':
                if grid[x + i + 1][y + 1][0] == 0:
                    continue
                else:
                    break
            if self.direction == 'vert':
                if grid[x + 1][y + i + 1][0] == 0:
                    continue
                else:
                    break
        else:
            result = True
        return result

    def check_position(self, x: int, y: int):
        if 0 <= x < 10 and 0 <= y < 10:
            if self.direction == 'hor':
                if x + self.length < 10:
                    return True
                else:
                    return False
            else:
                if y + self.length < 10:
                    return True
                else:
                    return False
        else:
            return False

    def set_value(self, x: int, y: int, grid: list):
        global grid_computer, grid_player
        if self.direction == 'hor':
            for i in range(self.length + 3):
                grid[x + i][y][0] = 2
                grid[x + i][y + 1][0] = 2
                grid[x + i][y + 2][0] = 2
            for i in range(self.length + 1):
                grid[x + i + 1][y + 1][0] = 1
        else:
            for i in range(self.length + 3):
                grid[x][y + i][0] = 2
                grid[x + 1][y + i][0] = 2
                grid[x + 2][y + i][0] = 2
            for i in range(self.length + 1):
                grid[x + 1][y + i + 1][0] = 1

    def set_picked_value(self, x: int, y: int, grid: list):
        global grid_computer, grid_player
        if self.direction == 'hor':
            for i in range(self.length + 3):
                grid[x + i][y][1] = 1
                grid[x + i][y + 1][1] = 1
                grid[x + i][y + 2][1] = 1
        else:
            for i in range(self.length + 3):
                grid[x][y + i][1] = 1
                grid[x + 1][y + i][1] = 1
                grid[x + 2][y + i][1] = 1

    def turn(self):
        if self.direction == 'vert':
            self.direction = 'hor'
        else:
            self.direction = 'vert'

    #х и у являются координатами всего поля
    def draw_rect(self, x: int, y: int, color=(80, 60, 230), width: int = 0):
        if self.direction == 'hor':
            L = [pygame.Rect((x + i) * cell, y * cell, cell, cell) for i in range(4)]
        else:
            L = [pygame.Rect(x * cell, (y + i) * cell, cell, cell) for i in range(4)]
        for i in range(self.length + 1):
            pygame.draw.rect(screen, pygame.Color(color), L[i], width)

    def del_rect(self, x: int, y: int):
        if self.direction == 'hor':
            L = [pygame.Rect((x + i) * cell, y * cell, cell, cell) for i in range(4)]
        else:
            L = [pygame.Rect(x * cell, (y + i) * cell, cell, cell) for i in range(4)]
        for i in range(self.length + 1):
            pygame.draw.rect(screen, pygame.Color(70, 200, 235), L[i], 0)
            pygame.draw.rect(screen, pygame.Color(145, 145, 145), L[i], 1)
            pygame.draw.rect(screen, pygame.Color(70, 125, 234),
                             pygame.Rect(cell, cell, cell * length_field, cell * length_field),
                             3)
            pygame.draw.rect(screen, pygame.Color(70, 125, 234),
                             pygame.Rect(cell, 12 * cell, cell * length_field, cell * length_field), 3)

    def draw_rect_area(self, x: int, y: int, color=(140, 140, 140)):
        #рисует область вокруг корабля
        L = []
        if self.direction == 'hor':
            for i in range(self.length + 3):
                L.append((x + i - 1, y + 1))
                L.append((x + i - 1, y - 1))
            L.append((x - 1, y))
            L.append((x + 1 + self.length, y))
        if self.direction == 'vert':
            for i in range(self.length + 3):
                L.append((x + 1, y + i - 1))
                L.append((x - 1, y + i - 1))
            L.append((x, y - 1))
            L.append((x, y + 1 + self.length))
        for l in L:
            if 0 < l[0] < 11 < l[1] < 22:
                pygame.draw.rect(screen, pygame.Color(color),
                                 pygame.Rect(l[0] * cell, l[1] * cell, cell, cell),
                                 0)


def random_shape(m: int):
    #случайный выбор фигуры - длина и напрвление
    while True:
        x = random.randint(0, 9)
        y = random.randint(0, 9)
        direction_random = random.randint(0, 1)
        if direction_random == 0:
            direction = 'vert'
        else:
            direction = 'hor'
        shape = Geometry(m, direction)
        if shape.check_position(x, y):
            S = (x, y, Geometry(m, direction))
            break
        else:
            continue
    return S


def random_draw(m: int):
    #рисование фигуры с ее проверкой на нахождении в правильном месте
    shape = random_shape(m)
    flag = True
    while flag:
        if shape[2].check_intersection(shape[0], shape[1], grid=grid_computer):
            #чтобы посмотреть поле компьютера, включи строку
            #shape[2].draw_rect(shape[0] + 1, shape[1] + 12)
            shape[2].set_value(shape[0], shape[1], grid_computer)
            flag = False
        else:
            shape = random_shape(m)


def random_field():
    #случайное заполнение поля для области компьютера
    for k in range(4):
        for n in range(4 - k):
            random_draw(k)


def draw_picked(x, y, color=(170, 100, 10)):
    #рисование клетки которая была выбрана инроком или компьютером
    rect = pygame.Rect(x * cell, y * cell, cell, cell)
    pygame.draw.rect(screen, pygame.Color(color), rect, 0)


def check_possibility(x, y):
    #проверка возможности выбора данной клетки
    if 10 > x >= 0 and 10 > y >= 0 and grid_player[x + 1][y + 1][1] == 0:
        return True
    else:
        return False


def sort_choices(points: list = choices, direct: int = direction):
    #сортировка списка, который хранит подряд выбранные попадания компьютера
    global choices, direction, player_direction, player_picking
    if direct == 0:
        S = sorted(points, key=lambda item: item[0])
    elif direct == 1:
        S = sorted(points, key=lambda item: item[1])
    else:
        S = points
    if points == choices:
        choices = S
    else:
        player_picking = S


def random_choice():
    #случайный выбор клетки поля игрока
    flag = True
    while flag:
        new_x = random.randint(0, 9)
        new_y = random.randint(0, 9)
        if check_possibility(new_x, new_y):
            flag = False
        else:
            continue
    grid_player[new_x + 1][new_y + 1][1] = 1
    return new_x, new_y


def choice_from_four():
    #случайный выбор одной из четырех клеток после первого попадания
    flag = True
    while flag:
        delta = random.randrange(-1, 2, 2)
        direct = random.randint(0, 1)
        # 0 - направление по х
        # 1 - направление по у
        if direct == 0:
            if check_possibility(choices[0][0] + delta, choices[0][1]):
                new_x = choices[0][0] + delta
                new_y = choices[0][1]
                flag = False
            else:
                continue
        if direct == 1:
            if check_possibility(choices[0][0], choices[0][1] + delta):
                new_x = choices[0][0]
                new_y = choices[0][1] + delta
                flag = False
            else:
                continue
    grid_player[new_x + 1][new_y + 1][1] = 1
    return new_x, new_y, direct


def choice_from_two():
    #случайный выбор из двух клеток после двух и более попаданий
    flag = True
    while flag:
        delta = random.randrange(-1, len(choices) + 1, len(choices) + 1)
        if direction == 0:
            new_x = choices[0][0] + delta
            new_y = choices[0][1]
        else:
            new_x = choices[0][0]
            new_y = choices[0][1] + delta
        if check_possibility(new_x, new_y):
            flag = False
        else:
            continue
    grid_player[new_x + 1][new_y + 1][1] = 1
    return new_x, new_y


def check_killing(points: list = choices, grid: list = grid_player, direct: int = direction):
    #проверка на уничтожение корабля
    global choices, direction, player_direction, player_picking
    if len(points) == 1:
        if (grid[points[0][0] + 2][points[0][1] + 1][0] == 2) and (grid[points[0][0]][points[0][1] + 1][0] == 2) and (
                grid[points[0][0] + 1][points[0][1] + 2][0] == 2) and (grid[points[0][0] + 1][points[0][1]][0] == 2):
            return True, Geometry(0, 'vert')
        else:
            return False, Geometry(0, 'vert')
    elif len(points) > 1 and direct == 0:
        if (grid[points[0][0]][points[0][1] + 1][0] == 2) and (
                grid[points[0][0] + len(points) + 1][points[0][1] + 1][0] == 2):
            return True, Geometry(len(points) - 1, 'hor')
        else:
            return False, Geometry(0, 'vert')
    elif len(points) > 1 and direct == 1:
        if (grid[points[0][0] + 1][points[0][1]][0] == 2) and (
                grid[points[0][0] + 1][points[0][1] + len(points) + 1][0] == 2):
            return True, Geometry(len(points) - 1, 'vert')
        else:
            return False, Geometry(0, 'vert')


def computer_turn():
    #алгоритм для хода компьютера
    time.sleep(1)
    global choices, direction, turn
    if len(choices) == 0:
        x, y = random_choice()
        d = '_'
    elif len(choices) == 1:
        x, y, d = choice_from_four()
    elif len(choices) > 1:
        x, y = choice_from_two()
        d = copy(direction)
    draw_picked(x + 1, y + 1)
    if grid_player[x + 1][y + 1][0] == 1:
        choices.append((x, y))
        direction = d
        if len(choices) > 1:
            sort_choices(points=choices, direct=direction)
        L = check_killing(points=choices, grid=grid_player, direct=direction)
        if L[0]:
            shape = L[1]
            shape.draw_rect(choices[0][0] + 1, choices[0][1] + 1, (200, 40, 40))
            shape.set_picked_value(choices[0][0], choices[0][1], grid_player)
            choices = []
            direction = '_'
    else:
        turn = 0


def check_picking(x, y):
    #проверка на наличие попаданий вокруг выбранной клетки и записи их в список
    list = [(x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y)]
    for l in list:
        if grid_computer[l[0] + 1][l[1] + 1][0] == 1 and grid_computer[l[0] + 1][l[1] + 1][1] == 1:
            if l not in player_picking:
                player_picking.append(l)
        else:
            continue


def collect_picking(x, y):
    #запись в список подряд стоящих попаданий
    global player_picking, player_direction
    player_picking = [(x, y)]
    i = 0
    while len(player_picking) < 5:
        try:
            check_picking(player_picking[i][0], player_picking[i][1])
            i += 1
        except:
            break
    if len(player_picking) != 1:
        if player_picking[0][0] == player_picking[1][0]:
            player_direction = 1
        else:
            player_direction = 0


def player_turn():
    #алгоритм для хода игрока
    global player_picking, player_direction, turn, player_cell
    x = player_cell[0] - 1
    y = player_cell[1] - 12
    if grid_computer[x + 1][y + 1][0] == 1:
        draw_picked(x + 1, y + 12)
        collect_picking(x, y)
        if len(player_picking) > 1:
            sort_choices(points=player_picking, direct=player_direction)
        L = check_killing(points=player_picking, grid=grid_computer, direct=player_direction)
        x = player_picking[0][0]
        y = player_picking[0][1]
        player_picking = []
        player_direction = '_'
        if L[0]:
            shape = L[1]
            shape.draw_rect_area(x + 1, y + 12)
            shape.draw_rect(x + 1, y + 12, color=(200, 40, 40))
            shape.set_picked_value(x, y, grid_computer)
    else:
        turn = 1


def sum_cells(position: int = 0):
    #сумма всех единиц означающих наличие корабля или выбора клетки
    S = 0
    for L in range(len(grid_player)):
        for H in range(len(grid_player[L])):
            if grid_player[L][H][position] == 1:
                S += grid_player[L][H][position]
    return S


def sum_kills(grid):
    #сумма попаданий
    S = 0
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if grid[i][j][0] == 1 and grid[i][j][1] == 1:
                S += 1
    return S


def take_shape(direct: str):
    #выбор фигуры в зависимости от заполнения поля
    if sum_cells() == 0:
        Shape = Geometry(3, direct)
    elif 4 <= sum_cells() < 10:
        Shape = Geometry(2, direct)
    elif 10 <= sum_cells() < 16:
        Shape = Geometry(1, direct)
    elif 16 <= sum_cells() < 20:
        Shape = Geometry(0, direct)
    else:
        Shape = False
    return Shape


def draw_shapes(grid: list = grid_player, color=(80, 60, 230)):
    #рисование всех установленных фигур и выбранных полей
    for i in range(12):
        for j in range(12):
            if grid[i][j][0] == 1:
                pygame.draw.rect(screen, pygame.Color(color),
                                 pygame.Rect(i * cell, j * cell, cell, cell), 0)
                pygame.draw.rect(screen, pygame.Color(145, 145, 145),
                                 pygame.Rect(i * cell, j * cell, cell, cell), 1)


random_field()
draw_wire()

#начальные переменные для начала игры
x = 4
y = 4
shape_direct = 'hor'
X = 4
Y = 16

while True:
    #основная логика игры
    if bool(take_shape(shape_direct)):
        shape = take_shape(shape_direct)
        shape.draw_rect(x, y)
        draw_shapes()
    else:
        x, y = X, Y
        shape = Geometry(0, 'hor')
        if turn == 1:
            print(f'Ваши очки {sum_kills(grid_computer)}')
            print(f'Очки компьютера {sum_kills(grid_player)}')
            computer_turn()
        elif turn == 0:
            shape.draw_rect(x, y, width=1, color=(10, 10, 10))
            if len(player_cell) == 0:
                pass
            else:
                print(f'Ваши очки {sum_kills(grid_computer)}')
                print(f'Очки компьютера {sum_kills(grid_player)}')
                player_turn()
                player_cell = []
        else:
            pass

    #управление клавишами
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if bool(take_shape(shape_direct)):
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    shape.del_rect(x, y)
                    if x > 1:
                        x -= 1
                elif event.key == pygame.K_RIGHT:
                    shape.del_rect(x, y)
                    if shape.check_position(x, y - 1):
                        x += 1
                elif event.key == pygame.K_DOWN:
                    shape.del_rect(x, y)
                    if shape.check_position(x - 1, y):
                        y += 1
                elif event.key == pygame.K_UP:
                    shape.del_rect(x, y)
                    if y > 1:
                        y -= 1
                elif event.key == pygame.K_SPACE:
                    shape.del_rect(x, y)
                    shape.turn()
                    shape_direct = shape.direction
                    if not shape.check_position(x - 1, y - 1):
                        if shape.direction == 'hor':
                            x = 10 - shape.length
                        else:
                            y = 10 - shape.length
                elif event.key == pygame.K_RSHIFT:
                    if shape.check_intersection(x - 1, y - 1):
                        shape.set_value(x - 1, y - 1, grid_player)
                        x = 4
                        y = 4
        else:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    draw_wire()
                    if X > 1:
                        X -= 1
                elif event.key == pygame.K_RIGHT:
                    draw_wire()
                    if X < 10:
                        X += 1
                elif event.key == pygame.K_DOWN:
                    draw_wire()
                    if Y < 21:
                        Y += 1
                elif event.key == pygame.K_UP:
                    draw_wire()
                    if Y > 12:
                        Y -= 1
                elif event.key == pygame.K_RSHIFT:
                    if grid_computer[X][Y - 11][1] == 0:
                        player_cell = [X, Y]
                        grid_computer[X][Y - 11][1] = 1
                        draw_picked(X, Y, color=(145, 145, 145))

    #определение победителя
    if sum_kills(grid_player) == 20:
        draw_screen()
        font = pygame.font.SysFont('couriernew', 40, bold=True)
        num = font.render('Вы проиграли', True, (200, 0, 0))
        screen.blit(num, (4, 5 * cell))
        turn = 2

    if sum_kills(grid_computer) == 20:
        draw_screen()
        font = pygame.font.SysFont('couriernew', 40, bold=True)
        num = font.render('Вы выйграли', True, (10, 10, 100))
        screen.blit(num, (17, 16 * cell))
        turn = 2

    #инструкции
    pygame.draw.rect(screen, pygame.Color(255, 255, 255),
                     pygame.Rect(0, 23 * cell, cell * 12, cell * 4),0)
    pygame.draw.rect(screen, pygame.Color(0, 0, 0),
                     pygame.Rect(0, 23 * cell, cell * 12, cell * 4), 2)

    font = pygame.font.SysFont('couriernew', 15, bold=True)
    str1 = font.render('Упраление:', True, (0, 0, 0))
    screen.blit(str1, (4 * cell, 23 * cell))
    str2 = font.render('перемещение с помощью стрелок', True, (0, 0, 0))
    screen.blit(str2, (0.8 * cell, 24 * cell))
    str3 = font.render('поворот элемента - "Space"', True, (0, 0, 0))
    screen.blit(str3, (1.3 * cell, 25 * cell))
    str4 = font.render('выбор позиции - "Shift"', True, (0, 0, 0))
    screen.blit(str4, (1.8 * cell, 26 * cell))


    pygame.display.flip()
    clock.tick(fps)
