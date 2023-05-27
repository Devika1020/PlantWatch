import os
from doctest import debug
from flask import Flask, render_template, request, session, redirect, flash, send_file,url_for
from flask.sessions import SecureCookieSession
from flask import Flask, render_template, jsonify, request, Markup

import utils
from werkzeug.utils import secure_filename
from DBConnection import Db
from datetime import datetime
import requests

from model import predict_image

app = Flask(__name__, template_folder='template', static_url_path='/static/')
UPLOAD_FOLDER = './static/image'

ALLOWED_EXTENSIONS = {'txt', 'pdf','png','jpg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "asdff"



@app.route('/')
def ind():
    return render_template("HomePage.html")


@app.route('/HomePage')
def HomePage():
    return render_template("HomePage.html")


@app.route('/search')
def search():
    return render_template("User/search_symptoms.html")


@app.route('/Login')
def login():
    return render_template("login.html")


@app.route('/Adminhome')
def Adminhome():
    return render_template("AdminHome.html")


@app.route('/Userhome')
def Userhome():
    return render_template("User/Userhome.html")

@app.route('/Shophome')
def Shophome():
    return render_template("Shop/ShopHome.html")

@app.route('/LogOut')
def logOut():
    return render_template("LogOut.html")


@app.route('/login1', methods=['post'])
def login1():
    name = request.form['un']
    password = request.form['pass']
    session['lid'] = name
    qry = "select * from login where admin_id='" + name + "' and password='" + password + "'"
    ob = Db()
    print(qry)
    res = ob.selectOne(qry)
    if res is not None:
        return Adminhome()
    qry = "select * from user_details where user_id='" + name + "' and password='" + password + "'"
    ob = Db()
    print(qry)
    res = ob.selectOne(qry)
    if res is not None:
        return Userhome()
    qry = "select * from shops where idshop ='" + name + "' and password='" + password + "'"
    ob = Db()
    print(qry)
    res = ob.selectOne(qry)
    if res is not None:
        return Shophome()
    return "<script>alert('invalid');window.location='/';</script>"


#----------------------------------------------Admin----------------------------------------#
@app.route('/LinkAddPlantCategory')
def LinkAddParty():
    return render_template("AddPlantCategory.html")

@app.route('/LinkAddsellCategory')
def LinkAddSarty():
    return render_template("AddSellCategory.html")


@app.route('/ShopViewCategory')
def ShopViewCategory():
    qry = "select * from selling_category"
    ob = Db()
    print(qry)
    res = ob.select(qry)
    return render_template("Shop/ShopViewCategory.html", data=res)

@app.route('/add_to_shop')
def add_to_shop():
    ob = Db()
    shop = session['lid']
    id = request.args.get('id')
    qry = "select * from selling_category where id_category = '"+str(id)+"' and idshop ='"+str(shop)+"' "
    res = ob.selectOne(qry)
    if res == None:
        q = "insert into selling_category values(null,'" + id + "','"+shop+"' )"
        ob.insert(q)
    return redirect(url_for('LinkAddCategoryshop'))

@app.route('/ViewCategoryshop')
def ViewCategoryshop():
    ob = Db()
    shop = session['lid']
    qry = "select selling_category.*, plant_category.* from selling_category join plant_category where plant_category.idplant_category = selling_category.id_category and selling_category.idshop ='"+str(shop)+"' "
    res = ob.select(qry)
    return render_template("Shop/ViewCategoryshop.html", data=res)

@app.route('/additemshop')
def additemshop():
    id = request.args.get('id')
    return render_template("Shop/additemshop.html",id=id )

    # id = request.args.get('id')
    # jd = request.args.get('jd')
    # # qry = "select plant_details.*, category.* from category join plant_details where category.idcategory ='"+str(id)+"' and category.idcategory = plant_details.category_id "
    # qry = "select * from category where idplant_category ='"+str(id)+"' "
    # ob = Db()
    # print(qry)
    # res = ob.select(qry)
    # session['itemtocat'] = jd
    # return render_template("Shop/AddPlantshop.html", data=res)

@app.route('/add_plant_to_shop')
def add_plant_to_shop():
    ob = Db()
    shop = session['lid']
    cat =session['itemtocat']
    id = request.args.get('id')
    qry = "select * from shop_items where id_item = '" + str(id) + "' and idshop ='"+str(shop)+"' "
    res = ob.selectOne(qry)
    if res == None:
        qry = "select * from category where idcategory = '" + str(id) + "' "
        res = ob.selectOne(qry)
        print(res)
        name = res['name']
        return render_template("Shop/add_plant.html",item_id =id, item_name = name)
    return redirect(url_for('ViewPlantshop',id =cat))


@app.route('/adding_item',methods=['post'])
def adding_item():
    ob = Db()
    shop = session['lid']
    cat = request.form['idsellcat']
    name = request.form['name']
    qty = request.form['qty']
    price = request.form['price']
    q = "insert into shop_items values(null,'" + cat + "','" + price + "','" + qty + "','" + shop + "','" + name + "' )"
    ob.insert(q)
    return redirect(url_for('Viewitemshop', id=cat))




@app.route('/Viewitemshop')
def Viewitemshop():
    id = request.args.get('id')
    ob = Db()
    shop = session['lid']
    q = "select * from shop_items where idselling_category ='"+id+"' and idshop ='"+str(shop)+"' "
    res = ob.select(q)
    return render_template("Shop/Viewitemshop.html", data=res)
    # # qry = "select shop_items.*, plant_details.* from shop_items join plant_details where shop_items.idshop ='"+str(shop)+"' and shop_items.idselling_category = '"+str(id)+"' and shop_items.id_item = plant_details.idplant_details "
    # qry = "select shop_items.*, category.name from shop_items join category where shop_items.id_item = category.idcategory and shop_items.idshop ='"+str(shop)+"' "
    # print(qry)
    # res = ob.select(qry)
    # print(res)
    # return render_template("Shop/Viewitemshop.html", data=res)






@app.route('/AddPlantCategory',methods=['post'])
def AddPlantCategory():
    name = request.form['TxtName']
    ob = Db()
    q = "insert into plant_category values(null,'" + name + "')"
    ob.insert(q)
    return "<script>alert('Inserted succesfully');window.location='/Adminhome';</script>"

@app.route('/AddSellCategory',methods=['post'])
def AddSellCategory():
    name = request.form['TxtName']
    ob = Db()
    q = "insert into selling_category values(null,'" + name + "')"
    ob.insert(q)
    return "<script>alert('Inserted succesfully');window.location='/LinkAddsellCategory';</script>"

#----------------------------------------------Admin----------------------------------------#
@app.route('/LinkShopRegister')
def LinkShopRegister():
    return render_template("AddShop.html")


@app.route('/shops_register',methods=['post'])
def shops_register():
    txtid = request.form['txtId']
    name = request.form['txtName']
    address = request.form['address']
    phone = request.form['phone']
    mail = request.form['txtMail']
    txtpass = request.form['txtpass']
    ob = Db()
    q = "insert into shops values( '" + txtid + "','" + address + "','" + phone + "','" + mail + "','" + txtpass + "','"+name+"')"
    ob.insert(q)
    return "<script>alert('Inserted successfully');window.location='/Adminhome';</script>"


@app.route('/search_action',methods=['post'])
def search_action():
    name = request.form['txtSym']
    ob = Db()
    q = "select * from disease_solution where symptom like '%" + name + "%' "
    data= ob.select(q)
    if data is not None:
        return render_template('User/search_result.html', data=data)
    return "<script>alert('No Data Found');window.location='/search';</script>"


@app.route('/view_shop')
def view_shop():
    ob = Db()
    data = None
    res = ob.select("select * from shops")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Adminhome';</script>"
    return render_template('ViewShop.html', data=res)


@app.route('/view_shop_user')
def view_shop_user():
    ob = Db()
    data = None
    res = ob.select("select * from shops")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/search';</script>"
    return render_template('User/ViewShop.html', data=res)

# user section by captain

@app.route('/user_view_cat')
def user_view_cat():
    id = request.args.get('id')
    ob = Db()
    session['userviewshop'] = id
    res = ob.select("select shop_items.*,selling_category.* FROM shop_items join selling_category on shop_items.idselling_category=selling_category.idselling_category where shop_items.idshop='"+id+"' ")
    return render_template('User/UserViewItems.html', data=res)

@app.route('/userViewPlantshop')
def userViewPlantshop():
    id = request.args.get('id')
    ob = Db()
    shop = session['userviewshop']
    res = ob.select("select shop_items.*, category.name from shop_items join category where shop_items.id_item = category.idcategory and shop_items.idselling_category ='"+str(id)+"' and shop_items.idshop='"+str(shop)+"' ")
    return render_template('User/userViewPlantshop.html', data=res, idsellcat=id)


@app.route('/add_item_quantity')
def add_item_quantity():
    id = request.args.get('id')
    ob = Db()
    shop = session['userviewshop']
    return render_template('User/AddItemToCart.html',idsellcat=id)



@app.route('/add_to_cart',methods=['post'])
def add_to_cart():
    shop = session['userviewshop']
    user = session['lid']
    idshopitem = request.args.get('id')
    quantity = request.form['quantity']
    price = request.form['price']
    qty = request.form['qty']
    idsellcat = request.form['idsellcat']
    p = int(price) / int(quantity)
    print(p)
    amount = int(qty) * p
    print(amount)
    ob = Db()
    res = ob.selectOne("select * from itemcart where idshopitem='" + idshopitem + "' and  userid ='"+str(user)+"' ")
    if res == None:
        q = "insert into itemcart values(null, '" + user+ "','" + str(idshopitem) + "','" + str(qty) + "','" + str(amount) + "')"
        ob.insert(q)
    else:
        q = "update itemcart set qty='" + str(qty) + "', price ='"+str(amount)+"'  where idshopitem='" + idshopitem + "' and userid ='"+str(user)+"' "
        ob.update(q)
    return redirect(url_for('user_view_cat', id=shop))


import sys
sys.setrecursionlimit(1500)



@app.route('/GetOneCart')
def GetOneCart():
    ob = Db()
    user = session['lid']
    res = ob.select("select itemcart.*, shop_items.item_name, shop_items.idshop from itemcart join shop_items on itemcart.idshopitem = shop_items.idshop_items where itemcart.userid = '" + user + "'")
    p = ob.select("select price from itemcart where userid = '" + str(user) + "' ")
    total = int(0)
    for i in p:
        a = i['price']
        total = total + float(a)
    print(total)
    if total == 0:
        return "<script>alert('Cart is Empty');window.location='/Userhome';</script>"
    session['cartamount'] =total
    return render_template('User/cart.html', data=res,amount =total)



@app.route('/cartremove')
def cartremove():
    ob= Db()
    idcart = request.args.get('id')
    user = session['lid']
    q = "delete from itemcart where idcart ='" + idcart + "' and userid = '"+str(user)+"' "
    ob.delete(q)
    return redirect(url_for('GetOneCart'))

@app.route('/placeorder')
def placeorder():
    return render_template('User/card_validate.html',)

@app.route('/cardvalidate',methods=['post'])
def cardvalidate():
    ob = Db()
    acc = request.form['accno']
    cvv = request.form['cvv']
    carh = request.form['cardholder']
    exp = request.form['exp']
    res = ob.selectOne("select * from account_table where account_number ='" + str(acc) + "' and cvv ='"+str(cvv)+"' and card_holder ='"+str(carh)+"' and exp_date ='"+str(exp)+"' ")
    if res == None:
        return "<script>alert('invalid account details');window.location='/Userhome';</script>"
    else:
        user = session['lid']
        total = session['cartamount']
        q = "insert into bills values(null,'" + user + "','" + str(total) + "', curdate() ,'processing' )"
        ob.insert(q)
        p = ob.selectOne("select idbills from bills where userid = '" + str(user) + "' and total_amount = '"+str(total)+"' and date = curdate() and status ='processing' ")
        idbill = p['idbills']

        res = ob.select("select itemcart.*, shop_items.item_name, shop_items.idshop, shop_items.idshop_items from itemcart join shop_items on itemcart.idshopitem = shop_items.idshop_items where itemcart.userid = '" + str(user) + "' ")
        a = []
        for i in res:
            idcart = i['idcart']
            shopid = i['idshop']
            idshopitem = i['idshop_items']
            quantity = i['qty']
            price = i['price']
            a.append(idcart)
            q = "insert into shop_bill values(null,'" + str(shopid) + "','" + str(idbill) + "',curdate(),'" + str(idshopitem) + "','" + str(quantity) + "','" + str(price) + "')"
            ob.insert(q)

        q = "update bills set status='payed' where idbills='" + str(idbill) + "'"
        ob.update(q)
        for i in a:
            q = "delete from itemcart where idcart='" + str(i) + "'"
            ob.delete(q)

    return redirect(url_for('myorder'))

@app.route('/myorder')
def myorder():
    ob = Db()
    user = session['lid']
    res = ob.select("select * from bills where userid ='"+str(user)+"' ")
    if res ==None:
        return "<script>alert('No Any Orders');window.location='/Userhome';</script>"
    return render_template('User/my_orders.html', data=res)

@app.route('/vieworders')
def vieworders():
    ob = Db()
    idbill = request.args.get('id')
    res = ob.select("select shop_bill.*,shop_items.item_name,shops.name from shop_bill join shop_items join shops where shop_bill.idbill ='"+str(idbill)+"' and shop_bill.idshopitem = shop_items.idshop_items and shops.idshop = shop_bill.shopid")
    return render_template('User/view_orders.html', data=res)

@app.route('/shoporders')
def shoporders():
    shop = session['lid']
    ob = Db()
    res = ob.select("select shop_bill.*,shop_items.item_name,shops.name from shop_bill join shop_items join shops where shop_bill.idshopitem = shop_items.idshop_items and shops.idshop = shop_bill.shopid and shop_items.idshop ='"+str(shop)+"'")
    return render_template('Shop/view_orders.html', data=res)

@app.route('/LinkShopView')
def LinkShopView():
    ob = Db()
    res = ob.select("select * from shops ")
    return render_template('ViewShop.html', data = res)

@app.route('/adminviewshoporders')
def adminviewshoporders():
    shop = request.args.get('id')
    ob = Db()
    res = ob.select("select shop_bill.*,shop_items.item_name,shops.name from shop_bill join shop_items join shops where shop_bill.idshopitem = shop_items.idshop_items and shops.idshop = shop_bill.shopid and shop_items.idshop ='" + str(shop) + "'")
    return render_template('view_orders.html', data=res)



@app.route('/ViewPlantCategory')
def ViewPlantCategory():
    ob = Db()
    data = None
    res = ob.select("select * from plant_category")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Adminhome';</script>"
    return render_template('ViewPlantCategory.html', data=res)

@app.route('/ViewSellCategory')
def ViewSellCategory():
    ob = Db()
    data = None
    res = ob.select("select * from selling_category")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Adminhome';</script>"
    return render_template('ViewSellCategory.html', data=res)


@app.route('/LinkEditPlantCategory')
def LinkEditParty():
    id = request.args.get('id')
    ob = Db()
    data = None
    res = ob.selectOne("select * from plant_category where idplant_category='" + id + "'")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Adminhome';</script>"
    return render_template('EditPlantCategory.html', data=res)


@app.route('/EditPlantCategory',methods=['post'])
def EditParty():
    id = request.form['id']
    name = request.form['TxtName']
    ob = Db()
    q = "update plant_category set name='" + name + "' where idplant_category='" + id + "'"
    ob.update(q)
    return "<script>alert('Updated succesfully');window.location='/Adminhome';</script>"


@app.route('/DeletePlantCategory')
def DeletePlantCategory():
    id = request.args.get('id')
    ob = Db()
    q = "delete from plant_category where idplant_category='" + id + "'"
    ob.delete(q)
    return "<script>alert('Deleted succesfully');window.location='/Adminhome';</script>"


@app.route('/LinkaddPlants')
def LinkaddPlants():
    id = request.args.get('id')
    session['pcid']=id
    return render_template("AddPlants.html")


@app.route('/AddPlants',methods=['post'])
def AddPlace():
    name = request.form['TxtName']
    pcid=session['pcid']
    ob = Db()
    q = "insert into category values(null,'" + name + "','"+pcid+"')"
    ob.insert(q)
    return "<script>alert('Inserted succesfully');window.location='/Adminhome';</script>"


@app.route('/ViewPlants')
def ViewPlants():
    id = request.args.get('id')
    ob = Db()
    data = None
    res = ob.select("select * from category where idplant_category='"+id+"'")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Adminhome';</script>"
    return render_template('ViewPlants.html', data=res)


@app.route('/LinkEditPlant')
def LinkEditPlant():
    id = request.args.get('id')
    ob = Db()
    data = None
    res = ob.selectOne("select * from category where idcategory='" + id + "'")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Adminhome';</script>"
    return render_template('EditPlant.html', data=res)


@app.route('/EditPlant',methods=['post'])
def EditPlace():
    id = request.form['id']
    name = request.form['TxtName']
    ob = Db()
    q = "update category set name='" + name + "' where idcategory='" + id + "'"
    ob.update(q)
    return "<script>alert('Updated succesfully');window.location='/Adminhome';</script>"


@app.route('/DeletePlant')
def DeletePlant():
    id = request.args.get('id')
    ob = Db()
    q = "delete from category where idcategory='" + id + "'"
    ob.delete(q)
    return "<script>alert('Deleted succesfully');window.location='/Adminhome';</script>"


@app.route('/LinkAddVariety')
def LinkAddVariety():
    id = request.args.get('id')
    session['cid']=id
    return render_template("AddVariety.html")


@app.route('/AddVariety',methods=['post'])
def AddVariety():
    name = request.form['TxtName']
    desc = request.form['Txtdesc']
    cid = session['cid']
    ob = Db()
    q = "insert into plant_details values(null,'" + name + "','" + desc + "','"+cid+"')"
    ob.insert(q)
    return "<script>alert('Inserted succesfully');window.location='/Adminhome';</script>"


@app.route('/ViewVariety')
def ViewVariety():
    id = request.args.get('id')
    ob = Db()
    data = None
    res = ob.select("select * from plant_details where category_id='" + id + "'")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Adminhome';</script>"
    return render_template('ViewVariety.html', data=res)


@app.route('/LinkEditPlantVariety')
def LinkEditPlantVariety():
    id = request.args.get('id')
    ob = Db()
    data = None
    res = ob.selectOne("select * from plant_details where idplant_details='" + id + "'")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Adminhome';</script>"
    return render_template('EditVariety.html', data=res)


@app.route('/EditVariety',methods=['post'])
def EditVariety():
    id = request.form['id']
    name = request.form['TxtName']
    desc = request.form['Txtdesc']
    ob = Db()
    q = "update plant_details set name='"+name+"',leaf_description='"+desc+"' where idplant_details='"+id+"'"
    ob.update(q)
    return "<script>alert('Updated succesfully');window.location='/Adminhome';</script>"


@app.route('/DeletePlantVariety')
def DeletePlantVariety():
    id = request.args.get('id')
    ob = Db()
    q = "delete from plant_details where idplant_details='" + id + "'"
    ob.delete(q)
    return "<script>alert('Deleted succesfully');window.location='/Adminhome';</script>"


@app.route('/LinkUploadImage')
def LinkUploadImage():
    id = request.args.get('id')
    session['cid']=id
    return render_template("uploadimage.html")


@app.route('/UploadImage',methods=['post'])
def UploadImage():
    cid = session['cid']
    file = request.files['TxtPhoto']
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    ob = Db()
    q = "insert into plant_image values(null,'"+cid+"','"+filename+"')"
    ob.insert(q)
    return ViewPlantCategory()


@app.route('/ViewImage')
def ViewImage():
    id = request.args.get('id')
    ob = Db()
    data = None
    res = ob.select("select * from plant_image where category_id='"+id+"'")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Adminhome';</script>"
    return render_template('ViewImage.html', data=res)


@app.route('/DeleteImage')
def DeleteImage():
    id = request.args.get('id')
    ob = Db()
    q = "delete from plant_image where idplant_image='" + id + "'"
    ob.delete(q)
    return "<script>alert('Deleted succesfully');window.location='/Adminhome';</script>"


@app.route('/LinkAddDisease')
def LinkAddDisease():
    id = request.args.get('id')
    session['cid']=id
    return render_template("AddDisease.html")


@app.route('/AddDisease',methods=['post'])
def AddDisease():
    name = request.form['TxtName']
    desc = request.form['Txtdesc']
    cid = session['cid']
    ob = Db()
    q = "insert into disease values(null,'" + cid + "','" + name + "','" + desc + "','no image uploaded')"
    ob.insert(q)
    return "<script>alert('Inserted succesfully');window.location='/Adminhome';</script>"


@app.route('/ViewDisease')
def ViewDisease():
    id = request.args.get('id')
    ob = Db()
    data = None
    res = ob.select("select * from disease where category_id='" + id + "'")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/ViewPlantCategory';</script>"
    return render_template('ViewDisease.html', data=res)


@app.route('/LinkEditDisease')
def LinkEditDisease():
    id = request.args.get('id')
    ob = Db()
    data = None
    res = ob.selectOne("select * from disease where iddisease='" + id + "'")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Adminhome';</script>"
    return render_template('EditDisease.html', data=res)


@app.route('/EditDisease',methods=['post'])
def EditDisease():
    did = request.form['id']
    name = request.form['TxtName']
    desc = request.form['Txtdesc']
    ob = Db()
    q = "update disease set disease_name='"+name+"',disease_desc='"+desc+"' where iddisease='"+did+"'"
    ob.update(q)
    return "<script>alert('Updated succesfully');window.location='/Adminhome';</script>"


@app.route('/DeleteDisease')
def DeleteDisease():
    id = request.args.get('id')
    ob = Db()
    q = "delete from disease where iddisease='" + id + "'"
    ob.delete(q)
    return "<script>alert('Deleted succesfully');window.location='/Adminhome';</script>"


@app.route('/LinkUploadImageDisease')
def LinkUploadImageDisease():
    id = request.args.get('id')
    session['did']=id
    return render_template("UploadImageDisease.html")


@app.route('/UploadImageD',methods=['post'])
def UploadImageD():
    did = session['did']
    file = request.files['TxtPhoto']
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    ob = Db()
    q = "update disease set image_path='"+filename+"' where iddisease='"+did+"' "
    ob.update(q)
    return Adminhome()


@app.route('/ViewUserQueryAdmin')
def ViewUserQueryAdmin():
    ob = Db()
    data = None
    res = ob.select("select * from user_query")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Adminhome';</script>"
    return render_template('ViewUserQueryAdmin.html', data=res)


@app.route('/LinkReplyQuery')
def LinkReplyQuery():
    id = request.args.get('id')
    session['qid']=id
    return render_template("ReplyQuery.html")


@app.route('/ReplyQuery',methods=['post'])
def ReplyQuery():
    qid=session['qid']
    desc = request.form['TxtReply']
    ob = Db()
    q = "update user_query set reply='" + desc + "' where iduser_query='" + qid + "'"
    ob.update(q)
    return "<script>alert('Updated succesfully');window.location='/Adminhome';</script>"
#----------------------------------------------User-----------------------#

@app.route('/LinkAddUser')
def LinkAddUser():
    return render_template("AddUser.html")


@app.route('/AddUser',methods=['post'])
def AddUser():
    user=request.form['TxtUser']
    name = request.form['TxtName']
    address = request.form['TxtAddress']
    phone=request.form['TxtPhone']
    email = request.form['TxtEmail']
    password = request.form['TxtPassword']
    ob = Db()
    q = "insert into user_details values('"+user+"','" + name + "','" + address + "','" + phone + "','"+email+"','"+password+"')"
    ob.insert(q)
    return "<script>alert('Inserted succesfully');window.location='/HomePage';</script>"


#--------------------------------User-------------------#
# @app.route('/LinkUploadLeafImage')
# def LinkUploadLeafImage():
#     ob = Db()
#     data = None
#     res = ob.select("select p.*,c.* from plant_image as p join category as c on c.idcategory=p.category_id")
#     if res:
#         data = res
#     if data == None:
#         return "<script>alert('No Data Found');window.location='/Userhome';</script>"
#     return render_template('User/ViewPlantImageUser.html', data=res)

@app.route('/LinkUploadLeafImage')
def LinkUploadLeafImage():
    ob = Db()
    data = None

    res = ob.select("SELECT p.*, c.*, pd.leaf_description,pd.name as nam FROM plant_image p JOIN category c ON c.idcategory = p.category_id JOIN plant_details pd ON pd.category_id = p.category_id")

    if res:
        data = res

    if data == None:
        return "<script>alert('No Data Found');window.location='/Userhome';</script>"
    return render_template('User/ViewPlantImageUser.html', data=data)


@app.route('/ViewDiseases')
def ViewDiseases():
    ob = Db()
    data = None
    res = ob.select("select * from disease")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Userhome';</script>"
    return render_template('User/ViewDiseaseImageUser.html', data=res)


@app.route('/LinkAbc')
def LinkAbc():
    return  render_template("User/index.html")


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        try:
            file = request.files['file']


            img = file.read()

            prediction = predict_image(img)
            print(prediction)
            res = Markup(utils.disease_dic[prediction])
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                session['img'] = filename
            return render_template('User/display.html', status=200, result=res)
        except:
            pass
    return render_template('User/index.html', status=500, res="Internal Server Error")


@app.route('/ViewMorePlant')
def ViewMorePlant():
    id = request.args.get('id')
    ob = Db()
    data = None
    res = ob.select("select * from plant_image where category_id='" + id + "'")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Userhome';</script>"
    return render_template('User/ViewMorePlant.html', data=res)


@app.route('/ViewMoreDisease')
def ViewMoreDisease():
    id = request.args.get('id')
    ob = Db()
    data = None
    res = ob.select("select * from disease where category_id='" + id + "'")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Userhome';</script>"
    return render_template('User/ViewMoreDisease.html', data=res)


@app.route('/LinkAddUserQuery')
def LinkAddUserQuery():
    return render_template("User/AddUserQuery.html")


@app.route('/AddUserQuery',methods=['post'])
def AddUserQuery():
    uid = session['lid']
    query = request.form['Txtdesc']
    ob = Db()
    q = "insert into user_query values(null,'" + uid + "','" + query + "','pending',curdate())"
    ob.insert(q)
    return "<script>alert('Inserted succesfully');window.location='/Userhome';</script>"


@app.route('/ViewUserQuery')
def ViewUserQuery():
    uid = session['lid']
    ob = Db()
    data = None
    res = ob.select("select * from user_query where user_id='" + uid + "'")
    if res:
        data = res
    if data == None:
        return "<script>alert('No Data Found');window.location='/Userhome';</script>"
    return render_template('User/ViewUserQuery.html', data=res)

if __name__ == '__main__':
    app.run(debug=True)