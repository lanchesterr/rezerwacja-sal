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

# Tabela pośrednicząca dla relacji wiele-do-wielu ROLE_UZYTKOWNICY
role_uzytkownicy = db.Table(
    'ROLE_UZYTKOWNICY',
    db.Column('ID_UZYTKOWNIKA', db.Integer, db.ForeignKey('UZYTKOWNICY.ID_UZYTKOWNIKA'), primary_key=True),
    db.Column('ID_ROLI', db.Integer, db.ForeignKey('ROLE.ID_ROLI'), primary_key=True),
    db.Model.metadata
)

class Rola(db.Model):
    __tablename__ = 'ROLE'

    id_roli = db.Column("ID_ROLI", db.Integer, primary_key=True)
    nazwa_roli = db.Column("NAZWA_ROLI", db.String(50), nullable=False, unique=True)

    def __repr__(self):
        return f"<Rola {self.nazwa_roli}>"


# Tabela pośrednicząca dla relacji wiele-do-wielu - UZYTKOWNICY_PRZEDMIOTY
uzytkownicy_przedmioty = db.Table(
    'UZYTKOWNICY_PRZEDMIOTY',
    db.Column('ID_UZYTKOWNIKA', db.Integer, db.ForeignKey('UZYTKOWNICY.ID_UZYTKOWNIKA'), primary_key=True),
    db.Column('ID_PRZEDMIOTU', db.Integer, db.ForeignKey('PRZEDMIOTY.ID_PRZEDMIOTU'), primary_key=True),
    db.Model.metadata
)

class Przedmiot(db.Model):
    __tablename__ = 'PRZEDMIOTY'

    id_przedmiotu = db.Column("ID_PRZEDMIOTU", db.Integer, primary_key=True)
    nazwa_przedmiotu = db.Column("NAZWA_PRZEDMIOTU", db.String(50), nullable=False)


    # Relacja wiele-do-wielu z Uzytkownikiem
    # prowadzacy = db.relationship("Uzytkownik", secondary=uzytkownicy_przedmioty, backpopulates="przedmioty")
    def __repr__(self):
        return f"<Przedmiot {self.nazwa_przedmiotu}>"



class Uzytkownik(db.Model):
    __tablename__ = 'UZYTKOWNICY'

    id_uzytkownika = db.Column("ID_UZYTKOWNIKA", db.Integer, primary_key=True)
    imie = db.Column("IMIE", db.String(50), nullable=False)
    nazwisko = db.Column("NAZWISKO", db.String(50), nullable=False)
    stopien_naukowy = db.Column("STOPIEN_NAUKOWY", db.String(50), nullable=True)

    # Relacja wiele-do-wielu z Rola
    role = db.relationship("Rola", secondary="ROLE_UZYTKOWNICY", backref='uzytkownicy')
    # Relacja wiele-do-wielu z Przedmiot
    # przedmioty = db.relationship("Przedmiot", secondary=uzytkownicy_przedmioty, backpopulates="prowadzacy")
    def __repr__(self):
        return f"<Uzytkownik {self.imie} {self.nazwisko}>"

# Teraz możesz dodać relację poza klasami:
Uzytkownik.przedmioty = db.relationship(
    "Przedmiot",
    secondary=uzytkownicy_przedmioty,
    back_populates="prowadzacy"
)
Przedmiot.prowadzacy = db.relationship(
    "Uzytkownik",
    secondary=uzytkownicy_przedmioty,
    back_populates="przedmioty"
)

class Rezerwacja(db.Model):
    __tablename__ = 'REZERWACJE'

    id_rezerwacji = db.Column("ID_REZERWACJI", db.Integer, primary_key=True)
    id_sali = db.Column("ID_SALI", db.Integer, db.ForeignKey('SALE.ID_SALI'), nullable=False)
    id_uzytkownika = db.Column("ID_UZYTKOWNIKA", db.Integer, db.ForeignKey('UZYTKOWNICY.ID_UZYTKOWNIKA'), nullable=False)
    id_przedmiotu = db.Column("ID_PRZEDMIOTU", db.Integer, db.ForeignKey('PRZEDMIOTY.ID_PRZEDMIOTU'), nullable=False)
    status = db.Column("STATUS", db.String(50), nullable=False)
    czas_od = db.Column("CZAS_OD", db.DateTime, nullable=False)
    czas_do = db.Column("CZAS_DO", db.DateTime, nullable=False)
    id_grupy_cyklicznej = db.Column("ID_GRUPY_CYKLICZNEJ", db.Integer, db.ForeignKey('GRUPYCYKLICZNE.ID_GRUPY_CYKLICZNEJ'))

    sala = db.relationship('Sala')
    przedmiot = db.relationship('Przedmiot')
    uzytkownik = db.relationship('Uzytkownik')

    def __repr__(self):
        return f"<Rezerwacja {self.id_rezerwacji} - {self.status}>"


class GrupaCykliczna(db.Model):
    __tablename__ = 'GRUPYCYKLICZNE'

    id_grupy_cyklicznej = db.Column('ID_GRUPY_CYKLICZNEJ',db.Integer, primary_key=True)
    data_start = db.Column(db.Date, nullable=False)
    data_koniec = db.Column(db.Date, nullable=False)
    dzien_tygodnia = db.Column(db.Integer, nullable=False) 
    godzina_od = db.Column('GODZINA_OD', db.String(5), nullable=False)
    godzina_do = db.Column('GODZINA_DO', db.String(5), nullable=False)
    opis = db.Column(db.String(255))

    rezerwacje = db.relationship('Rezerwacja', backref='GRUPYCYKLICZNE', cascade="all, delete")

