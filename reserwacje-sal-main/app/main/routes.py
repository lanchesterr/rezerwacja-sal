from flask import render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import select
import time

from . import main
from app import db
from app.models import Budynek, Sala, Rola, Przedmiot, Uzytkownik, Rezerwacja, GrupaCykliczna, uzytkownicy_przedmioty
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

    # obsługa wyszukiwania
    szukana_nazwa = request.args.get('szukaj')
    if szukana_nazwa:
        wszystkie_budynki = Budynek.query.filter(Budynek.nazwa_budynku.ilike(f"%{szukana_nazwa}%")).all()
    else:
        wszystkie_budynki = Budynek.query.all()

    return render_template('budynki.html', budynki=wszystkie_budynki)

@main.route('/budynki/usun/<int:id>', methods=['POST'])
def usun_budynek(id):
    budynek = Budynek.query.get_or_404(id)
    try:
        db.session.delete(budynek)
        db.session.commit()
    except:
        db.session.rollback()
        return f"Błąd: W podanym budynku wystepują sale, usuń je jeśli chcesz usunąć budynek", 500
    return redirect(url_for('main.budynki'))

@main.route('/budynki/edytuj/<int:id>', methods=['POST'])
def edytuj_budynek(id):
    budynek = Budynek.query.get_or_404(id)
    budynek.nazwa_budynku = request.form['nazwa']
    budynek.adres = request.form['adres']
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

    # filtruj jeśli podano nazwę w GET
    szukana_nazwa = request.args.get('szukaj')
    if szukana_nazwa:
        wszystkie_sale = Sala.query.filter(Sala.nazwa_sali.ilike(f"%{szukana_nazwa}%")).all()
    else:
        wszystkie_sale = Sala.query.all()
    wszystkie_budynki = Budynek.query.all()
    return render_template('sale.html', sale=wszystkie_sale, budynki=wszystkie_budynki, err=err)

@main.route('/sale/usun/<int:id>', methods=['POST'])
def usun_sale(id):
    sala = Sala.query.get_or_404(id)
    try:
        Rezerwacja.query.filter_by(id_sali=id).delete()
        db.session.delete(sala)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return f"Sala niepoprawny: {e}", 500
    return redirect(url_for('main.sale'))

@main.route('/sale/edytuj/<int:id>', methods=['POST'])
def edytuj_sale(id):
    sala = Sala.query.get_or_404(id)
    sala.nazwa_sali = request.form['nazwa']
    sala.rodzaj_sali = request.form['rodzaj']
    sala.liczba_miejsc = request.form['liczba_miejsc']
    sala.wyposazenie = request.form['wyposażenie']
    budynek = Budynek.query.filter_by(nazwa_budynku=request.form['nazwa_budynku']).first()
    if not budynek:
        return redirect(url_for('main.sale', err='Budynek nie istnieje'))

    sala.id_budynku = budynek.id_budynku
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

    # wyszukiwanie po nazwie roli
    szukana_nazwa = request.args.get('szukaj')
    if szukana_nazwa:
        wszystkie_role = Rola.query.filter(Rola.nazwa_roli.ilike(f"%{szukana_nazwa}%")).all()
    else:
        wszystkie_role = Rola.query.all()

    return render_template('role.html', role=wszystkie_role)

@main.route('/role/edytuj/<int:id>', methods=['POST'])
def edytuj_role(id):
    rola = Rola.query.get_or_404(id)
    nowa_nazwa = request.form['nazwa_roli']
    if nowa_nazwa.strip():
        rola.nazwa_roli = nowa_nazwa.strip()
        db.session.commit()
    return redirect(url_for('main.role'))


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
        # id_uzytkownika = request.form.get('id_uzytkownika')

        # if not id_uzytkownika:
        #     err = "Musisz wybrać prowadzącego przedmiot."
        # else:
        try:
            nowy_przedmiot = Przedmiot(
                nazwa_przedmiotu=nazwa
            )
            db.session.add(nowy_przedmiot)
            db.session.commit()
            return redirect(url_for('main.przedmioty'))
        except Exception as e:
            db.session.rollback()
            err = f"Wystąpił błąd: {str(e)}"

    szukana_nazwa = request.args.get('szukaj')
    if szukana_nazwa:
        przedmioty = Przedmiot.query.filter(Przedmiot.nazwa_przedmiotu.ilike(f"%{szukana_nazwa}%")).all()
    else:
        przedmioty = Przedmiot.query.all()

    uzytkownicy = Uzytkownik.query.all()
    return render_template('przedmioty.html', przedmioty=przedmioty, uzytkownicy=uzytkownicy, err=err)


@main.route('/przedmioty/usun/<int:id>', methods=['POST'])
def usun_przedmiot(id):
    try:
        # Usuń wszystkie powiązania w tabeli pośredniczącej dla danego ID_PRZEDMIOTU
        stmt = uzytkownicy_przedmioty.delete().where(uzytkownicy_przedmioty.c.ID_PRZEDMIOTU == id)
        db.session.execute(stmt)

        # Usuń sam przedmiot
        przedmiot = Przedmiot.query.get_or_404(id)
        db.session.delete(przedmiot)
        db.session.commit()

        return redirect(url_for('main.przedmioty'))

    except Exception as e:
        db.session.rollback()
        return f"Błąd: {str(e)}", 500

@main.route('/przedmioty/edytuj/<int:id>', methods=['GET', 'POST'])
def edytuj_przedmiot(id):
    przedmiot = Przedmiot.query.get_or_404(id)
    uzytkownicy = Uzytkownik.query.all()

    if request.method == 'POST':
        nazwa = request.form.get('nazwa_przedmiotu')
        prowadzacy_ids = request.form.getlist('prowadzacy_ids')  # pobiera listę ID

        try:
            # Aktualizuj nazwę
            przedmiot.nazwa_przedmiotu = nazwa

            # Usuń stare powiązania
            db.session.execute(
                uzytkownicy_przedmioty.delete().where(uzytkownicy_przedmioty.c.ID_PRZEDMIOTU == id)
            )

            # Dodaj nowe
            for pid in prowadzacy_ids:
                db.session.execute(
                    uzytkownicy_przedmioty.insert().values(
                        ID_UZYTKOWNIKA=int(pid),
                        ID_PRZEDMIOTU=id
                    )
                )

            db.session.commit()
            return redirect(url_for('main.przedmioty'))

        except Exception as e:
            db.session.rollback()
            return f"Błąd przy edycji: {str(e)}", 500

    return render_template('przedmioty.html', przedmioty=Przedmiot.query.all(), uzytkownicy=uzytkownicy)

@main.route('/przedmioty/uzytkownik/<int:uzytkownik_id>')
def pobierz_przedmioty(uzytkownik_id):
    uzytkownik = Uzytkownik.query.get(uzytkownik_id)

    if not uzytkownik:
        return jsonify({"error": "Użytkownik nie znaleziony"}), 404

    przedmioty = [{
        'id' : p.id_przedmiotu,
        'nazwa' : p.nazwa_przedmiotu
    } for p in uzytkownik.przedmioty]
    print("Przedmioty:", przedmioty)
    return jsonify(przedmioty)

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
    # filtruj jeśli podano nazwę w GET
    szukana_nazwa = request.args.get('szukaj')
    if szukana_nazwa:
        wszyscy = Uzytkownik.query.filter(Uzytkownik.nazwisko.ilike(f"%{szukana_nazwa}%")).all()
    else:
        wszyscy = Uzytkownik.query.all()
    wszystkie_role = Rola.query.all()
    przedmioty = Przedmiot.query.all()
    print("Wszystkie role:", wszystkie_role)  # zobacz w konsoli
    return render_template('uzytkownicy.html', uzytkownicy=wszyscy, role=wszystkie_role, przedmioty=przedmioty)

@main.route('/uzytkownicy/edytuj/<int:id>', methods=['GET', 'POST'])
def edytuj_uzytkownika(id):
    uzytkownik = Uzytkownik.query.get_or_404(id)
    role = Rola.query.all()
    przedmioty = Przedmiot.query.all()

    if request.method == 'POST':
        imie = request.form.get('imie')
        nazwisko = request.form.get('nazwisko')
        stopien_naukowy = request.form.get('stopien_naukowy')

        role_ids = request.form.getlist('role_ids')
        przedmioty_ids = request.form.getlist('przedmioty_ids')  # Pobierz ID przedmiotów

        try:
            # Aktualizacja podstawowych danych
            uzytkownik.imie = imie
            uzytkownik.nazwisko = nazwisko
            uzytkownik.stopien_naukowy = stopien_naukowy

            # Usuń stare powiązania
            uzytkownik.role.clear()
            uzytkownik.przedmioty.clear()

            # Dodaj nowe powiązania - role
            for rid in role_ids:
                rola = Rola.query.get(rid)
                if rola:
                    uzytkownik.role.append(rola)

            # Dodaj nowe powiązania - przedmioty
            for pid in przedmioty_ids:
                przedmiot = Przedmiot.query.get(pid)
                if przedmiot:
                    uzytkownik.przedmioty.append(przedmiot)

            db.session.commit()
            return redirect(url_for('main.uzytkownicy'))

        except Exception as e:
            db.session.rollback()
            return f"Błąd: {str(e)}", 500

    return render_template('uzytkownicy.html', uzytkownicy=Uzytkownik.query.all(), role=role, przedmioty=przedmioty)

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

            # Obsługa kolizji rezerwacji
            kolizja_sali = Rezerwacja.query.filter(Rezerwacja.id_sali == nowa.id_sali,
                                              Rezerwacja.czas_od < nowa.czas_do,
                                              Rezerwacja.czas_do > nowa.czas_od).first()
            if kolizja_sali:
                flash("Wybrany termin koliduje z istniejącą rezerwacją!", "error")
                return redirect(url_for('main.rezerwacje'))  # przekierowanie z komunikatem

            # Obsługa próby rezerwacji "wstecz" np. od 11 do 10
            if nowa.czas_od > nowa.czas_do:
                flash("Nieprawidłowy zakres czasu rezerwacji!", "error")
                return redirect(url_for('main.rezerwacje'))

            # Obsługa próby dodania rezerwacji w czasie której użytkownik ma już zajęcia gdzieś indziej
            kolizja_uzytkownika = Rezerwacja.query.filter(Rezerwacja.id_uzytkownika == nowa.id_uzytkownika,
                                                          Rezerwacja.czas_od < nowa.czas_do,
                                                          Rezerwacja.czas_do > nowa.czas_od).first()
            if kolizja_uzytkownika:
                flash("Wybrany użytkownik prowadzi już zajęcia w tym terminie!", "error")
                return redirect(url_for('main.rezerwacje'))
                
            db.session.add(nowa)
            db.session.commit()
            return redirect(url_for('main.rezerwacje'))

        except Exception as e:
            db.session.rollback()
            return f"Błąd: {e}", 400
    # filtruj jeśli podano nazwę w GET
    szukana_nazwa = request.args.get('szukaj')
    if szukana_nazwa:
        rezerwacje = Rezerwacja.query.filter(Sala.nazwa_sali.ilike(f"%{szukana_nazwa}%")).all()
    else:
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

@main.route('/rezerwacje/edytuj/<int:id>', methods=['GET', 'POST'])
def edytuj_rezerwacje(id):
    rezerwacja = Rezerwacja.query.get_or_404(id)
    sale = Sala.query.all()
    przedmioty = Przedmiot.query.all()
    uzytkownicy = Uzytkownik.query.all()

    if request.method == 'POST':
        try:
            # Zaktualizuj dane z formularza
            rezerwacja.status = request.form['status']
            rezerwacja.id_sali = int(request.form['id_sali'])
            rezerwacja.id_przedmiotu = int(request.form['id_przedmiotu'])
            rezerwacja.id_uzytkownika = int(request.form['id_uzytkownika'])
            rezerwacja.czas_od = datetime.strptime(request.form['czas_od'], '%Y-%m-%dT%H:%M')
            rezerwacja.czas_do = datetime.strptime(request.form['czas_do'], '%Y-%m-%dT%H:%M')

            db.session.commit()
            return redirect(url_for('main.rezerwacje'))

        except Exception as e:
            db.session.rollback()
            return f"Błąd: {str(e)}", 500

    return render_template(
        'rezerwacje.html',
        rezerwacje=Rezerwacja.query.all(),
        sale=sale,
        przedmioty=przedmioty,
        uzytkownicy=uzytkownicy
    )
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
    return render_template('grupy_cykliczne.html', grupy=grupy,
                           sale=sale, przedmioty=przedmioty, uzytkownicy=uzytkownicy)

@main.route('/grupy_cykliczne/usun/<int:id>', methods=['POST'])
def usun_grupe_cykliczna(id):
    grupa = GrupaCykliczna.query.get_or_404(id)
    Rezerwacja.query.filter_by(id_grupy_cyklicznej=grupa.id_grupy_cyklicznej).delete()
    db.session.delete(grupa)
    db.session.commit()
    return redirect(url_for('main.grupy_cykliczne'))

