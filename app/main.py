from flask import Flask, render_template ,request,redirect ,flash, send_file
from flask_login import LoginManager, login_user, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime, func,extract,insert
from flask.helpers import url_for
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date,timedelta,datetime
from functools import wraps
# from flaskwebgui import FlaskUI # import FlaskUI
import os, sys
import sqlite3
import csv
# os.add_dll_directory(r"C:\Program Files\GTK3-Runtime Win64\bin")
from weasyprint import HTML


app = Flask(__name__)
db = SQLAlchemy(app)
# ui = FlaskUI(app, width=500, height=500) # add app and parameters


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.products import *
from models.stock import *
from models.users import *
from models.orderdetails import *
from models.orders import *
from models.payments import *
from models.deliveries import *


# app.config.from_object(Development)
app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=720)
app.config['SQLALCHEMY_DATABASE_URI'] =  "postgresql://postgres:21post@localhost:5432/alchemy"


# conn = sqlite3.connect('alchemy.db') 
# c = conn.cursor()


@app.before_first_request
def create_tables():
    #db.drop_all()
    db.create_all()
    
    login_manager = LoginManager()
    login_manager.login_view = 'login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return Users.query.get(int(user_id))


@app.route('/add_csv')
def add_csv():
    with open('inventory.csv', 'r', encoding="utf-8") as file:
        csv_reader = csv.reader(file, delimiter=',')
        rows = [{"id": row[0], "name": row[1],"bp": row[2],"sp": row[3],"user_id": row[4] } 
            for row in csv_reader]
        
        for i in rows:
            print(i)
            add = Products(id= i['id'],name = i['name'] ,bp=i['bp'] ,sp=i['sp'] ,user_id=i['user_id'] )
            db.session.add(add)
            db.session.commit()
        return redirect('/inventory')


def role_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if current_user.role != 'Admin' :
            flash('You are not authorised to access this page.')
            return "<h1> Access  Denied </h1>"
        else:        
            
            return  f(*args, **kwargs)
    return wrapper
        

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated :
            flash('Login first to access this page.')
            return redirect('/login')
        else:        
           
            return  f(*args, **kwargs)
    return wrapper
        

@app.route('/')
def home():
    
    return render_template('index.html')


@app.route('/login')
def login():
    
    return render_template('login.html' )

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/signup')
def signup():
    
    return render_template('sign-up.html' )


@app.route('/admin')
@role_required
@login_required
def admin():
    
    records =Users.query.all() 
    
    return render_template('admin.html',myUsers=records)

@app.route('/signup', methods=['POST'])
def signup_post():
  
    email = request.form.get('email')
    name = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role')
    

    user = Users.query.filter_by(email=email).first()

    if user:
        flash('Email address already exists')
        return redirect(url_for('signup'))

    new_user = Users(email=email, username=name, password=generate_password_hash(password, method='sha256'),role=role)

    db.session.add(new_user)
    db.session.commit()
    
    login_user(new_user)

    return redirect('/')


@app.route('/login', methods=['POST'])
def login_post():
   
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = Users.query.filter_by(email=email).first()
    
    if not user or not check_password_hash(user.password, password) :
        flash('Please check your login details and try again.')
        return redirect(url_for('login'))
    
    login_user(user, remember=remember)
    
    return redirect('/')

@app.route('/create_user', methods=['POST'])
def create_user():
    username =request.form['username']
    role= request.form['role']
    password = request.form['password']
    email = request.form['email']
    
    rows = Users(username=username,role=role,password=password,email=email)
    db.session.add(rows)
    db.session.commit()
   
    return redirect('/admin')

@app.route('/delete_user',methods=['post','get'])
def delete_user():

    id = request.form['user_id']
    row = Users.query.filter_by(id = id).one()
     
    db.session.delete(row)
    db.session.commit()
    
    return redirect('/admin')

	
@app.route('/uploader', methods = ['GET', 'POST'])
def uploader():
   if request.method == 'POST':
      f = request.files['file']
      f.save(secure_filename(f.filename))
      flash('file uploaded successfully')
      return redirect('/inventory')


@app.route('/inventory')
@login_required
def inventory():
    
    records =Products.query.all() 
    name=current_user.username
   
    return render_template('inventory.html',myData=records,name= name)

@app.route('/stock')
@login_required
def stock():
    records =Stock.query.all() 
    
    return render_template('stock.html',myStock=records)

@app.route('/sales')
@login_required
def sales():
    
    records =OrderDetails.query.all()
    
    return render_template('sales.html',mySales=records)


@app.route('/payments')
@login_required
@role_required
def payment():
    
    rowz = Payments.query.all()
    
    return render_template('payments.html', payments= rowz)


@app.route('/delivery')
@login_required
@role_required
def delivery():
    
    rowz = Deliveries.query.all()
    
    return render_template('delivery.html', delis= rowz)


@app.route('/orders')
@login_required
@role_required
def orders():
    
    rowz = Orders.query.all()
    
    return render_template('orders.html', orders= rowz)

    
@app.route('/sales/<int:id>')
def view_sales(id):

    recordss = OrderDetails.query.filter_by(product_id =id)
    
    return render_template('sales.html',mySales=recordss)
    

@app.route('/stock/<int:id>')
def view_stock(id):

    recordss = Stock.query.filter_by(product_id =id)
    rems = 0
    srems = 0
    rem =  Stock.query.with_entities(func.sum(Stock.quantity)).filter(Stock.product_id == id ).first()
    for i in rem: 
        rems = i  
    srem = OrderDetails.query.with_entities(func.sum(OrderDetails.quantity)).filter(OrderDetails.pid == id).first()
    for i in srem:
        srems = i
    
    if rems == None :
        remainderr = 0
        if srems == None:
            remainderr = int(rems) - int(srems)
            return render_template('stock.html', remainder = remainderr)
    
    remainderr = int(rems) - int(srems)
    
    return render_template('stock.html',myStock=recordss, remainder = remainderr)
    


@app.route('/makeorder')
@login_required
def make_order():
    
    rowz = Orders(user_id = current_user.id , created_at= datetime.now() )
    db.session.add(rowz)
    db.session.commit()
    
    url = "/order/"+str(rowz.id)
    
    return redirect(url)


@app.context_processor
def utility_processor():
    def compute_quanity(orderID: int):
       
        inv = OrderDetails.query.with_entities(OrderDetails.quantity,Products.sp).join(Products).filter(OrderDetails.order_id == orderID).all()
        totals = list(map(lambda tupl: tupl[0]* tupl[1], inv))
        return sum(totals)
            
    return dict(compute_quanity=compute_quanity)


@app.route('/receipt', methods = ['GET', 'POST'])
def receipt():
    
    oid = Orders.query.order_by(Orders.id.desc()).first()
    id = oid.id
    od = OrderDetails.query.with_entities( Products.name,OrderDetails.quantity ,Products.sp).join(Products).filter(OrderDetails.order_id == id)
    
    
    posted_data = request.get_json() or {}
    today = date.today()
    default_data = {
        'time': datetime.now(),
        'from_addr': {
            'addr1': '12345 Sunny Road',
            'addr2': 'Sunnyville, CA 12345',
            'company_name': 'IMS Systems Ltd'
        },
        'invoice_number': id,
        'items': od
        
    }

    time = posted_data.get('time', default_data['time'])
    from_addr = posted_data.get('from_addr', default_data['from_addr'])
    invoice_number = posted_data.get('invoice_number',  default_data['invoice_number'])
    items = posted_data.get('items', default_data['items'])
    
    rendered = render_template('receipt.html', 
                            date = today, 
                            from_addr = from_addr,
                            items = items,
                            id = id ,
                            invoice_number = invoice_number,
                            time = time)
    html = HTML(string=rendered)
    html.write_pdf('./invoice' +  str(id) +'.pdf')
    return send_file(
            './invoice'+  str(id) +'.pdf'
        )


@app.route('/order/<int:id>', methods=['GET','POST'])
def search(id):
    
    if request.method == 'GET':
        
        p = Products.query.all()
        pay = Payments.query.filter(Payments.order_id == id)
        ods = OrderDetails.query.with_entities(OrderDetails.order_id, OrderDetails.pid,OrderDetails.quantity ,Products.name,Products.sp).join(Products).filter(OrderDetails.order_id == id)
        for i in ods:
            pass
        return render_template('make_order.html',id=id,p = p,pay=pay,ods=ods)
        
    else:
        results = []
        search_string = request.form.getlist('search')
        qty = request.form["qty"]
        
        for i in search_string:
            print(i)
            results = Products.query.filter(Products.name.contains(i)).all()
            if results:
                for res in results:
                    print("resultsssss", res)
                rows = OrderDetails(pid = res.id, quantity=qty, order_id = id ,current_bp = res.bp, current_sp = res.sp)
                db.session.add(rows)
                db.session.commit()
                
                url="/order/"+str(id)
                
                return  redirect(url)
            
            else:
                flash('No results found!')
                url="/order/"+str(id)
                return  redirect(url)


@app.route('/makepays' ,methods=['post','get'])
@login_required
def payss():
    
    amount = request.form["amount"]
        
    id = request.form["o_id"]
        
    payrec = Payments(amount =amount, order_id = id, created_at = datetime.now())
    db.session.add(payrec)
    db.session.commit()

    url="/order/"+str(id) 
          
    return  redirect(url)


@app.route('/makedelivery' ,methods=['post','get'])
@login_required
def make_delivery():
    
    name = request.form["name"]
    phone = request.form["phone"]
    address = request.form["address"]
    deli = request.form["deli"]
        
    id = request.form["o_id"]
        
    delis = Deliveries(customer_name = name, order_id = id,phone_no=phone,address=address, delivered_by=deli, date_delivered =datetime.now())
    db.session.add(delis)
    db.session.commit()

    url="/order/"+str(id) 
          
    return  redirect(url)


@app.route('/save_products',methods=['post','get'])
def save_products():

    name =request.form['name']
    bp = request.form['bp']
    sp = request.form['sp']
    
    user = current_user.id
    rows = Products(name=name,bp=bp,sp=sp,user_id=user)
    db.session.add(rows)
    db.session.commit()
    
    return redirect(url_for('inventory'))

@app.route('/add_stock',methods=['post','get'])
def add_stock():

    quantity = request.form['quantity']
    product_id = request.form['product_id']
    created_at ='NOW()'
    
    
    user = current_user.id
    rows = Stock(quantity = quantity,product_id=product_id,user_id=user,created_at=created_at)
    db.session.add(rows)  
    db.session.commit()
    
    
    return redirect(url_for('inventory',user_id=user))

@app.route('/edit_item',methods=['post','get'])
def edit_item():

    #query = """UPDATE products SET name = %s,bp=%s,sp=%s,serial_no=%s WHERE id=%s """  
    pid = request.form['pid']
    row = Products.query.filter_by(id = pid).one()
    row.name = request.form['pname']
    row.bp = request.form['pbp']
    row.sp = request.form['psp']
      
    db.session.merge(row)   
    db.session.commit()
    
    user = current_user.id

    return redirect(url_for('inventory',user_id=user))

@app.route('/delete_item',methods=['post','get'])
def delete_item():

    pid = request.form['product_id']
    row = Products.query.filter_by(id = pid).one()
     
    db.session.delete(row)
    db.session.commit()
    
   
    return redirect(url_for('inventory'))


@app.route('/delete_od',methods=['post','get'])
def delete_od():

    oid = request.form['od_id']
    row = OrderDetails.query.filter_by(id = oid).one()
     
    db.session.delete(row)
    db.session.commit()

    o_id = request.form["o_id"]
    url="/order/"+str(o_id) 
                
    return  redirect(url)


@app.route('/dashboard')
@role_required
@login_required
def dashboard():
    
    #query the database and obtain sales per month as python 
#   cur.execute("SELECT extract(month from s.created_at) AS monthly,sum(s.quantity * p.sp) AS sales FROM sales s JOIN products p ON p.id = s.product_id GROUP BY monthly ORDER BY monthly ;")
#   spm = cur.fetchall()
    spm = Orders.query.with_entities(func.sum(Payments.amount), extract('month',Orders.created_at)).join(Payments).group_by( extract('month',Orders.created_at)) 
    
    monthspm=[]
    dataspm=[]
    for x in spm :
        monthspm.append(x[1])
        dataspm.append(int(x[0]))
   
        
#   cur.execute(" SELECT sum(s.quantity * p.sp) AS sales, p.name FROM sales s JOIN products p ON p.id = s.product_id GROUP BY p.name ;")
    sbp = Products.query.with_entities(func.sum(OrderDetails.quantity), Products.name).join(OrderDetails).group_by(Products.name ).order_by(func.sum(OrderDetails.quantity))
    
    namesbp=[]
    salesbp=[]
    for x in sbp:
        namesbp.append(x[1])
        salesbp.append(float(x[0])) 
    

#   cur.execute("SELECT sum(s.quantity * p.sp) AS sales,DATE(created_at) AS today FROM sales s JOIN products p ON p.id = s.product_id WHERE DATE(created_at) = current_date GROUP BY today;")
    # ds =  Sales.query.with_entities(func.sum(Sales.quantity * Products.sp),func.date(Sales.created_at)).join(Products).filter(func.date(Sales.created_at) == date.today()).group_by(func.date(Sales.created_at)) 
    
    ds =  Orders.query.with_entities(func.date(Orders.created_at),func.sum(Payments.amount)).join(Payments).filter(func.date(Orders.created_at) == date.today()).group_by(func.date(Orders.created_at))
                
    dailys = 0
    today = []
    for i in ds:
        dailys=(float(i[1]))
        today=(i[0])
   
    
#   monthly sales
    ms = Orders.query.with_entities(func.sum(Payments.amount),extract('month',Orders.created_at)).join(Payments).filter(extract('month',Orders.created_at) == date.today().month).group_by(extract('month',Orders.created_at)) 
    monthsales = 0
    thismonth = []
    for i in ms:
        monthsales=(float(i[0]))
        thismonth=(i[1])
   


#   profit per month   
#   cur.execute("SELECT sum(p.sp - p.bp) AS profit,extract(month from s.created_at) AS monthly FROM sales s JOIN products p ON p.id = s.product_id GROUP BY monthly ORDER BY monthly ;")
    # prof = Sales.query.with_entities(func.sum(Products.sp - Products.bp)* Sales.quantity),extract('month',Sales.created_at)).join(Products).filter(extract('month',Sales.created_at) == date.today().month).group_by(extract('month',Sales.created_at))
    
    
# top5 product sales
#   cur.execute('SELECT p.name,sum(s.quantity) AS most_sold FROM sales s JOIN products p ON p.id = s.product_id GROUP BY p.name ORDER BY (sum(s.quantity)) DESC LIMIT 5;')
    prod=[]
    data5=[]
    top5 = Products.query.with_entities(Products.name, func.sum(OrderDetails.quantity)).join(OrderDetails ).group_by(Products.name ).order_by(func.sum(OrderDetails.quantity)).limit(5) 
    
    for i in top5:
        prod.append(i[0])
        data5.append(int(i[1]))
    
        
       
    return render_template('dashboard.html',prod=prod,data5=data5,dailys = dailys,today=today,monthspm=monthspm,dataspm=dataspm,namesbp=namesbp,salesbp= salesbp,monthsales=monthsales,thismonth=thismonth)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()



if __name__ == '__main__':
    app.run(debug=True, port=5002)
    