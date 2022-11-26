import numpy as np
import random
import copy
import math
import time


#mody ovladajuce program
class Modes:
    def __init__(self, print: bool, opt: bool, path: bool):
        self.NONE = 0
        self.PRINT = print
        self.OPTIMAL = opt
        self.PATH = path
        self.MINE = 3
        self.ROULETTE = 4
        self.ELITEROULETTE = 5


class Specimen:
    def __init__(self, chromozome):
        self.fitness = 0
        self.num_found = 0
        self.chromozome = chromozome
        self.path = None

    #inicializujem nahodny chromozome
    def initchromozome(self):
        self.chromozome = np.zeros(64, dtype=np.uint8)
        for i in range(64):
            self.chromozome[i] = random.getrandbits(8)

    def print(self):
        print("Fit: " + str(round(self.fitness, 3)) + " Pok: " + str(self.num_found) + " Dlz: " + str(
            int(len(self.path) / 2)) + " | " + self.path)

    #utility funkcia pri triedeni
    def getfit(self):
        return self.fitness

    #dve funkcie na pocitanie fitness
    def calcfit(self):
        if m.PATH:
            if len(self.path) == 0:
                self.fitness = 0
            else:
                res = (0.75 / _map.num_treasures) * self.num_found
                res += (0.25 / (len(self.path) / 2)) * self.num_found
                self.fitness = res
        else:
            self.fitness = (1 / _map.num_treasures) * self.num_found

    #kazdy gen ma danu % sancu na mutaciu
    def mutate(self, max_mutations):
        for i in range(64):
            chance = random.random() * 100
            if chance < max_mutations:
                self.chromozome[i] = random.getrandbits(8)


class Point:
    def __init__(self, y, x):
        self.x = x
        self.y = y


#virtualny stroj definovany podla zadania
class Machine:
    def __init__(self, start, gen):
        self.arr = copy.deepcopy(gen)
        self.path = ""
        self.position = copy.deepcopy(start)
        self.num_found = 0

    def generate(self):
        i = 0
        #ukazovatel
        actual = 0
        while i < 500 and self.num_found != _map.num_treasures:
            instruction = self.arr[actual] >> 6
            address = self.arr[actual] & 0b00111111

            if instruction == 0:
                self.inc(address)

            elif instruction == 1:
                self.dec(address)

            elif instruction == 2:
                actual = address

            else:
                #ak som vyskocil z hracej mriezky
                if self.move(address) == -1:
                    break
                if _map.pole[self.position.y][self.position.x]:
                    self.num_found += 1
                    _map.pole[self.position.y][self.position.x] = False
            actual += 1
            if actual % 64 == 0:
                actual = 0
            i += 1

    #inkrementujem cyklicky tak, aby som nemenil instrukciu
    def inc(self, address):
        if (self.arr[address] & 0b00111111) == 63:
            self.arr[address] &= 0b11000000
        else:
            self.arr[address] += 1

    # dekrementujem cyklicky tak, aby som nemenil instrukciu
    def dec(self, address):
        if (self.arr[address] & 0b00111111) == 0:
            self.arr[address] |= 0b00111111
        else:
            self.arr[address] += 1

    #pri vypise rovno robim pohyb, modifikujem startovaciu poziciu stroja
    def move(self, address):
        #orientujem sa podla poslednych dvoch bitov
        val = self.arr[address] & 0b00000011
        #idem dole
        if val == 0:
            self.path += "D "
            self.position.y += 1
            if self.position.y == _map.MAXY:
                return -1
        #idem vpravo
        elif val == 1:
            self.path += "P "
            self.position.x += 1
            if self.position.x == _map.MAXX:
                return -1
        #idem hore
        elif val == 2:
            self.path += "H "
            self.position.y -= 1
            if self.position.y == -1:
                return -1
        #idem vlavo
        else:
            self.path += "L "
            self.position.x -= 1
            if self.position.x == -1:
                return -1
        return 0


def cross_breed(j1, j2):
    sizes = [3, 5, 7, 11, 15]
    output = np.zeros(64, dtype=np.uint8)
    part = 0
    switch = True
    for i in range(64):
        #beriem si random casti
        if part == 0:
            #taky random aby som nevybehol z pola
            part = sizes[random.randint(0, 4)]
            #na striedacku beriem z jedneho a druheho
            switch = not switch

        if switch:
            output[i] = j1.chromozome[i]
        else:
            output[i] = j2.chromozome[i]
        part -= 1
    return output


#utility funkcia do popolvara :D
def generate_path(cesta):
    cesta += "x"
    x = _map.start_pos.x
    y = _map.start_pos.y
    for c in cesta:
        if c == " ":
            continue
        print(str(x) + " " + str(y))
        if c == "P":
            x += 1
        if c == "H":
            y -= 1
        if c == "D":
            y += 1
        if c == "L":
            x -= 1


class Population:
    def __init__(self, num_gen, num_spec, num_mut):
        self.generation = None
        self.elite = None
        self.num_gen = num_gen
        self.num_spec = num_spec
        self.num_mut = num_mut
        #elite je vzdy 5% populacie
        self.num_elite = int(math.ceil((num_spec / 100) * 5))

    def initialize(self):
        i = 0
        self.generation = []
        self.elite = []
        while i < self.num_spec:
            _map.reset_treasures()

            specimen = Specimen(None)
            specimen.initchromozome()

            m1 = Machine(_map.start_pos, specimen.chromozome)
            m1.generate()

            specimen.path = m1.path
            specimen.num_found = m1.num_found
            specimen.calcfit()
            self.generation.append(specimen)
            i += 1

        self.generation.sort(key=Specimen.getfit)

        if MODE == m.MINE:
            for i in range(self.num_spec - self.num_elite, self.num_spec):
                self.elite.append(self.generation[i])

        if m.PRINT:
            self.print_top()
            if MODE == m.MINE:
                self.print_elite()

    def print_top(self):
        for i in range(self.num_spec - 10, self.num_spec):
            self.generation[i].print()

    def store_elite(self):
        # ukladam unikatnu elitu
        for i in range(self.num_spec - self.num_elite, self.num_spec):
            for j in range(0, self.num_elite):
                if self.elite[j].path == self.generation[i].path:
                    break

                if self.elite[j].fitness < self.generation[i].fitness:
                    self.elite[j] = copy.deepcopy(self.generation[i])
                    break

    def print_elite(self):
        print("ELITA-----")
        for x in self.elite:
            x.vypis()

    def create_elite_specimen(self):
        count = 0
        # prvych x bude elite x top10%
        top10 = int(math.ceil(9 * self.num_spec / 10))
        for i in range(top10, self.num_spec):
            for j in range(0, self.num_elite):
                specimen = Specimen(cross_breed(self.generation[i], self.elite[j]))
                specimen.mutate(self.num_mut)
                self.generation[count] = specimen
                count += 1
        remainder = self.num_spec - count
        # dalsich x bude vyskladanych z 75% - 90% najlepsich
        for i in range(remainder):
            s1 = random.randint(int(3 * self.num_spec / 4), int(math.ceil(9 * self.num_spec / 10)))
            s2 = random.randint(int(3 * self.num_spec / 4), int(math.ceil(9 * self.num_spec / 10)))
            specimen = Specimen(cross_breed(self.generation[s1], self.generation[s2]))
            specimen.mutate(self.num_mut)
            self.generation[count] = specimen
            count += 1

    def create_specimen_roulette(self):
        sumf = 0
        newgen = []
        count = 0
        for x in self.generation:
            sumf += x.fitness

        if MODE == m.ELITEROULETTE:
            for i in range(self.num_spec - self.num_elite, self.num_spec):
                newgen.append(copy.deepcopy(self.generation[i]))
                count += 1

        for j in range(self.num_spec - count):
            p1 = self.get_roulette_parent(sumf)
            p2 = self.get_roulette_parent(sumf)
            new_spec = Specimen(cross_breed(p1, p2))
            new_spec.mutate(self.num_mut)
            newgen.append(new_spec)

        self.generation = newgen

    def get_roulette_parent(self, sumf):
        chance = random.random() * sumf

        partf = 0
        for i in range(self.num_spec - 1, -1, -1):
            partf += self.generation[i].fitness
            if partf > chance:
                return self.generation[i]
        return self.generation[0]


#mapa je 2D arr False hodnot, kde True su len poklady
class Map:
    def __init__(self, maxy, maxx, sy, sx):
        self.pole = None
        self.MAXX = maxx
        self.MAXY = maxy
        self.num_treasures = 0
        self.treasures_positions = []
        self.start_pos = Point(sy, sx)

    def initialize(self):
        self.MAXX = 7
        self.MAXY = 7

        self.pole = np.full((self.MAXX, self.MAXY), False)

        #definujem suradnice pokladov
        self.treasures_positions.append(Point(5, 4))
        self.treasures_positions.append(Point(4, 1))
        self.treasures_positions.append(Point(3, 6))
        self.treasures_positions.append(Point(2, 2))
        self.treasures_positions.append(Point(1, 4))
        self.num_treasures = len(self.treasures_positions)

    #po kazdom prejdeni obnovujem poklady
    def reset_treasures(self):
        for sur in self.treasures_positions:
            self.pole[sur.y][sur.x] = True


def solve():
    global averages
    population.initialize()
    gen_counter = 1
    optimal = copy.deepcopy(population.generation[population.num_spec - 1])
    while gen_counter < population.num_gen:
        if m.PRINT:
            print("------ Generacia: " + str(gen_counter) + ", " + str(len(population.generation)))

        if MODE == m.MINE:
            population.create_elite_specimen()
        elif MODE == m.ROULETTE or MODE == m.ELITEROULETTE:
            population.create_specimen_roulette()

        #generovanie rieseni
        for i in range(population.num_spec):
            _map.reset_treasures()

            m1 = Machine(_map.start_pos, population.generation[i].chromozome)
            m1.generate()

            population.generation[i].path = m1.path
            population.generation[i].num_found = m1.num_found
            population.generation[i].calcfit()

        population.generation.sort(key=Specimen.getfit)

        #ukladam optimalneho jedinca ak je zvolene
        if m.OPTIMAL and population.generation[population.num_spec - 1].fitness > optimal.fitness:
            optimal = copy.deepcopy(population.generation[population.num_spec - 1])

        #ukladam elitu pre moje riesenie
        if MODE == m.MINE:
            population.store_elite()

        #ak som nasiel riesenie a nehladam optimalne tak koncim
        if not m.OPTIMAL and population.generation[population.num_spec - 1].num_found == _map.num_treasures:
            print("Riesenie najdene v generacii " + str(gen_counter))
            population.generation[population.num_spec - 1].print()
            # generujcestu(population.generation[population.num_spec - 1].path)
            return gen_counter

        #vypisujem top 10 jedincov
        if m.PRINT:
            population.print_top()
            if MODE == m.MINE:
                population.print_elite()

        gen_counter += 1

    #ked skoncili vsetky generacie vypisujem najoptimalnejsie riesenie
    if m.OPTIMAL:
        print("Najoptimalnejsie riesenie:")
        optimal.vypis()
        if optimal.num_found == 5:
            averages.append(len(optimal.path) / 2)
        else:
            averages.append(0)
        # generujcestu(population.elite[0].path)
    return gen_counter


def run():
    f = open("vystup.txt", "a")
    global averages
    _map.initialize()

    average = 0
    avg_count = 0
    xxx = 0
    totalt = 0

    while xxx < num_repeats:
        bt = time.time()
        print("Beh " + str(xxx))
        found = solve()
        et = time.time()

        if population.generation[population.num_spec - 1].num_found != _map.num_treasures:
            print("Riesenie nebolo najdene")
        else:
            avg_count += 1
            totalt += et - bt
            average += found
        xxx += 1

    print("Vysledok nebol najdeny " + str(xxx - avg_count) + " krat z " + str(xxx) + " pokusov")
    f.write("Vysledok nebol najdeny " + str(xxx - avg_count) + " krat z " + str(xxx) + " pokusov")

    if avg_count == 0:
        avg_count = 1
    print("Vysledok najdeny priemerne v generacii: " + str(average / avg_count))
    print("Priemerne trvanie: " + str(totalt / avg_count))

    f.close()


#vypisy, optimalne hladanie, path
m = Modes(False, False, False)
MODE = m.MINE
#pocetGeneracii, num_spec, max%Mutacii
population = Population(200, 100, 1.5)

#maxY, maxX, startY, startX
_map = Map(7, 7, 6, 3)

num_repeats = 1

averages = []
run()
