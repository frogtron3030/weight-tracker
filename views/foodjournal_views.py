from flask import Blueprint, request, redirect, render_template, url_for
from flask.views import MethodView
from flask.ext.mongoengine.wtf import model_form
from weighttracker.models.foodjournal import Foodjournal
import parsedatetime
from datetime import datetime
from time import mktime

foodjournals = Blueprint('foodjournals', __name__, template_folder='templates')


class ListFoodjournals(MethodView):

  def get(self, page=1):
    foodjournals = Foodjournal.objects.order_by('-eating_time_parsed').paginate(page, per_page=10)
    return render_template('foodjournals/list.html', foodjournals=foodjournals)


class ShowFoodjournal(MethodView):

  def get(self, id):
    foodjournal = Foodjournal.objects.get_or_404(id=id )
    return render_template('foodjournals/show.html', foodjournal=foodjournal)


class EditFoodjournal(MethodView):

  def get(self, id):
    foodjournal = Foodjournal.objects.get_or_404(id=id )
    header_text = "Edit This Food Journal Entry"
    return render_template('foodjournals/edit.html', foodjournal=foodjournal, header_text=header_text)


class NewFoodjournal(MethodView):

  def get_context(self, id=None):
    form_cls = model_form(Foodjournal, exclude=('created_at', 'updated_at'))

    if id:
      foodjournal = Foodjournal.objects.get_or_404(id=id)
      header_text = "Edit This Food Journal Entry"
      if request.method == 'POST':
        form = form_cls(request.form, inital=foodjournal._data)
      else:
        form = form_cls(obj=foodjournal)
    else:
      foodjournal = Foodjournal()
      header_text = "Add a New Food Journal Entry"
      form = form_cls(request.form)

    context = {
            "foodjournal": foodjournal,
            "form": form,
            "header_text": header_text,
            "create": id is None
    }

    return context


  def get(self, id=None):
    context = self.get_context(id)
    return render_template('foodjournals/new.html', **context)

  def post(self, id=None):
    context = self.get_context(id)
    form = context.get('form')

    if form.validate():
      foodjournal = context.get('foodjournal')
      form.populate_obj(foodjournal)

      # Add the eating_time_parsed value, or update it
      cal = parsedatetime.Calendar()
      time_struct, parse_status = cal.parse(foodjournal['eating_time'])
      foodjournal['eating_time_parsed'] = datetime.fromtimestamp(mktime(time_struct))
      foodjournal['updated_at'] = datetime.now()

      # Save the record
      foodjournal.save()

      return redirect(url_for('foodjournals.list'))
    return render_template('foodjournals/new.html', **context)



# Register the urls
foodjournals.add_url_rule('/foodjournals/', view_func=ListFoodjournals.as_view('list'))
foodjournals.add_url_rule('/foodjournals/<int:page>/', view_func=ListFoodjournals.as_view('listpage'))
foodjournals.add_url_rule('/foodjournals/new/', view_func=NewFoodjournal.as_view('new'))
foodjournals.add_url_rule('/foodjournals/create/', defaults={'eating_time': None}, view_func=NewFoodjournal.as_view('create'))
foodjournals.add_url_rule('/foodjournals/<id>/', view_func=ShowFoodjournal.as_view('show'))
foodjournals.add_url_rule('/foodjournals/edit/<id>/', view_func=NewFoodjournal.as_view('edit'))