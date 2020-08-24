
"""
Napomena: Svjesni smo da zadatak nije ni izbliza gotov, ali smo htjeli predati barem ovo zato da znate da smo barem razmislili o zadatku.

Jezik je, naravno, sličan C-u.
Ima dva tipa varijabli koje se razlikuju po nazivu:
 -ime stringovne varijable počinje sa underscore-om kojega slijedi slovo
 -ime brojevne varijable počinje sa slovom
 -ostatak imena oba tipa se može sastojati samo od brojeva ili slova
Funkcije koje koristimo:
....oddo - slično c-ovaskoj for funkciji koja bi izgledala ovako: oddo(varijabla, pocetnavr, krajnjavr), uočite da su sve ovo varijable brojevnog tipa jer im nazivi ne počinju sa _
....uvjet - slično if funkciji, s tim da bi unutar zagrade smjele stajati samo usporedbe stringovnih ili brojevnih zraza
	  - nakon uvjeta su obavezne vitičaste zagrade u kojima su naredbe
	  - uvjet je ispunjen ako su izrazi istog tipa i ako je (ne)jednakost unutra istinita
....alternativa - slično else, samo što bi bile obavezne vitičaste zagrade
....duljina - funkcija koja vraća duljinu stringa

Za konkatenaciju stringova smo odabrali simbol '&', a ostali operatori su prilično jasni.
"""




from pj import *

class AN(enum.Enum):
    ODDO, ISPIŠI, UPIŠI, UVJET, ALTERNATIVA, BROJUSLOVA, DULJINA, ISTI, NL = 'oddo', 'upiši', 'ispiši', 'uvjet', 'alt', 'slovima', 'duljina', 'isti', 'nl'
    PLUS, MINUS, PUTA, PODIJELJENO, KONK = '+-*/&'
    OTVORENA, ZATVORENA, VOTVORENA, VZATVORENA, TOCKAZAREZ, APOSTROF = '(',')','{','}',';',"'"
    VECE, MANJE, JEDNAKO = '><='
    VECEJEDNAKO, MANJEJEDNAKO, RAZLICITO, PRIDRUZI = '>=', '<=', '!=', '->'
    class BROJ(Token):
        def vrijednost(self): return int(self.sadržaj)
        def prevedi(self): yield 'PUSH', self.vrijednost()
    class STRING(Token):
        """string čine svi znakovi između ' ', zabranjen znak za string je ' """
        pass
    class SIME(Token):
        """ime za broj, počinje underscoreom, a ostatak se sastoji samo od slova i brojeva (broj ne smije biti direktno iza _."""
        def vrijednost(self, mem): return pogledaj(mem, self)
    class BIME(Token):
        """ime za string, sastoji se samo od slova i brojeva, počinje slovom"""
        def vrijednost(self, mem): return pogledaj(mem, self)

def an_lex(source):
    lex = Tokenizer(source)
    for znak in iter(lex.čitaj, ''):
        if znak.isspace(): lex.zanemari()
        elif znak == '!':
            sljedeći = lex.čitaj()
            if sljedeći == '=': yield lex.token(AN.RAZLICITO)
            else :raise lex.greška('u ovom jeziku ne bi trebalo biti samostalnih !')
        elif znak == '<':
            if lex.slijedi('='): yield lex.token(AN.MANJEJEDNAKO)
            else :lex.token(AN.MANJE)
        elif znak == '>':
            if lex.slijedi('='): yield lex.token(AN.VECEJEDNAKO)
            else :lex.token(AN.VECE)
        elif znak == '-':
            if lex.slijedi('>'): yield lex.token(AN.PRIDRUZI)
            else :lex.token(AN.MINUS)
        elif znak == "'":
            lex.pročitaj_do("'")
            yield lex.token(AN.STRING)
        elif znak == '_':
            sljedeći = lex.čitaj()
            if sljedeći.isalpha: 
                lex.zvijezda(str.isalnum)
                yield lex.literal(AN.SIME) 
            else: raise lex.greška('u ovom jeziku se underscore (_) može koristiti samo na početku imena stringovne varijable, mora ga slijediti slovo')
        elif znak.isalpha():
            lex.zvijezda(str.isalnum)
            yield lex.literal(AN.BIME)    
        elif znak.isdigit():
            lex.zvijezda(str.isdigit)
            p = lex.sadržaj
            if p == '0' or p[0] != '0': yield lex.token(AN.BROJ)
            else :raise lex.greška('broj nije u bazi 10')
        else: yield lex.literal(AN)




#testiranje leksera
print('br->6; _i5->134; a->(br+i)/5; a==i5; br!=4; ')
for tok in an_lex("br->6; i5->134; a->(br+i)/5; a==i5; br!=4; _str->'nfsl'; duljina(_str) "):
	print(tok)




### Beskontekstna gramatika:
# naredba -> pridruži | ispiši | upiši | petlja | uvjet
# pridruži -> BIME PRIDRUZI brojevniizraz | SIME PRIDRUZI stringovniizraz
# ispiši -> 
# upiši ->
# usporednik -> brojčlan | brojevniizraz | stringčlan | stringovniizraz
# stringovniizraz -> stringovniizraz KONK stringčlan | stringčlan 
# stringčlan -> STRING | SIME | OTV stringovniizraz ZATV | BROJUSLOVA OTVORENA brojevniizraz ZATVORENA
# brojevniizraz -> brojevniizraz PLUS brojčlan | brojevniizraz MINUS brojčlan | brojčlan
# brojčlan -> brojčlan PUTA faktor | brojčlan PODIJELJENO faktor | MINUS faktor | faktor
# faktor -> BROJ | BIME | OTV brojevniizraz ZATV | DULJINA OTV stringovniizraz ZATV
# petlja -> ODDO OTVORENA usporedba ZATVORENA VOTVORENA naredbe VZATVORENA
# usporedba -> brojčlan ( VECE | MANJE | JEDNAKO | VECEJEDNAKO | MANJEJEDNAKO | RAZLICITO ) brojčlan
#            | stringovniizraz ISTI stringovniizraz
# naredbe -> naredba ( TOČKAZAREZ naredbe )?
# uvjet -> UVJET OTVORENA usporedba ZATVORENA VOTVORENA naredbe VZATVORENA ( ALTERNATIVA VOTVORENA naredbe VZATVORENA )?



#nedovrseni parser
class ANParser(Parser):
    def brojevniizraz(self):
        članovi = [self.brojčlan()]
        while self >> {AN.PLUS, AN.MINUS}:
            operator = self.zadnji
            dalje = self.član()
            članovi.append(dalje if operator ^ PSK.PLUS else Suprotan(dalje))
        return članovi[0] if len(članovi) == 1 else Zbroj(članovi)

        
    def usporedbe(self):
        if self >> AN.VECE:
            drugi = self.izraz()
            return UsporedbaVece([prvi, drugi])
        elif self >> AN.VECEJEDNAKO:
            drugi = self.izraz()
            return UsporedbaVeceJednako([prvi, drugi])
        elif self >> AN.MANJE:
            drugi = self.izraz()
            return UsporedbaManjeJednako([prvi, drugi])
        elif self >> AN.MANJEJEDNAKO:
            drugi = self.izraz()
            return UsporedbaManjeJednako([prvi, drugi])
        elif self >> AN.JEDNAKO:
            drugi = self.izraz()
            return UsporedbaJednako([prvi, drugi])
        else:
            return prvi

    def brojčlan(self):
        if self >> AC.MINUS: return Unarna(self.zadnji, self.faktor())
        trenutni = self.faktor()
        while True:
            if self >> {AC.PUTA, AC.KROZ}:
                trenutni = Umnozak(self.zadnji, trenutni, self.faktor())
            else: return trenutni
            
    def faktor(self):
        if self >> {AN.BROJ, AN.BIME}: trenutni = self.zadnji
        elif self >> AN.OTV:
            trenutni = self.izraz()
            self.pročitaj(AN.ZATV)
        else: raise self.greška()
        while self >> AC.KONJ: trenutni = Unarna(self.zadnji, trenutni)
        return trenutni

    start = brojevniizraz
