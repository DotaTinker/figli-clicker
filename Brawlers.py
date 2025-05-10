import random
import math
from pygame.time import wait

"""classes_persent = {"healer": 25, "damage_dealer": 25, "sniper": 25, "tank": 25}
classes_strike = {"healer": 0, "damage_dealer": 0, "sniper": 0, "tank": 0}
rarity_percents = {"rare": 1, "super_rare": 0.7, "epic": 0.5, "mythic": 0.25, "legendary": 0.04, "": 97.51}
rarity_strike = {"rare": 0, "super_rare": 0, "epic": 0, "mythic": 0, "legendary": 0, "": 0}"""

def chance_class_changer(_class, classes_persent, classes_strike):
    classes_persent_2 = classes_persent.copy()
    persent = classes_persent_2.pop(_class)
    strike = classes_strike[_class]
    strike += 1
    for key in classes_strike.keys():
        if key != _class:
            classes_strike[key] = 0
        else:
            classes_strike[key] = strike
    minus = strike * random.randrange(7, 13, 1) / 10
    persent -= minus
    classes_persent_2 = [(key, value) for key, value in sorted(classes_persent_2.items(), key=lambda item: item[1])]

    # 25, 25, 25
    if classes_persent_2[0][1] == classes_persent_2[1][1] == classes_persent_2[2][1]:
        amounts = []
        amounts.extend([minus // 3] * 3)
        amounts[random.choice([0, 1, 2])] += minus % 3
    # 20, 20, 60
    elif classes_persent_2[0][1] == classes_persent_2[1][1] and classes_persent_2[2][1] > classes_persent_2[0][1]:
        p1 = random.randrange(40, 45, 1)
        p2 = random.randrange(40, 45, 1)
        p3 = 100 - p1 - p2
        amounts = [(minus / 100) * p2, (minus / 100) * p1, (minus / 100) * p3]
    # 20, 40, 40
    elif classes_persent_2[0][1] < classes_persent_2[2][1] and classes_persent_2[1][1] == classes_persent_2[2][1]:
        p1 = random.randrange(70, 80, 1)
        p2 = random.randrange(8, 12, 1)
        p3 = 100 - p1 - p2
        amounts = [(minus / 100) * p2, (minus / 100) * p1, (minus / 100) * p3]
    # 20, 30, 50
    else:
        p1 = random.randrange(50, 60, 1)
        p2 = random.randrange(25, 35, 1)
        p3 = 100 - p1 - p2
        amounts = [(minus / 100) * p2, (minus / 100) * p1, (minus / 100) * p3]

    classes_persent_2 = {key: value for key, value in classes_persent_2}

    for i, key_value in enumerate(classes_persent_2.items()):
        classes_persent[key_value[0]] += amounts[i]
    classes_persent[_class] = persent

    if sum(classes_persent.values()) != 100:
        classes_persent[random.choice(list(classes_persent.keys()))] += 100 - sum(
            classes_persent.values())
    return classes_persent, classes_strike

def chance_rarity_changer(_rarity, rarity_strike, rarity_percents):
    for k in rarity_strike.keys():
        if k != _rarity:
            rarity_strike[k] = 0
        else:
            rarity_strike[k] += 1
    if not _rarity:
        minus = (1 - math.e ** (-0.05 * math.log(rarity_strike[_rarity] + 1))) / 10
    elif _rarity == "rare":
        minus = rarity_strike[_rarity] ** 0.2 / 10
    elif _rarity == "super_rare":
        minus = math.atan(0.2 * rarity_strike[_rarity]) / (math.pi / 2)
    elif _rarity == "epic":
        minus = 1 - math.e ** (-0.1 * rarity_strike[_rarity])
    elif _rarity == "mythic":
        minus = (((0.01 * rarity_strike[_rarity]) * 2 * rarity_strike[_rarity] + (0.01 * rarity_strike[_rarity]) * (1 - math.e ** (-0.1 * rarity_strike[_rarity]))) / (
                1 - math.e ** (-0.05 * math.log(rarity_strike[_rarity] + 1) * math.atan(0.2 * rarity_strike[_rarity]) / (math.pi / 2)))) / 40
    else:
        minus = 0.1488 + random.randrange(228, 488) / 100 * rarity_strike[_rarity]
    rarity_percents[_rarity] -= minus
    if rarity_percents[_rarity] < 0:
        rarity_percents[_rarity] = 0
    for k in rarity_percents.keys():
        if k != _rarity:
            if k == "legendary":
                rarity_percents[k] += minus / 100 * (random.randrange(200, 300)) / 100
            elif k == "rare":
                rarity_percents[k] += minus / 100 * 20
            elif k == "super_rare":
                rarity_percents[k] += minus / 100 * 16
            elif k == "epic":
                rarity_percents[k] += minus / 100 * 8
            elif k == "mythic":
                rarity_percents[k] += minus / 100 * 5
            else:
                rarity_percents[k] += minus / 100 * 50
    a = 100 - sum(rarity_percents.values())
    rarity_percents[random.choices(list(rarity_percents.keys()))[0]] += a
    return rarity_strike, rarity_percents

class BaseBrawler:
    def __init__(self, rarity, team, x, y):
        self.team = team
        self.x = x
        self.y = y
        self.rarity = rarity
        self.extra_damage_chance = {"extra": 5, "": 95}
        self.extra_damage_strike = {"extra": 0, "": 0}
        self.last_amounts = []
        self.xps = []
        if isinstance(self, Healer):
            self.f = self.init_2()
        else:
            self.init_2()

    def ex_dmg_chance_changer(self, was):
        """На вход подаётся, что выпало, выпал ли доп урон, или ничего, функция просто меняет веса, т.е шанс."""
        if was == "":
            self.extra_damage_strike[""] += 1
            self.extra_damage_strike["extra"] = 0
            minus = random.randrange(1 + self.extra_damage_strike[""], 3 + self.extra_damage_strike[""]) / 10 * self.extra_damage_strike[""]
            self.extra_damage_chance[""] -= minus
            self.extra_damage_strike["extra"] = 100 - self.extra_damage_chance[""]
        else:
            self.extra_damage_strike["extra"] += 1
            self.extra_damage_strike[""] = 0
            minus = self.extra_damage_strike["extra"] * (random.randrange(1 + self.extra_damage_strike["extra"], 2 + self.extra_damage_strike["extra"]) / 10)
            self.extra_damage_chance["extra"] -= minus
            if self.extra_damage_chance["extra"] < 0:
                self.extra_damage_chance["extra"] = 0
            self.extra_damage_chance[""] = 100 - self.extra_damage_chance["extra"]

    def hit(self, amount, field):
        self.xp -= amount
        self.xps.append(self.xp)
        if self.xp <= 0:
            field.kill(self.x, self.y)

    def did_i_win(self, field):
        if self.team == "blue":
            if self.y == 0:
                field.winner = "blue"
        else:
            if self.y == 9:
                field.winner = "red"

    def get_enemy_on_my_range_line(self, field):
        if self.team == "blue":
            for i in range(1, self.attack_range + 1):
                try:
                    if field.field[self.y - i][self.x] != 0:
                        if field.field[self.y - i][self.x].team != self.team:
                            return (self.y - i, self.x)
                except IndexError:
                    break
        else:
            for i in range(1, self.attack_range + 1):
                try:
                    if field.field[self.y + i][self.x] != 0:
                        if field.field[self.y + i][self.x].team != self.team:
                            return (self.y + i, self.x)
                except IndexError:
                    break

    def minus_1_y_error(self):
        return True if self.y - 1 == -1 else False

    def index_10_error(self):
        return True if self.y + 1 == 10 else False

    def motion(self, field, back=False):
        if not back:
            if self.team == "blue":
                if field.field[self.y - 1][self.x] == 0:
                    field._update(self.x, self.y, 0, self.x, self.y - 1, self)
                    self.y -= 1
            else:
                if field.field[self.y + 1][self.x] == 0:
                    field._update(self.x, self.y, 0, self.x, self.y + 1, self)
                    self.y += 1
        else:
            if self.team == "blue":
                if not self.index_10_error():
                    if field.field[self.y + 1][self.x] == 0:
                        field._update(self.x, self.y, 0, self.x, self.y + 1, self)
                        self.y += 1
            else:
                if not self.minus_1_y_error():
                    if field.field[self.y - 1][self.x] == 0:
                        field._update(self.x, self.y, 0, self.x, self.y - 1, self)
                        self.y -= 1
        self.did_i_win(field)


    def heal(self, amount):
        if self.xp + amount > self.xp_limit:
            self.xp = self.xp_limit
        else:
            self.xp += amount
        self.xps.append(self.xp)

class DamageDealer(BaseBrawler):
    def init_2(self):
        if self.rarity == "rare":
            self.xp = random.randrange(1200, 1300, 20)
            self.attack_range = 3
        elif self.rarity == "super_rare":
            self.xp = random.randrange(1700, 1800, 20)
            self.attack_range = 3
        elif self.rarity == "epic":
            self.xp = random.randrange(2460, 2540, 40)
            self.attack_range = 3
        elif self.rarity == "mythic":
            self.xp = random.randrange(3200, 2380, 60)
            self.attack_range = 4
        else: # elif self.rarity == "legendary":
            self.xp = 3800
            self.attack_range = 5
        self.xp_limit = self.xp

    def attack(self, field):
        enemy = self.get_enemy_on_my_range_line(field)
        if enemy:
            what = random.choices(list(self.extra_damage_chance.keys()),
                                  weights=list(self.extra_damage_chance.values()))
            if self.rarity == "rare":
                amount = random.randrange(570, 630, 2)
            elif self.rarity == "super_rare":
                amount = random.randrange(780, 820, 2)
            elif self.rarity == "epic":
                amount = random.randrange(1300, 1390, 2)
            elif self.rarity == "mythic":
                amount = random.randrange(1700, 1800, 5)
            else:
                amount = random.randrange(2100, 2160, 10)
            if what:
                amount += amount / 100 * (20 * ((10 - self.extra_damage_strike["extra"]) / 10))
            self.ex_dmg_chance_changer(what)
            self.last_amounts.append([str(amount), what])
            field.field[enemy[0]][enemy[1]].hit(amount, field)
        else:
            self.motion(field)

    def step(self, field):
        self.attack(field)

class Sniper(BaseBrawler):
    def init_2(self):
        if self.rarity == "rare":
            self.xp = random.randrange(1200, 1300, 20)
            self.attack_range = 5
        elif self.rarity == "super_rare":
            self.xp = random.randrange(1700, 1800, 20)
            self.attack_range = 6
        elif self.rarity == "epic":
            self.xp = random.randrange(2460, 2540, 40)
            self.attack_range = 7
        elif self.rarity == "mythic":
            self.xp = random.randrange(3200, 2380, 60)
            self.attack_range = 7
        else: # elif self.rarity == "legendary":
            self.xp = 3800
            self.attack_range = 8
        self.xp_limit = self.xp

    def minus_percents(self, dist):
        return 50 / (self.attack_range - 1) * (dist - 1) + 50

    def attack(self, field):
        enemy = self.get_enemy_on_my_range_line(field)
        if enemy:
            what = random.choices(list(self.extra_damage_chance.keys()),
                                  weights=list(self.extra_damage_chance.values()))
            distance = abs(enemy[0] - self.y)
            if self.rarity == "rare":
                amount = random.randrange(570, 630, 2)
            elif self.rarity == "super_rare":
                amount = random.randrange(780, 820, 2)
            elif self.rarity == "epic":
                amount = random.randrange(1300, 1390, 2)
            elif self.rarity == "mythic":
                amount = random.randrange(1700, 1800, 5)
            else:
                amount = random.randrange(2100, 2160, 10)
            if what:
                amount += amount / 100 * (20 * ((10 - self.extra_damage_strike["extra"]) / 10))
            amount = (amount / 100) * self.minus_percents(distance)
            self.last_amounts.append([str(amount), what])
            self.ex_dmg_chance_changer(what)
            field.field[enemy[0]][enemy[1]].hit(amount, field)

            if self.rarity == "mythic" or self.rarity == "legendary":
                self.motion(field, back=True)
        else:
            self.motion(field)

    def step(self, field):
        self.attack(field)

class Tank(BaseBrawler):
    def init_2(self):
        if self.rarity == "rare":
            self.xp = random.randrange(4500, 4600, 20)
            self.attack_range = 2
        elif self.rarity == "super_rare":
            self.xp = random.randrange(5400, 5500, 20)
            self.attack_range = 2
        elif self.rarity == "epic":
            self.xp = random.randrange(6100, 6200, 100)
            self.attack_range = 2
        elif self.rarity == "mythic":
            self.xp = random.randrange(7000, 7300, 60)
            self.attack_range = 2
        else: # elif self.rarity == "legendary":
            self.xp = 8000
            self.attack_range = 3
        self.xp_limit = self.xp

    def attack(self, field):
        self.motion(field)
        enemy = self.get_enemy_on_my_range_line(field)
        if enemy:
            what = random.choices(list(self.extra_damage_chance.keys()),
                                  weights=list(self.extra_damage_chance.values()))
            distance = abs(enemy[0] - self.y)
            if self.rarity == "rare":
                amount = random.randrange(570, 630, 2)
            elif self.rarity == "super_rare":
                amount = random.randrange(780, 820, 2)
            elif self.rarity == "epic":
                amount = random.randrange(1300, 1390, 2)
            elif self.rarity == "mythic":
                amount = random.randrange(1700, 1800, 5)
            else:
                amount = random.randrange(2100, 2160, 10)
            if what:
                amount += amount / 100 * (20 * ((10 - self.extra_damage_strike["extra"]) / 10))
            if distance == 2:
                amount = (amount / 100) * 80
            elif distance == 3:
                amount = (amount / 100) * 60
            self.last_amounts.append([str(amount), what])
            self.ex_dmg_chance_changer(what)
            field.field[enemy[0]][enemy[1]].hit(amount, field)

    def step(self, field):
        self.attack(field)

class Healer(BaseBrawler):
    def h_f(self, field, delta_y, y, delta_x, x):
        try:
            if field.field[self.y + delta_y + y][self.x + delta_x + x] and field.field[self.y + delta_y + y][
                self.x + delta_x + x].team == self.team and field.field[self.y + delta_y + y][self.x + delta_x + x] != self:
                return field.field[self.y + delta_y + y][self.x + delta_x + x]
        except IndexError:
            pass

    def init_2(self):
        self.current_step = 0
        if self.rarity == "rare":
            self.step_count = 1
            self.xp = random.randrange(4500, 4600, 20)
            self.number_of_brawlers = 1
            def func(field):
                s = []
                for y in range(7):
                    a = self.h_f(field, -3, y, 0, 0)
                    s.append(a) if a else ...
                for x in range(-1, 2, 2):
                    for y in range(5):
                        a = self.h_f(field, -2, y, x, 0)
                        s.append(a) if a else ...
                return s
        elif self.rarity == "super_rare":
            self.step_count = 2
            self.xp = random.randrange(4500, 4600, 20)
            self.number_of_brawlers = 1
            def func(field):
                s = []
                for y in range(7):
                    a = self.h_f(field, -3, y, 0, 0)
                    s.append(a) if a else ...
                for x in range(-1, 2, 2):
                    for y in range(5):
                        a = self.h_f(field, -2, y, 0, x)
                        s.append(a) if a else ...
                for x in range(-2, 3, 4):
                    for y in range(3):
                        a = self.h_f(field, -1, y, 0, x)
                        s.append(a) if a else ...
                return s
        elif self.rarity == "epic":
            self.step_count = 3
            self.xp = random.randrange(4500, 4600, 20)
            self.number_of_brawlers = 2
            def func(field):
                s = []
                for x in range(-1, 2):
                    for y in range(11):
                        a = self.h_f(field, -5, y, 0, x)
                        s.append(a) if a else ...
                for delta_x in range(-2, 3, 4):
                    for x in range(2) if delta_x > 0 else range(0, -2, -1):
                        for y in range(9):
                            a = self.h_f(field, -4, y, delta_x, x)
                            s.append(a) if a else ...
                for x in range(-4, 5, 8):
                    for y in range(7):
                        a = self.h_f(field, -3, y, 0, x)
                        s.append(a) if a else ...
                return s
        elif self.rarity == "mythic":
            self.step_count = 6
            self.xp = random.randrange(4500, 4600, 20)
            self.number_of_brawlers = 3
            def func(field):
                s = []
                for x in range(-2, 3):
                    for y in range(15):
                        a = self.h_f(field, -7, y, 0, x)
                        s.append(a) if a else ...
                for delta_x in range(-3, 4, 6):
                    for x in range(2) if delta_x > 0 else range(0, -2, -1):
                        for y in range(13):
                            a = self.h_f(field, -6, y, delta_x, x)
                            s.append(a) if a else ...
                for delta_x in range(-5, 6, 10):
                    for x in range(2) if delta_x > 0 else range(0, -2, -1):
                        for y in range(11):
                            a = self.h_f(field, -5, y, delta_x, x)
                            s.append(a) if a else ...
                for x in range(-7, 15, 14):
                    for y in range(9):
                        a = self.h_f(field, -4, y, 0, x)
                        s.append(a) if a else ...
                return s
        else:
            self.step_count = 0
            self.xp = random.randrange(4500, 4600, 20)
            self.number_of_brawlers = 4
            def func(field):
                s = []
                _x, _y = self.x, self.y
                self.x, self.y = 0, 0
                for x in range(0, 10):
                    for y in range(0, 10):
                        a = self.h_f(field, 0, y, 0, x)
                        s.append(a) if a else ...
                self.x, self.y = _x, _y
        self.xp_limit = self.xp
        return func

    def attack(self, field):
        list_of_brawlers = sorted(self.f(field), key=lambda x: x.xp)
        for i in range(self.number_of_brawlers):
            try:
                brawler = list_of_brawlers[i]
                what = random.choices(list(self.extra_damage_chance.keys()),
                                      weights=list(self.extra_damage_chance.values()))
                if self.rarity == "rare":
                    amount = random.randrange(570, 630, 2)
                elif self.rarity == "super_rare":
                    amount = random.randrange(780, 820, 2)
                elif self.rarity == "epic":
                    amount = random.randrange(1300, 1390, 2)
                elif self.rarity == "mythic":
                    amount = random.randrange(1700, 1800, 5)
                else:
                    amount = random.randrange(2100, 2160, 10)
                if what:
                    amount += amount / 100 * (20 * ((10 - self.extra_damage_strike["extra"]) / 10))
                self.last_amounts.append([str(amount), what])
                self.ex_dmg_chance_changer(what)
                brawler.heal(amount)
            except IndexError:
                pass

    def step(self, field):
        self.current_step += 1
        if self.current_step == self.step_count:
            self.current_step = 0
            self.motion(field)
        self.attack(field)

    def json(self):
        return {
            "team": self.team,
            "rarity": self.rarity,
            "max_xp": self.xp_limit,
            "current_xp": self.xp,
            "extra_chance": self.extra_damage_chance,
            "extra_strike": self.extra_damage_strike,
            "xp_list": self.xps,
            "attack_list": self.last_amounts
        }

class Field:
    def __init__(self, first):
        self.field = [[0 for _ in range(10)] for _ in range(10)]
        if first == "blue":
            self.team_list = ["blue", "red"]
        else:
            self.team_list = ["red", "blue"]
        self.cursor_teams = 2
        self.winner = ""

    def add_brawler(self, brawler):
        self.field[brawler.y][brawler.x] = brawler

    def _update(self, old_x, old_y, old_to, new_x, new_y, new_to):
        self.field[old_y][old_x] = old_to
        self.field[new_y][new_x] = new_to

    def print_field(self):
        for el in self.field:
            row = []
            for ell in el:
                if isinstance(ell, DamageDealer):
                    row.append('D')
                elif isinstance(ell, Sniper):
                    row.append('S')
                elif isinstance(ell, Healer):
                    row.append('H')
                elif isinstance(ell, Tank):
                    row.append('T')
                else:
                    row.append("-")
            print(row)

    def create_team_lists(self):
        self.blue_list = []
        self.red_list = []
        for y in range(10):
            for x in range(10):
                if self.field[y][x] != 0:
                    if self.field[y][x].team == "blue":
                        self.blue_list.append(self.field[y][x])
        for y in range(9, -1, -1):
            for x in range(10):
                if self.field[y][x] != 0:
                    if self.field[y][x].team == "red":
                        self.red_list.append(self.field[y][x])

        self.cur_b, self.c_b = len(self.blue_list), len(self.blue_list)
        self.cur_r, self.c_r = len(self.red_list), len(self.red_list)

    def step(self):
        team = self.team_list[self.cursor_teams % 2]
        if team == "blue":
            self.blue_list[self.cur_b % self.c_b].step(self)
            self.cur_b += 1
        else:
            self.red_list[self.cur_r % self.c_r].step(self)
            self.cur_r += 1
        self.cursor_teams += 1

    def next_step(self):
        team = self.team_list[self.cursor_teams % 2]
        try:
            if team == "blue":
                return (self.blue_list[self.cur_b % self.c_b].y, self.blue_list[self.cur_b % self.c_b].x)
            return (self.red_list[self.cur_r % self.c_r].y, self.red_list[self.cur_r % self.c_r].x)
        except ZeroDivisionError:
            pass


    def kill(self, x, y):
        brawler = self.field[y][x]
        if brawler.team == "blue":
            index = self.blue_list.index(brawler)
            self.blue_list.remove(brawler)
            if index >= self.cur_b % self.c_b:
                a = 0
            else:
                a = -1
            self.cur_b = len(self.blue_list) * (self.cur_b // self.c_b) + self.cur_b % self.c_b + a
            self.c_b = len(self.blue_list)
        else:
            index = self.red_list.index(brawler)
            self.red_list.remove(brawler)
            if index >= self.cur_r % self.c_r:
                a = 0
            else:
                a = -1
            self.cur_r = len(self.red_list) * (self.cur_r // self.c_r) + self.cur_r % self.c_r + a
            self.c_r = len(self.red_list)
        self.field[y][x] = 0

        if not self.blue_list:
            self.team_list = ["red", "red"]
        if not self.red_list:
            self.team_list = ["blue", "blue"]

    def json(self):
        a = {}
        for y in range(10):
            for x in range(10):
                if self.field[y][x]:
                    y_x_next = self.next_step()
                    if y_x_next:
                        if y == y_x_next[0] and x == y_x_next[1]:
                            a[[str(y), str(x)], True] = self.field[y][x].json()
                    else:
                        a[[str(y), str(x)], False] = self.field[y][x].json()

class FieldTest:
    def __init__(self):
        self.field = [[0 for _ in range(31)] for _ in range(31)]

    def add_brawler(self, brawler):
        self.field[brawler.y][brawler.x] = brawler

    def print_field(self):
        for el in self.field:
            row = []
            for ell in el:
                if isinstance(ell, Healer):
                    row.append('H')
                elif isinstance(ell, Sniper):
                    row.append('S')
                elif ell == "!":
                    row.append(ell)
                else:
                    row.append("-")
            print(row)

"""
def ff(f, ll):
    for y in range(10):
        for x in range(10):
            if ll[y][x]:
                team = "blue" if ll[y][x][1] == 'b' else "red"
                if ll[y][x][0] == 's':
                    f.add_brawler(Sniper("legendary", team, x, y))
                if ll[y][x][0] == 'd':
                    f.add_brawler(DamageDealer("legendary", team, x, y))
                if ll[y][x][0] == 't':
                    f.add_brawler(Tank("legendary", team, x, y))
                if ll[y][x][0] == 'h':
                    f.add_brawler(Healer("epic", team, x, y))



matrix = [
    ['dr', 'sr', 'hr', 'tr', 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ['db', 'sb', 'hb', 'tb', 0, 0, 0, 0, 0, 0]
]
f = Field("blue")
ff(f, matrix)
f.create_team_lists()
while True:
    f.step()
    f.print_field()
    if f.winner:
        print(f.winner)
        break
    wait(5000)
    print()
    print()

"""
'''h = Healer("legs", "blue", 15, 15)
f2 = FieldTest()
f2.add_brawler(h)
h.attack(f2)
f2.print_field()'''