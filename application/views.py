"""
views.py

URL route handlers

Note that any handler params must match the URL route params.
For example the *say_hello* handler, handling the URL route '/hello/<username>',
  must be passed *username* as the argument.

"""
from google.appengine.api import users
from google.appengine.api import mail
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from flask import request, render_template, flash, url_for, redirect, session

from flask_cache import Cache
from flask_babel import refresh
import flask_login

from application import app
from decorators import login_required, admin_required
from forms import RegisterForm, JobForm, ContactForm


# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/setlocale/<locale>')
def setlocale(locale):
    session['locale'] = locale
    refresh()
    return redirect(request.referrer)

#about
@app.route('/about/access')
def access():
    return render_template('about/access.html')

@app.route('/about/balance')
def balance():
    return render_template('about/balance.html')

@app.route('/about/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm(request.form)
    if request.method == 'POST' and form.validate():
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        comment = form.message.data

        sender='Admin of AFCP <lutianming1005@gmail.com>'
        to="lutianming1005@hotmail.com"
        subject = 'Message from {0} {1}<{2}>'.format(first_name, last_name, email)
        body = u"""
    Following is the message from {0} {1} {2}:

    {3}
    """.format(first_name, last_name, email, comment)

        mail.send_mail(sender, to, subject, body)

        flash('mail sent')
    return render_template('about/contact.html', form=form)

@app.route('/about')
def about():
    return redirect(url_for('access'))

@cache.cached(timeout=60)
def cached_examples():
    """This view should be cached for 60 sec"""
    examples = ExampleModel.query()
    return render_template('list_examples_cached.html', examples=examples)


def warmup():
    """App Engine warmup handler
    See http://code.google.com/appengine/docs/python/config/appconfig.html#Warming_Requests

    """
    return ''
