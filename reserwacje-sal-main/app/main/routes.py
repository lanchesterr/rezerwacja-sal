from flask import render_template, request, redirect, url_for
from sqlalchemy import select

from . import main
from app import db
from app.models import Budynek, Sala, Rola, Przedmiot, Uzytkownik, Rezerwacja, GrupaCykliczna
from datetime import datetime, timedelta

@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('home.html')

@main.route('/budynki', methods=['GET', 'POST'])
def budynki():
    if request.method == 'POST':
        nazwa = request.form['nazwa']
        adres = request.form['adres']
        nowy_budynek = Budynek(nazwa_budynku=nazwa, adres=adres)
        db.session.add(nowy_budynek)
        db.session.commit()
        return redirect(url_for('main.budynki'))

    wszystkie_budynki = Budynek.query.all()
    return render_template('budynki.html', budynki=wszystkie_budynki)

@main.route('/budynki/usun/<int:id>', methods=['POST'])
def usun_budynek(id):
    budynek = Budynek.query.get_or_404(id)
    db.session.delete(budynek)
    db.session.commit()
    return redirect(url_for('main.budynki'))

@main.route('/sale', methods=['GET', 'POST'])
def sale():
    err = None
    if request.method == 'POST':
        nazwa = request.form['nazwa']
        rodzaj = request.form['rodzaj']
        liczba_miejsc = request.form['liczba_miejsc']
        wyposazenie = request.form['wyposażenie']
        nazwa_budynku = request.form['nazwa_budynku']

        budynek = Budynek.query.filter_by(nazwa_budynku=nazwa_budynku).first()
        if not budynek:
            err = "Budynek o takiej nazwie nie istnieje"
            wszystkie_sale = Sala.query.all()
            return render_template('sale.html', sale=wszystkie_sale, err=err)

        nowa_sala = Sala(
            nazwa_sali=nazwa,
            rodzaj_sali=rodzaj,
            liczba_miejsc=liczba_miejsc,
            wyposazenie=wyposazenie,
            id_budynku=budynek.id_budynku
        )
        db.session.add(nowa_sala)
        db.session.commit()
        return redirect(url_for('main.sale'))

    wszystkie_sale = Sala.query.all()
    return render_template('sale.html', sale=wszystkie_sale, err=err)

@main.route('/sale/usun/<int:id>', methods=['POST'])
def usun_sale(id):
    sala = Sala.query.get_or_404(id)
    db.session.delete(sala)
    db.session.commit()
    return redirect(url_for('main.sale'))

@main.route('/role', methods=['GET', 'POST'])
def role():
    if request.method == 'POST':
        nazwa_roli = request.form['nazwa_roli']
        nowa_rola = Rola(nazwa_roli=nazwa_roli)
        db.session.add(nowa_rola)
        db.session.commit()
        return redirect(url_for('main.role'))

    wszystkie_role = Rola.query.all()
    return render_template('role.html', role=wszystkie_role)

@main.route('/role/usun/<int:id>', methods=['POST'])
def usun_role(id):
    rola = Rola.query.get_or_404(id)
    db.session.delete(rola)
    db.session.commit()
    return redirect(url_for('main.role'))

@main.route('/przedmioty', methods=['GET', 'POST'])
def przedmioty():
    err = None

    if request.method == 'POST':
        nazwa = request.form.get('nazwa_przedmiotu')
        id_uzytkownika = request.form.get('id_uzytkownika')

        if not id_uzytkownika:
            err = "Musisz wybrać prowadzącego przedmiot."
        else:
            try:
                nowy_przedmiot = Przedmiot(
                    nazwa_przedmiotu=nazwa,
                    id_uzytkownika=int(id_uzytkownika)
                )
                db.session.add(nowy_przedmiot)
                db.session.commit()
                return redirect(url_for('main.przedmioty'))
            except Exception as e:
                db.session.rollback()
                err = f"Wystąpił błąd: {str(e)}"

    przedmioty = Przedmiot.query.all()
    uzytkownicy = Uzytkownik.query.all()
    return render_template('przedmioty.html', przedmioty=przedmioty, uzytkownicy=uzytkownicy, err=err)

@main.route('/przedmioty/usun/<int:id>', methods=['POST'])
def usun_przedmiot(id):
    przedmiot = Przedmiot.query.get_or_404(id)
    db.session.delete(przedmiot)
    db.session.commit()
    return redirect(url_for('main.przedmioty'))

@main.route('/uzytkownicy', methods=['GET', 'POST'])
def uzytkownicy():
    if request.method == 'POST':
        imie = request.form['imie']
        nazwisko = request.form['nazwisko']
        stopien_naukowy = request.form.get('stopien_naukowy')

        nowy_uzytkownik = Uzytkownik(imie=imie, nazwisko=nazwisko, stopien_naukowy=stopien_naukowy)

        db.session.add(nowy_uzytkownik)
        db.session.flush()

        # Obsługa ról
        rola_ids = request.form.getlist('id_roli')
        for rola_id in rola_ids:
            rola = Rola.query.get(rola_id)
            if rola:
                nowy_uzytkownik.role.append(rola)

        db.session.commit()
        return redirect(url_for('main.uzytkownicy'))

    wszyscy = Uzytkownik.query.all()
    wszystkie_role = Rola.query.all()
    print("Wszystkie role:", wszystkie_role)  # zobacz w konsoli
    return render_template('uzytkownicy.html', uzytkownicy=wszyscy, role=wszystkie_role)

@main.route('/uzytkownicy/usun/<int:id>', methods=['POST'])
def usun_uzytkownika(id):
    uzytkownik = Uzytkownik.query.get_or_404(id)
    db.session.delete(uzytkownik)
    db.session.commit()
    return redirect(url_for('main.uzytkownicy'))

@main.route('/rezerwacje', methods=['GET', 'POST'])
def rezerwacje():
    if request.method == 'POST':
        try:
            nowa = Rezerwacja(
                id_sali=int(request.form['id_sali']),
                id_przedmiotu=int(request.form['id_przedmiotu']),
                id_uzytkownika=int(request.form['id_uzytkownika']),
                status=request.form['status'],
                czas_od=datetime.fromisoformat(request.form['czas_od']),
                czas_do=datetime.fromisoformat(request.form['czas_do'])
            )
            #TODO: Zablokowanie możliwości rezerwacji w tym samym terminie
            #      oraz w bezsensownych terminach, np. wstecz
            kolizja = Rezerwacja.query.filter(Rezerwacja.id_sali == nowa.id_sali,
                                              Rezerwacja.czas_od < nowa.czas_do,
                                              Rezerwacja.czas_do > nowa.czas_od).first()
            if kolizja:
                return redirect(url_for('main.rezerwacje'))
            db.session.add(nowa)
            db.session.commit()
            return redirect(url_for('main.rezerwacje'))
        except Exception as e:
            db.session.rollback()
            return f"Błąd: {e}", 400

    rezerwacje = Rezerwacja.query.all()
    sale = Sala.query.all()
    przedmioty = Przedmiot.query.all()
    uzytkownicy = Uzytkownik.query.all()
    return render_template('rezerwacje.html', rezerwacje=rezerwacje, sale=sale, przedmioty=przedmioty, uzytkownicy=uzytkownicy)

@main.route('/rezerwacje/usun/<int:id>', methods=['POST'])
def usun_rezerwacje(id):
    r = Rezerwacja.query.get_or_404(id)
    db.session.delete(r)
    db.session.commit()
    return redirect(url_for('main.rezerwacje'))

@main.route('/grupy_cykliczne', methods=['GET', 'POST'])
def grupy_cykliczne():
    if request.method == 'POST':
        try:
            data_start = datetime.strptime(request.form['data_start'], '%Y-%m-%d').date()
            data_koniec = datetime.strptime(request.form['data_koniec'], '%Y-%m-%d').date()
            dzien_tygodnia = int(request.form['dzien_tygodnia'])
            godzina_od = request.form['godzina_od']
            godzina_do = request.form['godzina_do']
            opis = request.form['opis']

            grupa = GrupaCykliczna(
                data_start=data_start,
                data_koniec=data_koniec,
                dzien_tygodnia=dzien_tygodnia,
                godzina_od=godzina_od,
                godzina_do=godzina_do,
                opis=opis
            )
            db.session.add(grupa)
            db.session.flush()

            id_sali = int(request.form['id_sali'])
            id_przedmiotu = int(request.form['id_przedmiotu'])
            id_uzytkownika = int(request.form['id_uzytkownika'])
            status = request.form['status']

            czas_od_time = datetime.strptime(godzina_od, '%H:%M').time()
            czas_do_time = datetime.strptime(godzina_do, '%H:%M').time()

            aktualna_data = data_start
            while aktualna_data <= data_koniec:
                if aktualna_data.weekday() == dzien_tygodnia:
                    czas_od = datetime.combine(aktualna_data, czas_od_time)
                    czas_do = datetime.combine(aktualna_data, czas_do_time)
                    db.session.add(Rezerwacja(
                        id_sali=id_sali,
                        id_przedmiotu=id_przedmiotu,
                        id_uzytkownika=id_uzytkownika,
                        status=status,
                        czas_od=czas_od,
                        czas_do=czas_do,
                        id_grupy_cyklicznej=grupa.id_grupy_cyklicznej
                    ))
                aktualna_data += timedelta(days=1)

            db.session.commit()
            return redirect(url_for('main.grupy_cykliczne'))

        except Exception as e:
            db.session.rollback()
            return f"Błąd: {e}", 400

    grupy = GrupaCykliczna.query.all()
    sale = Sala.query.all()
    przedmioty = Przedmiot.query.all()
    uzytkownicy = Uzytkownik.query.all()
    return render_template('grupy_cykliczne.html', grupy=grupy, sale=sale, przedmioty=przedmioty, uzytkownicy=uzytkownicy)

@main.route('/grupy_cykliczne/usun/<int:id>', methods=['POST'])
def usun_grupe_cykliczna(id):
    grupa = GrupaCykliczna.query.get_or_404(id)
    Rezerwacja.query.filter_by(id_grupy_cyklicznej=grupa.id_grupy_cyklicznej).delete()
    db.session.delete(grupa)
    db.session.commit()
    return redirect(url_for('main.grupy_cykliczne'))
