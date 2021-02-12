from flask import Flask, render_template, request, redirect,url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask import render_template
from flask_migrate import Migrate
from datetime import datetime
from config import Config
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate=Migrate(app,db)

class Product(db.Model):
    id =db.Column(db.Integer,primary_key=True)
    prod_name=db.Column(db.String(70),unique=True)
    prod_qty=db.Column(db.Integer)

    def __repr__(self):
        return '<Product {} {} {} >'.format(self.id,self.prod_name,self.prod_qty)

class Location(db.Model):
    location_id=db.Column(db.Integer,primary_key=True)
    Location_name=db.Column(db.String(70),unique=True)
    def __repr__(self):
        return '<Location {}>'.format(self.Location_name)


class Product_Movement(db.Model):
    movement_id=db.Column(db.Integer,primary_key=True)
    timestamp=db.Column(db.DateTime, default=datetime.utcnow)
    loc=db.Column(db.String(70))
    prod_id=db.Column(db.Integer,db.ForeignKey('product.id'))
    qty=db.Column(db.Integer)
    def __repr__(self):
        return '<Product Movement {} {} {} {}>'.format(self.timestamp,self.loc,self.prod_id,self.qty)
class Report(db.Model):
    report_id=db.Column(db.Integer,primary_key=True)
    loc = db.Column(db.String(70))
    product_id=db.Column(db.Integer)
    product_name=db.Column(db.String(70),unique=True)
    qty = db.Column(db.Integer)

    def __repr__(self):
        return '<Report {} {} {} >'.format(self.loc,self.product_name,self.qty)
@app.route('/')
def home():
    return  render_template('base.html')
@app.route('/product')
def product():
    data=Product.query.all()
    m = db.inspect(Product)
    return render_template('product.html',column=m,products=data)

@app.route('/addproduct', methods=["POST","GET"])
def addproduct():
    if request.method == "POST":

        prd_name=request.form['prd_name']
        prd_qty=request.form['prd_qty']
        print('ans:',prd_qty)
        if prd_name==None or prd_qty==None:
            flash('Enter both values')
            return  redirect(url_for('addproduct'))
        if len(prd_name)>2 and len(prd_qty)>0:
            p=Product(prod_name=prd_name,prod_qty=prd_qty)

            db.session.add(p)
            db.session.commit()
            print("successfully added :)")
        else:
            flash('product name should be longer than a 2 characters and prod quantity should be greater than 0.')
            return redirect(url_for('addproduct'))
    return render_template('addprd.html')

@app.route('/editprod/<prdt_name>',methods=["POSt","GET"])
def edit_prod(prdt_name):

    result = Product.query.filter_by(prod_name=prdt_name ).first()
    if request.method=="POST":
        # l = Location(Location_name=request.form["locn_name"])
        result.prod_name = request.form["prd_name"]
        result.prod_qty = request.form["prd_qty"]
        if len(result.prod_name) > 2 and int( result.prod_qty) >= 0:

            db.session.add(result)
            db.session.commit()
            return redirect(url_for('product'))
        else:
            flash( 'product name should be longer than a 2 characters and prod qty should be ghreater than or qeual to 0.')
            return redirect(url_for('product'))
    return render_template('editproduct.html',products=result)


@app.route('/addlocation',methods=["POST","GET"])
def location():
    if request.method == "POST":
        loc_name=request.form["loc_name"]
        if len(loc_name)>=3:
            l=Location(Location_name=loc_name)
            db.session.add(l)
            db.session.commit()
            print("successfully added :)")
        else:
            flash('location name should be longer than 3 characters.')
            return redirect(url_for('location'))
        return redirect(url_for('show_locns'))
    return render_template('addlocation.html')
@app.route('/showlocations')
def show_locns():
    data = Location.query.all()
    # print('data:',data)
    return render_template('showlocations.html',locations=data)

@app.route('/editlocation/<loc_name>',methods=["POSt","GET"])
def edit_locn(loc_name):

    result = Location.query.filter_by(Location_name=loc_name ).first()
    print(result.location_id)
    if request.method=="POST":
        # l = Location(Location_name=request.form["locn_name"])
        result.Location_name=request.form["locn_name"]
        if len(result.Location_name) >= 3:
            db.session.add(result)
            db.session.commit()
        else:
            flash('location name should be longer than 3 characters.')
            return redirect(url_for('show_locns'))
        return redirect(url_for('show_locns'))
    return render_template('editlocation.html',location=result)

@app.route('/addproductmvmt',methods=["POST","GET"])
def add_product_movement():
    locn = Location.query.all()
    if request.method=="POST":
        from_lcn=request.form['from_location']
        to_lcn=request.form['to_location']   #from data assign to local variable to_lcn
        prd_id=request.form['prd_id']
        qty=request.form['qty']
        result=Product.query.filter_by(id=prd_id).first()
        if len(qty)<=0:
            flash('Enter quantity')
            return redirect(url_for('add_product_movement'))
        if result==None:
            flash('Product id submitted does not match the id in product table pls sepcify valid prod id.')
            return redirect(url_for('add_product_movement'))
        if from_lcn !='none' and to_lcn=='none':
            # check_from_location = Product_Movement.query.filter_by(loc=from_lcn,prod_id=prd_id).first()
            from_report_location=Report.query.filter_by(loc=from_lcn,product_id=prd_id).first()

            print('product_movement: ',from_report_location ,result)
            if from_report_location==None:
                flash('location does not contain any product of specify prod id or locantion is not avilable.')
                return redirect(url_for('add_product_movement'))
            if from_report_location.qty>=int(qty):
                from_report_location.product_name=result.prod_name
                from_report_location.qty=from_report_location.qty-int(qty)
                check_from_location=Product_Movement(loc=from_lcn,prod_id=prd_id,qty= from_report_location.qty)
                db.session.add(check_from_location)
                db.session.add(from_report_location)
                db.session.commit()
                return redirect(url_for('show_prd_mvmt'))
            else:
                flash('there is less amount of product available at specify location. Pls decrease qty')
                return redirect(url_for('add_product_movement'))

            return redirect(url_for('show_prd_mvmt'))
        elif to_lcn!='none' and from_lcn=='none':
            check_to_location=Product_Movement.query.filter_by(loc=to_lcn,prod_id=prd_id).first()
            to_report_location=Report.query.filter_by(loc=to_lcn,product_id=prd_id).first()
            print('toreport_location name: ', to_report_location)
            # if check_to_location==None:
            #     flash('some value needs to be assign to a location first')
            #     return redirect(url_for('add_product_movement'))
            if to_report_location:

                quantity=to_report_location.qty+int(qty)
                sqlqry = Product_Movement(loc=to_lcn, prod_id=prd_id, qty=quantity)
                # report_query = Report(loc=to_lcn,product_name=result.prod_name, product_id=prd_id, qty=quantity)
                to_report_location.qty=to_report_location.qty+int(qty)
                db.session.add(sqlqry)
                db.session.add(to_report_location)
                # db.session.commit()
                result.prod_qty = result.prod_qty - int(qty)
                db.session.add(result)
                db.session.commit()

            elif not to_report_location:
                if int(qty)<=result.prod_qty:
                    report_query=Report(loc=to_lcn, product_name=result.prod_name,product_id=prd_id,qty=int(qty))
                    sqlqry=Product_Movement(loc=to_lcn, prod_id=prd_id ,qty=qty)
                    result.prod_qty = result.prod_qty-int(qty)
                    db.session.add(sqlqry)
                    db.session.add(report_query)
                    db.session.add(result)
                    db.session.commit()
                else:
                    flash('product avilable quantity is less than quantity specify pls enter quantity less than prod qty.')
                    return redirect(url_for('add_product_movement'))


            return redirect(url_for('show_prd_mvmt'))
        elif to_lcn!='none' and from_lcn !='none':
            check_from_location = Product_Movement.query.filter_by(loc=from_lcn,prod_id=prd_id).first()
            from_report_location = Report.query.filter_by(loc=from_lcn, product_id=prd_id).first()
            print('product_movement',check_from_location)
            check_to_location = Product_Movement.query.filter_by(loc=to_lcn).first()
            to_report_location = Report.query.filter_by(loc=to_lcn, product_id=prd_id).first()
            print('product_movement',check_to_location)
            if from_report_location==None:
                flash('some value needs to be assign to a location first check in show prod mvmt if location is contian any prod')
                return redirect(url_for('add_product_movement'))
            if from_report_location.qty >= int(qty) and to_report_location:
                from_report_location.qty=from_report_location.qty-int(qty)
                check_from_location.qty = from_report_location.qty
                to_report_location.qty=to_report_location.qty+int(qty)
                check_to_location.qty=to_report_location.qty
                db.session.add(check_from_location)
                db.session.add(from_report_location)
                db.session.add(to_report_location)
                db.session.add(check_to_location)
                db.session.commit()
            elif not to_report_location:
                if int(qty)<=from_report_location.qty:
                    from_report_location.qty = from_report_location.qty - int(qty)
                    check_from_location.qty = from_report_location.qty
                    to_report_query=Report(loc=to_lcn, product_name=result.prod_name,product_id=prd_id,qty=int(qty))
                    sqlqry=Product_Movement(loc=to_lcn, prod_id=prd_id ,qty=qty) #adding query to product movement
                    result.prod_qty = result.prod_qty-int(qty)
                    db.session.add(check_from_location)
                    db.session.add(sqlqry)
                    db.session.add(from_report_location)
                    db.session.add(to_report_query)
                    db.session.commit()
                else:
                    flash('product avilable quantity is less than quantity specify pls enter quantity less than prod qty.')
                    return redirect(url_for('add_product_movement'))
            else:
                flash('there is less amount of product available at specify location. Pls decrease qty')
                return redirect(url_for('add_product_movement'))
            return redirect(url_for('show_prd_mvmt'))

    return render_template('addprdmvmt.html',locations=locn)

@app.route('/report')
def show_report():
    data= Report.query.all()
    return render_template('reportfile.html',report=data)
@app.route('/showprodmvmt')
def show_prd_mvmt():
    prod_mvmt=Product_Movement.query.all()
    product_name={}
    name=[key.prod_id for key in prod_mvmt ]
    for n in name:
        x=Product.query.filter_by(id=n).first()
        if x:
            product_name[n]=x.prod_name
    return render_template('showprdmvmt.html',products_name=product_name,product_mvmt=prod_mvmt)
if __name__ == '__main__':
    app.run()
