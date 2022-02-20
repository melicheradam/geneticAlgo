import numpy as np
import random
import copy
import math
import time


#mody ovladajuce program
class Mody:
    def __init__(self, vypis, opt, ces):
        self.ZIADNY = 0
        self.VYPIS = vypis
        self.OPTIMAL = opt
        self.CESTA = ces
        self.MOJE = 3
        self.RULETA = 4
        self.ELITERULETA = 5


class Jedinec:
    def __init__(self, chromozom):
        self.fitness = 0
        self.pocetnajdenych = 0
        self.chromozom = chromozom
        self.cesta = None

    #inicializujem nahodny chromozom
    def initchromozom(self):
        self.chromozom = np.zeros(64, dtype=np.uint8)
        for i in range(64):
            self.chromozom[i] = random.getrandbits(8)

    def vypis(self):
        print("Fit: " + str(round(self.fitness, 3)) + " Pok: " + str(self.pocetnajdenych) + " Dlz: " + str(
            int(len(self.cesta) / 2)) + " | " + self.cesta)

    #utility funkcia pri triedeni
    def getfit(self):
        return self.fitness

    #dve funkcie na pocitanie fitness
    def calcfit(self):
        if m.CESTA:
            if len(self.cesta) == 0:
                self.fitness = 0
            else:
                res = (0.75 / mapa.pocetPokladov) * self.pocetnajdenych
                res += (0.25 / (len(self.cesta) / 2)) * self.pocetnajdenych
                self.fitness = res
        else:
            self.fitness = (1 / mapa.pocetPokladov) * self.pocetnajdenych

    #kazdy gen ma danu % sancu na mutaciu
    def zmutuj(self, maxpocetmutacii):
        for i in range(64):
            sanca = random.random() * 100
            if sanca < maxpocetmutacii:
                self.chromozom[i] = random.getrandbits(8)


class Suradnica:
    def __init__(self, y, x):
        self.x = x
        self.y = y


#virtualny stroj definovany podla zadania
class Stroj:
    def __init__(self, start, gen):
        self.pole = copy.deepcopy(gen)
        self.cesta = ""
        self.pozicia = copy.deepcopy(start)
        self.pocetNajdenych = 0

    def generuj(self):
        i = 0
        #ukazovatel
        ukaz = 0
        while i < 500 and self.pocetNajdenych != mapa.pocetPokladov:
            instrukcia = self.pole[ukaz] >> 6
            adresa = self.pole[ukaz] & 0b00111111

            if instrukcia == 0:
                self.inc(adresa)

            elif instrukcia == 1:
                self.dec(adresa)

            elif instrukcia == 2:
                ukaz = adresa

            else:
                #ak som vyskocil z hracej mriezky
                if self.move(adresa) == -1:
                    break
                if mapa.pole[self.pozicia.y][self.pozicia.x]:
                    self.pocetNajdenych += 1
                    mapa.pole[self.pozicia.y][self.pozicia.x] = False
            ukaz += 1
            if ukaz % 64 == 0:
                ukaz = 0
            i += 1

    #inkrementujem cyklicky tak, aby som nemenil instrukciu
    def inc(self, adresa):
        if (self.pole[adresa] & 0b00111111) == 63:
            self.pole[adresa] &= 0b11000000
        else:
            self.pole[adresa] += 1

    # dekrementujem cyklicky tak, aby som nemenil instrukciu
    def dec(self, adresa):
        if (self.pole[adresa] & 0b00111111) == 0:
            self.pole[adresa] |= 0b00111111
        else:
            self.pole[adresa] += 1

    #pri vypise rovno robim pohyb, modifikujem startovaciu poziciu stroja
    def move(self, adresa):
        #orientujem sa podla poslednych dvoch bitov
        val = self.pole[adresa] & 0b00000011
        #idem dole
        if val == 0:
            self.cesta += "D "
            self.pozicia.y += 1
            if self.pozicia.y == mapa.MAXY:
                return -1
        #idem vpravo
        elif val == 1:
            self.cesta += "P "
            self.pozicia.x += 1
            if self.pozicia.x == mapa.MAXX:
                return -1
        #idem hore
        elif val == 2:
            self.cesta += "H "
            self.pozicia.y -= 1
            if self.pozicia.y == -1:
                return -1
        #idem vlavo
        else:
            self.cesta += "L "
            self.pozicia.x -= 1
            if self.pozicia.x == -1:
                return -1
        return 0


def krizenie(j1, j2):
    velkosti = [3, 5, 7, 11, 15]
    vysledny = np.zeros(64, dtype=np.uint8)
    cast = 0
    switch = 1
    for i in range(64):
        #beriem si random casti
        if cast == 0:
            #taky random aby som nevybehol z pola
            cast = velkosti[random.randint(0, 4)]
            #na striedacku beriem z jedneho a druheho
            if switch == 1:
                switch = 2
            else:
                switch = 1

        if switch == 1:
            vysledny[i] = j1.chromozom[i]
        else:
            vysledny[i] = j2.chromozom[i]
        cast -= 1
    return vysledny


#utility funkcia do popolvara :D
def generujcestu(cesta):
    cesta += "x"
    x = mapa.startPoz.x
    y = mapa.startPoz.y
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


class Populacia:
    def __init__(self, pocetg, pocetj, pocetm):
        self.generacia = None
        self.elita = None
        self.maxpocetgeneracii = pocetg
        self.pocetJedincov = pocetj
        self.pocetMutacii = pocetm
        #elita je vzdy 5% populacie
        self.pocetelita = int(math.ceil((pocetj / 100) * 5))

    def inicializuj(self):
        i = 0
        self.generacia = []
        self.elita = []
        while i < self.pocetJedincov:
            mapa.resetpoklady()

            jedinec = Jedinec(None)
            jedinec.initchromozom()

            m1 = Stroj(mapa.startPoz, jedinec.chromozom)
            m1.generuj()

            jedinec.cesta = m1.cesta
            jedinec.pocetnajdenych = m1.pocetNajdenych
            jedinec.calcfit()
            self.generacia.append(jedinec)
            i += 1

        self.generacia.sort(key=Jedinec.getfit)

        if MODE == m.MOJE:
            for i in range(self.pocetJedincov - self.pocetelita, self.pocetJedincov):
                self.elita.append(self.generacia[i])

        if m.VYPIS:
            self.vypistop()
            if MODE == m.MOJE:
                self.vypiselitu()

    def vypistop(self):
        for i in range(self.pocetJedincov - 10, self.pocetJedincov):
            self.generacia[i].vypis()

    def ulozelitu(self):
        # ukladam unikatnu elitu
        for i in range(self.pocetJedincov - self.pocetelita, self.pocetJedincov):
            for j in range(0, self.pocetelita):
                if self.elita[j].cesta == self.generacia[i].cesta:
                    break

                if self.elita[j].fitness < self.generacia[i].fitness:
                    self.elita[j] = copy.deepcopy(self.generacia[i])
                    break

    def vypiselitu(self):
        print("ELITA-----")
        for x in self.elita:
            x.vypis()

    def vytvorjedinceelita(self):
        count = 0
        # prvych x bude elita x top10%
        top10 = int(math.ceil(9 * self.pocetJedincov / 10))
        for i in range(top10, self.pocetJedincov):
            for j in range(0, self.pocetelita):
                jedinec = Jedinec(krizenie(self.generacia[i], self.elita[j]))
                jedinec.zmutuj(self.pocetMutacii)
                self.generacia[count] = jedinec
                count += 1
        zvysok = self.pocetJedincov - count
        # dalsich x bude vyskladanych z 75% - 90% najlepsich
        for i in range(zvysok):
            j1 = random.randint(int(3 * self.pocetJedincov / 4), int(math.ceil(9 * self.pocetJedincov / 10)))
            j2 = random.randint(int(3 * self.pocetJedincov / 4), int(math.ceil(9 * self.pocetJedincov / 10)))
            jedinec = Jedinec(krizenie(self.generacia[j1], self.generacia[j2]))
            jedinec.zmutuj(self.pocetMutacii)
            self.generacia[count] = jedinec
            count += 1

    def vytvorjedinceruleta(self):
        sumf = 0
        novagen = []
        count = 0
        for x in self.generacia:
            sumf += x.fitness

        if MODE == m.ELITERULETA:
            for i in range(self.pocetJedincov - self.pocetelita, self.pocetJedincov):
                novagen.append(copy.deepcopy(self.generacia[i]))
                count += 1

        for j in range(self.pocetJedincov - count):
            p1 = self.getrodicruleta(sumf)
            p2 = self.getrodicruleta(sumf)
            novyj = Jedinec(krizenie(p1, p2))
            novyj.zmutuj(self.pocetMutacii)
            novagen.append(novyj)

        self.generacia = novagen

    def getrodicruleta(self, sumf):
        sanca = random.random() * sumf

        partf = 0
        for i in range(self.pocetJedincov - 1, -1, -1):
            partf += self.generacia[i].fitness
            if partf > sanca:
                return self.generacia[i]
        return self.generacia[0]


#mapa je 2D pole False hodnot, kde True su len poklady
class Mapa:
    def __init__(self, maxy, maxx, sy, sx):
        self.pole = None
        self.MAXX = maxx
        self.MAXY = maxy
        self.pocetPokladov = 0
        self.surPokladov = []
        self.startPoz = Suradnica(sy, sx)

    def inicializuj(self):
        self.MAXX = 7
        self.MAXY = 7

        self.pole = np.full((self.MAXX, self.MAXY), False)

        #definujem suradnice pokladov
        self.surPokladov.append(Suradnica(5, 4))
        self.surPokladov.append(Suradnica(4, 1))
        self.surPokladov.append(Suradnica(3, 6))
        self.surPokladov.append(Suradnica(2, 2))
        self.surPokladov.append(Suradnica(1, 4))
        self.pocetPokladov = len(self.surPokladov)

    #po kazdom prejdeni obnovujem poklady
    def resetpoklady(self):
        for sur in self.surPokladov:
            self.pole[sur.y][sur.x] = True


def najdiriesenie():
    global priemery
    populacia.inicializuj()
    generaciecounter = 1
    optimalny = copy.deepcopy(populacia.generacia[populacia.pocetJedincov - 1])
    while generaciecounter < populacia.maxpocetgeneracii:
        if m.VYPIS:
            print("------ Generacia: " + str(generaciecounter) + ", " + str(len(populacia.generacia)))

        if MODE == m.MOJE:
            populacia.vytvorjedinceelita()
        elif MODE == m.RULETA or MODE == m.ELITERULETA:
            populacia.vytvorjedinceruleta()

        #generovanie rieseni
        for i in range(populacia.pocetJedincov):
            mapa.resetpoklady()

            m1 = Stroj(mapa.startPoz, populacia.generacia[i].chromozom)
            m1.generuj()

            populacia.generacia[i].cesta = m1.cesta
            populacia.generacia[i].pocetnajdenych = m1.pocetNajdenych
            populacia.generacia[i].calcfit()

        populacia.generacia.sort(key=Jedinec.getfit)

        #ukladam optimalneho jedinca ak je zvolene
        if m.OPTIMAL and populacia.generacia[populacia.pocetJedincov - 1].fitness > optimalny.fitness:
            optimalny = copy.deepcopy(populacia.generacia[populacia.pocetJedincov - 1])

        #ukladam elitu pre moje riesenie
        if MODE == m.MOJE:
            populacia.ulozelitu()

        #ak som nasiel riesenie a nehladam optimalne tak koncim
        if not m.OPTIMAL and populacia.generacia[populacia.pocetJedincov - 1].pocetnajdenych == mapa.pocetPokladov:
            print("Riesenie najdene v generacii " + str(generaciecounter))
            populacia.generacia[populacia.pocetJedincov - 1].vypis()
            # generujcestu(populacia.generacia[populacia.pocetJedincov - 1].cesta)
            return generaciecounter

        #vypisujem top 10 jedincov
        if m.VYPIS:
            populacia.vypistop()
            if MODE == m.MOJE:
                populacia.vypiselitu()

        generaciecounter += 1

    #ked skoncili vsetky generacie vypisujem najoptimalnejsie riesenie
    if m.OPTIMAL:
        print("Najoptimalnejsie riesenie:")
        optimalny.vypis()
        if optimalny.pocetnajdenych == 5:
            priemery.append(len(optimalny.cesta) / 2)
        else:
            priemery.append(0)
        # generujcestu(populacia.elita[0].cesta)
    return generaciecounter


def run():
    f = open("vystup.txt", "a")
    global priemery
    mapa.inicializuj()

    priemer = 0
    priemercount = 0
    xxx = 0
    totalt = 0

    while xxx < pocetOpakovani:
        bt = time.time()
        print("Beh " + str(xxx))
        najdene = najdiriesenie()
        et = time.time()

        if populacia.generacia[populacia.pocetJedincov - 1].pocetnajdenych != mapa.pocetPokladov:
            print("Riesenie nebolo najdene")
        else:
            priemercount += 1
            totalt += et - bt
            priemer += najdene
        xxx += 1

    print("Vysledok nebol najdeny " + str(xxx - priemercount) + " krat z " + str(xxx) + " pokusov")
    f.write("Vysledok nebol najdeny " + str(xxx - priemercount) + " krat z " + str(xxx) + " pokusov")

    if priemercount == 0:
        priemercount = 1
    print("Vysledok najdeny priemerne v generacii: " + str(priemer / priemercount))
    print("Priemerne trvanie: " + str(totalt / priemercount))

    f.close()


#vypisy, optimalne hladanie, cesta
m = Mody(False, False, False)
MODE = m.MOJE
#pocetGeneracii, pocetJedincov, max%Mutacii
populacia = Populacia(200, 100, 1.5)

#maxY, maxX, startY, startX
mapa = Mapa(7, 7, 6, 3)

pocetOpakovani = 1

priemery = []
run()
