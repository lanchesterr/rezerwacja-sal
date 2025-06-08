# routes.py w blueprintcie main
from flask import render_template, request, redirect, url_for
from . import main
from app import db
from app.models import Budynek, Sala, Role, Przedmiot, Uzytkownik

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
        nowa_rola = Role(nazwa_roli=nazwa_roli)
        db.session.add(nowa_rola)
        db.session.commit()
        return redirect(url_for('main.role'))

    wszystkie_role = Role.query.all()
    return render_template('role.html', role=wszystkie_role)

@main.route('/role/usun/<int:id>', methods=['POST'])
def usun_role(id):
    rola = Role.query.get_or_404(id)
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
        db.session.commit()
        return redirect(url_for('main.uzytkownicy'))

    wszyscy = Uzytkownik.query.all()
    return render_template('uzytkownicy.html', uzytkownicy=wszyscy)

@main.route('/uzytkownicy/usun/<int:id>', methods=['POST'])
def usun_uzytkownika(id):
    uzytkownik = Uzytkownik.query.get_or_404(id)
    db.session.delete(uzytkownik)
    db.session.commit()
    return redirect(url_for('main.uzytkownicy'))
