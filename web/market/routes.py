from flask_login import current_user, login_required, login_user, logout_user
from market import app, db
from flask import render_template, redirect, request, url_for, flash
from market.forms import PurchaseItemForm, RegisterForm, LoginForm, SellItemForm
from market.models import Item, User

@app.route('/')
@app.route('/home')
@app.route('/home/')
def home_page():
    return render_template('home.html')

@app.route('/market', methods=['GET', 'POST'])
@login_required
def market_page():
    purchase_form=PurchaseItemForm()
    selling_form=SellItemForm()
    if request.method=='POST':
        # Purchase item logic
        purchased_item=request.form.get('purchased_item')
        purchased_item_object=Item.query.filter_by(name=purchased_item).first()
        if purchased_item_object:
            if current_user.can_purchase(purchased_item_object):
                purchased_item_object.buy(current_user)
                flash(f'Congratulations! You purchased {purchased_item_object.name} for ₹{purchased_item_object.price}.', category='success')
            else:   
                flash(f"Unfortunately, you don't have enough money to purchase {purchased_item_object.name}!", category='danger')

        # Selling item logic
        sold_item=request.form.get('sold_item')
        sold_item_object=Item.query.filter_by(name=sold_item).first()     
        if sold_item_object:
            if current_user.can_sell(sold_item_object):
                sold_item_object.sell(current_user)
                flash(f'Congratulations! You sold {sold_item_object.name} back to market!', category='success')
            else:   
                flash(f"Something went wrong with selling {purchased_item_object.name}!", category='danger')

        return redirect(url_for('market_page'))

    if request.method=='GET':      
        items=Item.query.filter_by(owner=None)
        owned_items=Item.query.filter_by(owner=current_user.id)
        return render_template('market.html', items=items, purchase_form=purchase_form, owned_items=owned_items, selling_form=selling_form)

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        create_user=User(username=form.username.data,
                        email=form.email.data,
                        password=form.password.data)
        db.session.add(create_user)
        db.session.commit()
        login_user(create_user)
        flash(f'Account created successfully! You are now logged in as {create_user.username}!', category='success')

        return redirect(url_for('market_page'))

    if form.errors!={}:
        for errors in form.errors.values():
            flash(f"There was an error with creating a user: {errors}", category='danger')
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user=User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
            login_user(attempted_user)
            flash(f'You have been successfully logged in as {attempted_user.username}!', category='success')
            return redirect(url_for('market_page'))
        else:
            flash('Username and password do not match! Please try again.', category='danger')
        
    return render_template('login.html', form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash(f'You have been logged out!', category='info')
    return redirect(url_for('home_page'))
