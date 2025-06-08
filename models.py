from app import db

class Budynek(db.Model):
    __tablename__ = 'BUDYNKI'

    id_budynku = db.Column("ID_BUDYNKU",db.Integer, primary_key=True)
    nazwa_budynku = db.Column("NAZWA_BUDYNKU", db.String(30), nullable=False)
    adres = db.Column("ADRES", db.String(50), nullable=False)

    def __repr__(self):
        return f"<Budynek {self.nazwa_budynku}>"

class Sala(db.Model):
    __tablename__ = 'SALE'

    id_sali = db.Column("ID_SALI",db.Integer, primary_key=True)
    nazwa_sali = db.Column("NAZWA_SALI", db.String(30), nullable=False)
    rodzaj_sali = db.Column("RODZAJ_SALI", db.String(30), nullable=False)
    liczba_miejsc = db.Column("LICZBA_MIEJSC", db.Integer, nullable=False)
    wyposazenie = db.Column("WYPOSAŻENIE", db.String(200), nullable=False)
    id_budynku = db.Column(db.Integer, db.ForeignKey('BUDYNKI.ID_BUDYNKU'), nullable=False)

    budynek = db.relationship('Budynek', backref='sale')

    def __repr__(self):
        return f"<Sala {self.nazwa_sali}>"
    
class Role(db.Model):
    __tablename__ = 'ROLE'

    id_roli = db.Column("ID_ROLI", db.Integer, primary_key=True)
    nazwa_roli = db.Column("NAZWA_ROLI", db.String(50), nullable=False, unique=True)

    def __repr__(self):
        return f"<Rola {self.nazwa_roli}>"


class Przedmiot(db.Model):
    __tablename__ = 'PRZEDMIOTY'

    id_przedmiotu = db.Column("ID_PRZEDMIOTU", db.Integer, primary_key=True)
    nazwa_przedmiotu = db.Column("NAZWA_PRZEDMIOTU", db.String(50), nullable=False)
    id_uzytkownika = db.Column("ID_UZYTKOWNIKA", db.Integer, db.ForeignKey('UZYTKOWNICY.ID_UZYTKOWNIKA'), nullable=False)

    uzytkownik = db.relationship('Uzytkownik', backref='przedmioty')


    def __repr__(self):
        return f"<Przedmiot {self.nazwa_przedmiotu}>"

class Uzytkownik(db.Model):
    __tablename__ = 'UZYTKOWNICY'

    id_uzytkownika = db.Column("ID_UZYTKOWNIKA", db.Integer, primary_key=True)
    imie = db.Column("IMIE", db.String(50), nullable=False)
    nazwisko = db.Column("NAZWISKO", db.String(50), nullable=False)
    stopien_naukowy = db.Column("STOPIEN_NAUKOWY", db.String(50), nullable=True)

    def __repr__(self):
        return f"<Uzytkownik {self.imie} {self.nazwisko}>"
