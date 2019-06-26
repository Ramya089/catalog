from flask import (
                    Flask,
                    flash,
                    render_template,
                    request,
                    url_for,
                    flash,
                    jsonify,
                    redirect)
from flask import session as login_session
from flask import make_response
import sys
from sqlalchemy import (Column, ForeignKey, Integer,
                        String)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy import create_engine
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import os
import random
import string
import httplib2
import json
import requests
app = Flask(__name__)
Base = declarative_base()


class Admins(Base):
    __tablename__ = "admin"
    admin_userid = Column(Integer, primary_key=True)
    admin_email = Column(String(100), nullable=False)


class Fooditems(Base):
    __tablename__ = "fooditems"
    fooditems_id = Column(Integer, primary_key=True)
    fooditems_name = Column(String(100), nullable=False)
    fooditems_admin = Column(Integer, ForeignKey('admin.admin_userid'))
    fooditems_relation = relationship(Admins)

    @property
    def serialize(self):
        return {
            'id': self.fooditems_id,
            'name': self.fooditems_name
            }


class Items(Base):
    __tablename__ = "items"
    item_id = Column(Integer, primary_key=True)
    item_name = Column(String(100), nullable=False)
    item_price = Column(Integer, nullable=False)
    item_image = Column(String(1000), nullable=False)
    fooditems_id = Column(Integer, ForeignKey('fooditems.fooditems_id'))
    item_relation = relationship(Fooditems)

    @property
    def serialize(self):
        return {
            'name': self.item_name,
            'price': self.item_price,
            'img_url': self.item_image
            }
engine = create_engine('sqlite:///fooditemss.db')
Base.metadata.create_all(engine)
session = scoped_session(sessionmaker(bind=engine))
CLIENT_ID = json.loads(open("client_secrets.json", 'r').read())
CLIENT_ID = CLIENT_ID['web']['client_id']


@app.route('/read')
def read():
    fooditems = session.query(Items).all()
    msg = ""
    for each in fooditems:
        msg += str(each.item_name)
    return msg


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')


# displays all fooditem categories
@app.route('/category', methods=['GET'])
def showcategory():
    if request.method == 'GET':
        category_list = session.query(Fooditems).all()
        return render_template('showcategory.html', categories=category_list)


# adds the fooditem category
@app.route('/category/new', methods=['GET', 'POST'])
def newcategory():
    if 'email' not in login_session:
        flash("Please Login")
        return redirect(url_for('login'))
    if request.method == 'GET':
        return render_template('newcategory.html')
    else:
        category_name = request.form['category_name']
        if category_name:
            admin = session.query(Admins).filter_by(
                admin_email=login_session['email']
                ).one_or_none()
            if admin is None:
                return redirect(url_for('home'))
            admin_userid = admin.admin_userid
            new_item = Fooditems(
                                fooditems_name=category_name,
                                fooditems_admin=admin_userid)
            session.add(new_item)
            session.commit()
            flash("your Fooditem is added")
            return redirect(url_for('home'))
        else:
            return 'enter some category'


# edits the fooditem category
@app.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
def editcategory(category_id):
    if 'email' not in login_session:
        flash("Please Login")
        return redirect(url_for('login'))
    admin = session.query(Admins).filter_by(
                admin_email=login_session['email']
                ).one_or_none()
    if admin is None:
        flash("Invalid User")
        return redirect(url_for('home'))
    fooditems = session.query(Fooditems).filter_by(
                                                   fooditems_id=category_id
                                                   ).one_or_none()
    if fooditems is None:
        flash("Category not found")
        return redirect(url_for('home'))
    login_admin_userid = admin.admin_userid
    admin_userid = fooditems.fooditems_admin
    if login_admin_userid != admin_userid:
        flash('you are not allowed to edit')
        return redirect(url_for('home'))
    if request.method == 'POST':
        category_name = request.form['category_name']
        fooditems.fooditems_name = category_name
        session.add(fooditems)
        session.commit()
        flash('updated successfully')
        return redirect(url_for('home'))
    else:
        fooditems = session.query(
                                    Fooditems).filter_by(
                                        fooditems_id=category_id
                                        ).one_or_none()
        return render_template('categoryedit.html',
                               fooditems_name=fooditems.fooditems_name,
                               id_category=category_id)


# deletes the fooditem category
@app.route('/category/<int:category_id>/delete')
def deletecategory(category_id):
    if 'email' not in login_session:
        flash("Please Login")
        return redirect(url_for('login'))
    admin = session.query(Admins).filter_by(
                admin_email=login_session['email']
                ).one_or_none()
    if admin is None:
        flash("Invalid User")
        return redirect(url_for('home'))
    fooditems = session.query(Fooditems).filter_by(
                                            fooditems_id=category_id
                                            ).one_or_none()
    if fooditems is None:
        flash("Category not found")
        return redirect(url_for('home'))
    login_admin_userid = admin.admin_userid
    admin_userid = fooditems.fooditems_admin
    if login_admin_userid != admin_userid:
        flash('you are not allowed to edit')
        return redirect(url_for('home'))
    fooditems = session.query(Fooditems).filter_by(
                                    fooditems_id=category_id
                                    ).one_or_none()
    if fooditems:
        name = fooditems.fooditems_name
        session.delete(fooditems)
        session.commit()
        flash('deleted successfully '+str(name))
        return redirect(url_for('home'))
    else:
        flash('category not found')
        return redirect(url_for('home'))


@app.route('/category/<int:category_id>/items')
def showitems(category_id):
    if request.method == 'GET':
        scategory_list = session.query(Items).filter_by(
                                        fooditems_id=category_id)
    return render_template('showitems.html', categories=scategory_list)


@app.route('/latestitems')
def Latestitems():
    if request.method == 'GET':
        category_list = session.query(Items).all()
    return render_template('latest.html', categories=category_list)


@app.route('/all_json')
def json_all():
    objects = session.query(Items).all()
    return jsonify(Objects=[each.serialize for each in objects])


@app.route('/category/<int:category_id>/items.json')
def single_categoryitems_json(category_id):
    objects = session.query(Items).filter_by(fooditems_id=category_id).all()
    return jsonify(Objects=[each.serialize for each in objects])


@app.route('/category/<int:category_id>/items/<int:itemid>',
           methods=['GET', 'POST'])
def itemdetails(category_id, itemid):
    if request.method == 'GET':
        item = session.query(Items).filter_by(fooditems_id=category_id,
                                              item_id=itemid).one_or_none()
        return render_template(
            'itemdetails.html', iname=item.item_name,
            iprice=item.item_price,
            iimage=item.item_image)


@app.route('/food/category/json')
def categoryjson():
    foods = session.query(Fooditems.one_or_none())
    return jsonify(Categories=[c.serialize for c in foods])


@app.route('/category/<int:categoryid>/items/new', methods=['GET', 'POST'])
def newitem(categoryid):
    if 'email' not in login_session:
        flash("Please Login")
        return redirect(url_for('login'))
    admin = session.query(Admins).filter_by(
                                            admin_email=login_session['email']
                                            ).one_or_none()
    if admin is None:
        flash("Invalid User")
        return redirect(url_for('home'))
    fooditems = session.query(Fooditems).filter_by(
                                        fooditems_id=categoryid
                                        ).one_or_none()
    if not fooditems:
        flash("Category not found")
        return redirect(url_for('home'))
    login_admin_userid = admin.admin_userid
    admin_userid = fooditems.fooditems_admin
    if login_admin_userid != admin_userid:
        flash('you are not allowed to edit')
        return redirect(url_for('home'))
    if request.method == 'GET':
        return render_template('additem.html', cat_id=categoryid)
    else:
        name = request.form['iname']
        image = request.form['iimage']
        price = request.form['iprice']
        id1 = request.form['iid']
        sid = categoryid
        new_item = Items(item_name=name,
                         item_price=price,
                         item_image=image,
                         fooditems_id=id1)
        session.add(new_item)
        session.commit()
        flash("your Fooditem is added")
        return redirect(url_for('home'))


@app.route('/category/<int:categoryid>/items/<int:itemid>/edit',
           methods=['GET', 'POST'])
def edititem(categoryid, itemid):
    if 'email' not in login_session:
        flash("Please Login")
        return redirect(url_for('login'))
    admin = session.query(Admins).filter_by(
                                            admin_email=login_session['email']
                                            ).one_or_none()
    if admin is None:
        flash("Invalid User")
        return redirect(url_for('home'))
    fooditems = session.query(Fooditems).filter_by(
                                                   fooditems_id=categoryid
                                                   ).one_or_none()
    if not fooditems:
        flash("Category not found")
        return redirect(url_for('home'))
    item = session.query(Items).filter_by(
                                item_id=itemid,
                                fooditems_id=categoryid
                                ).one_or_none()
    if not item:
        flash('invalid item')
        return redirect(url_for('home'))
    login_admin_userid = admin.admin_userid
    admin_userid = fooditems.fooditems_admin
    if login_admin_userid != admin_userid:
        flash('you are not allowed to edit')
        return redirect(url_for('home'))
    if request.method == 'POST':
        name = request.form['iname']
        image = request.form['iimage']
        price = request.form['iprice']
        item = session.query(Items).filter_by(fooditems_id=categoryid,
                                              item_id=itemid).one_or_none()
        if item:
            item.item_name = name
            item.item_image = image
            item.item_price = price
        else:
            flash('no items')
            return redirect(url_for('home'))
        session.add(item)
        session.commit()
        flash('updated successfully')
        return redirect(url_for('home'))
    else:
        edit = session.query(Items).filter_by(item_id=itemid).one_or_none()
        if edit:
            return render_template('itemedit.html', iname=edit.item_name,
                                   iprice=edit.item_price,
                                   iimage=edit.item_image,
                                   catid=categoryid, iid=itemid)
        else:
            flash('no elements')
            return redirect(url_for('home'))


@app.route('/category/<int:categoryid>/items/<int:itemid>/delete')
def deleteitem(categoryid, itemid):
    if 'email' not in login_session:
        flash("Please Login")
        return redirect(url_for('login'))
    admin = session.query(Admins).filter_by(
                admin_email=login_session['email']
                ).one_or_none()
    if admin is None:
        flash("Invalid User")
        return redirect(url_for('home'))
    fooditems = session.query(Fooditems).filter_by(
                                         fooditems_id=categoryid).one_or_none()
    if fooditems is None:
        flash("Category not found")
        return redirect(url_for('home'))
    item = session.query(Items).filter_by(
                                item_id=itemid, fooditems_id=categoryid
                                ).one_or_none()
    if not item:
        flash('invalid item')
        return redirect(url_for('home'))
    login_admin_userid = admin.admin_userid
    admin_userid = fooditems.fooditems_admin
    if login_admin_userid != admin_userid:
        flash('you are not allowed to edit')
        return redirect(url_for('home'))
    item = session.query(Items).filter_by(item_id=itemid).one_or_none()
    if item:
        name = item.item_name
        session.delete(item)
        session.commit()
        flash('deleted successfully '+str(name))
        return redirect(url_for('home'))
    else:
        flash('item not found')
        return redirect(url_for('home'))


# login routing
@app.route('/login')
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# GConnect
@app.route('/gconnect', methods=['POST', 'GET'])
def gConnect():
    if request.args.get('state') != login_session['state']:
        response.make_response(json.dumps('Invalid State paramenter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    request.get_data()
    code = request.data.decode('utf-8')
    # Obtain authorization code
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps("""Failed to upgrade
                                the authorisation code"""), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check that the access token is valid.
    access_token = credentials.access_token
    myurl = (
        'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
        % access_token)
    header = httplib2.Http()
    result = json.loads(header.request(myurl, 'GET')[1].decode('utf-8'))
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
            response = make_response(json.dumps("""Token's user ID does notmatch
                                     given user ID."""), 401)
            response.headers['Content-Type'] = 'application/json'
            return response
    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps(
            """Token's client ID
            does not match app's."""),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Store the access token in the session for later use.
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps
                                 ('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    # Get user info
    userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()
    # ADD PROVIDER TO LOGIN SESSION
    login_session['name'] = data['name']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'
    admin_userid = getID(login_session['email'])
    print("\n"*5, "error", admin_userid)
    if not admin_userid:
        admin_userid = create_User(login_session)
    login_session['admin_userid'] = admin_userid
    flash("Successfully logged in")
    return "Successfully verified user"


def create_User(login_session):
    email = login_session['email']
    User = Admins(admin_email=email)
    session.add(User)
    session.commit()
    admins = session.query(Admins).filter_by(admin_email=email).first()
    admin_userid = admins.admin_userid
    return admin_userid


def getID(admin_email):
    try:
        admin = session.query(Admins).filter_by(admin_email=admin_email).one()
        return admin.admin_userid
    except Exception as e:
        print(e)
        return None


# Gdisconnect
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps
                                 ('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    header = httplib2.Http()
    result = header.request(url, 'GET')[0]
    if result['status'] == '200':
        # Reset the user's session.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['email']
        response = redirect(url_for('home'))
        response.headers['Content-Type'] = 'application/json'
        flash("Logged out Successfully", "success")
        return response
    else:
        # if given token is invalid, unable to revoke token
        response = make_response(json.dumps('Failed to revoke token for user'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/logout')
def Logout():
    if 'email' in login_session:
        # flash('You are signed out')
        return gdisconnect()


@app.context_processor
def inject_all():
    category = session.query(Fooditems).all()
    return dict(mycategories=category)
if __name__ == '__main__':
    app.secret_key = "itemcatalog"
    app.run(debug=True, host="localhost", port=5000)
