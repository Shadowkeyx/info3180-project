"""
Flask Documentation:     https://flask.palletsprojects.com/
Jinja2 Documentation:    https://jinja.palletsprojects.com/
Werkzeug Documentation:  https://werkzeug.palletsprojects.com/
This file creates your application.
"""
import os, random, datetime, psycopg2
from app import app, db
from flask import render_template, request, redirect, url_for, flash
from flask import session, abort, send_from_directory, jsonify, make_response
from werkzeug.utils import secure_filename
from app.forms import UploadForm 
from app.models import PropertyInfo 

conn = psycopg2.connect(app.config['SQLALCHEMY_DATABASE_URI'])

###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html', name="Bradley Henry")

@app.route('/properties/create', methods=['POST', 'GET']) 
def createproperty():
    userform = UploadForm()

    if request.method == 'POST' and userform.validate_on_submit():

        title = userform.title.data
        description = userform.description.data 
        num_bedrooms = userform.num_bedrooms.data 
        num_bathrooms = userform.num_bathrooms.data 
        price = userform.price.data
        type_ = userform.type_.data 
        location = userform.location.data 

        userfile = request.files['upload'] 
        filename = secure_filename(userfile.filename) 
        userfile.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)) 

        propid = genId(title, filename) 
        date_created = datetime.date.today() 

        createproperty = PropertyInfo(id = propid, title = title, description = description, num_bedrooms = num_bedrooms, num_bathrooms = num_bathrooms, price = price, type_ = type_, location = location, upload = filename, date_created = date_created) 

        db.session.add(createproperty)
        db.session.commit() 

        flash('Property Successfully Uploaded', 'success')
        return redirect(url_for('properties')) 

    flash_errors(userform)
    """Render the website's createproperty page."""
    return render_template('createproperty.html', form = userform) 

@app.route("/uploads/,filename>") 
def get_image(filename):
    rootdir = os.getcwd()
    return send_from_directory(rootdir + "/" + app.config['UPLOAD_FOLDER'], filename) 

def genId(title, filename):
    id = []
    for x in title:
        id.append(str(ord(x))) 
    for x in filename:
        id.append(str(ord(x))) 
    random.shuffle(id) 
    res= ''.join(id) 
    return int(res[:5]) 

@app.route('/properties/', methods=["GET", "POST"]) 
def properties(): 

    properties = PropertyInfo.query.all()

    if request.method == "GET":
        """Render the website's properties page."""
        return render_template('properties.html', properties = properties) 
    elif request.method == "POST":
        response = make_response(jsonify(properties)) 
        response.headers['Content-Type'] = 'application/json'
        return response 

@app.route('/property/<propid>', methods=["GET", "POST"]) 
def get_property(propid):

    prop = PropertyInfo.query.filter_by(id=propid).first()

    if request.method == "GET":
        return render_template("viewproperty.html", prop=prop)

    elif request.method == "POST":
        if prop is not None:
            response = make_response(jsonify(id = prop.propid, title = prop.title, num_bedrooms = prop.num_bedrooms, num_bathrooms = prop.num_bathrooms, location = prop.location, price = prop.price, type_ = prop.type_, description = prop.description, upload = prop.filename, date_created = prop.date_created)) 
            response.headers['Content-Type'] = 'application/json'
            return response
        else:
            flash('Property Not Found', 'danger')
            return redirect(url_for("home")) 


###
# The functions below should be applicable to all Flask apps.
###

# Display Flask WTF errors as Flash messages
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ), 'danger')

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also tell the browser not to cache the rendered page. If we wanted
    to we could change max-age to 600 seconds which would be 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0",port="8080")
