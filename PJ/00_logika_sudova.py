"""Istinitosna vrijednost, i jednostavna optimizacija, formula logike sudova.

Standardna definicija iz [Vuković, Matematička logika]:
* Propozicijska varijabla (P0, P1, P2, ..., P9, P10, P11, ....) je formula
* Ako je F formula, tada je i !F formula (negacija)
* Ako su F i G formule, tada su i (F&G), (F|G), (F->G) i (F<->G) formule
Sve zagrade (oko binarnih veznika) su obavezne!

Interpretaciju zadajemo imenovanim argumentima: vrijednost(F, P2=True, P7=False)
Optimizacija (formula.optim()) zamjenjuje potformule oblika !!F sa F.
"""


from pj import *


class T(TipoviTokena):
    NEG, KONJ, DISJ, OTV, ZATV = '!&|()'
    KOND, BIKOND = '->', '<->'
    class PVAR(Token):
        def vrijednost(self, I): return I[self]
        def optim(self): return self


def ls(lex):
    for znak in lex:
        if znak == 'P':
            prvo = lex.čitaj()
            if not prvo.isdigit(): lex.greška('očekivana znamenka')
            if prvo != '0': lex.zvijezda(str.isdigit)
            yield lex.token(T.PVAR)
        elif znak == '-':
            lex.pročitaj('>')
            yield lex.token(T.KOND)
        elif znak == '<':
            lex.pročitaj('-'), lex.pročitaj('>')
            yield lex.token(T.BIKOND)
        else: yield lex.literal(T)


### Beskontekstna gramatika:
# formula -> NEG formula | PVAR | OTV formula binvez formula ZATV
# binvez -> KONJ | DISJ | KOND | BIKOND


### Apstraktna sintaksna stabla (i njihovi atributi):
# formula: PVAR: Token
#          Negacija: ispod:formula
#          Binarna: veznik:T lijevo:formula desno:formula


class P(Parser):
    def formula(self):
        if self >> T.PVAR: return self.zadnji
        elif self >> T.NEG: 
            ispod = self.formula()
            return Negacija(ispod)
        elif self >> T.OTV:
            lijevo = self.formula()
            veznik = self.pročitaj(T.KONJ, T.DISJ, T.KOND, T.BIKOND)
            desno = self.formula()
            self.pročitaj(T.ZATV)
            return Binarna(veznik, lijevo, desno)
        else: raise self.greška()

    lexer = ls
    start = formula


class Negacija(AST('ispod')):
    def vrijednost(self, I): return not self.ispod.vrijednost(I)

    def optim(self):
        ispod_opt = self.ispod.optim()
        if ispod_opt ^ Negacija: return ispod_opt.ispod 
        else: return Negacija(ispod_opt)


class Binarna(AST('veznik lijevo desno')):
    def vrijednost(self, I):
        v = self.veznik
        l = self.lijevo.vrijednost(I)
        d = self.desno.vrijednost(I)
        if v ^ T.DISJ: return l or d
        elif v ^ T.KONJ: return l and d
        elif v ^ T.KOND: return l <= d
        elif v ^ T.BIKOND: return l == d
        else: assert False, 'nepokriveni slučaj'

    def optim(self):
        lijevo_opt = self.lijevo.optim()
        desno_opt = self.desno.optim()
        return Binarna(self.veznik, lijevo_opt, desno_opt)


def istinitost(formula, **interpretacija):
    I = Memorija(interpretacija)
    return formula.vrijednost(I)


ulaz = '!(P5&!!(P3->P0))'
print(ulaz)
P.tokeniziraj(ulaz)

F = P(ulaz)
prikaz(F)
F = F.optim()
prikaz(F)
print(istinitost(F, P0=False, P3=True, P5=False))  # True

for krivo in 'P00', 'P1\nP2', 'P34<>P56':
    with očekivano(LeksičkaGreška): print(P.tokeniziraj(krivo))


# DZ: implementirajte još neke optimizacije: npr. F|!G u G->F.
# DZ: Napravite totalnu optimizaciju negacije: svaka formula s najviše jednim !
#     *Za ovo bi vjerojatno bilo puno lakše imati po jedno AST za svaki veznik.