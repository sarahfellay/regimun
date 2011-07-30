from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.db.models.aggregates import Count
from django.http import Http404, HttpResponse
from django.middleware import csrf
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import slugify
from django.utils import simplejson
from regimun_app.forms import jEditableForm, BasicConferenceInfoForm, \
    NewCommitteeForm, NewCountryForm, FeeStructureForm, UploadFileForm, \
    NewPaymentForm
from regimun_app.models import Conference, Committee, Country, DelegatePosition, \
    School, CountryPreference, Payment
from regimun_app.views.secretariat_admin import secretariat_authenticate
import csv
import exceptions
import inspect
import settings
import string

@login_required
def conference_ajax_functions(request, conference_slug, func_name):
    conference = get_object_or_404(Conference, url_name=conference_slug)
    func_name = string.replace(func_name, "-", "_")
    
    if secretariat_authenticate(request, conference) and func_name in globals() and inspect.isfunction(globals()[func_name]):
        return_value = globals()[func_name](request, conference)
        if return_value != None:
            if isinstance(return_value, HttpResponse):
                return return_value
            else:
                return HttpResponse(return_value, mimetype='application/javascript')
                #return HttpResponse("<html><body>" + return_value + "</body></html>")
    
    raise Http404

def get_basic_conference_form(request, conference):
    form = BasicConferenceInfoForm(instance=conference)
    
    output = ""
    if conference.logo:
        output += "<img src=\"" + settings.MEDIA_URL + conference.logo.url + "\" border=\"0\" width=\"100\" />"
    output += "<form action=\"ajax/save-basic-conference-form\" enctype=\"multipart/form-data\" method=\"post\" id=\"basic_conference_info_form\">"
    output += "<input type='hidden' name='csrfmiddlewaretoken' value='" + csrf.get_token(request) + "' />"
    output += "<table>"
    output += form.as_table()
    output += "</table></form>"
    return simplejson.dumps({'form':output})

def save_basic_conference_form(request, conference):
    form = BasicConferenceInfoForm(request.POST, request.FILES, instance=conference)
    
    if form.is_valid():
        conference = form.save()
        return simplejson.dumps({'conference':conference.pk})
    else:
        return simplejson.dumps({'form':form.as_p()})

def get_fee_structure_form(request, conference):
    form = FeeStructureForm(instance=conference.feestructure)
    
    output = "<form action=\"ajax/save-fee-structure-form\" method=\"post\" id=\"fee_structure_info_form\"><table>"
    output += form.as_table()
    output += "</table></form>"
    return simplejson.dumps({'form':output})

def save_fee_structure_form(request, conference):
    form = FeeStructureForm(request.POST, instance=conference.feestructure)
    
    if form.is_valid():
        fee_structure = form.save()
        return simplejson.dumps({'fee_structure':fee_structure.pk})
    else:
        return simplejson.dumps({'form':form.as_p()})

def get_conference_committees(request, conference):
    existing_committees = serializers.serialize('json', Committee.objects.filter(conference=conference), fields=('name'))
    form = NewCommitteeForm()
    
    return simplejson.dumps({'form':form.as_p(), 'objects':existing_committees})

def get_conference_countries(request, conference):
    existing_countries = serializers.serialize('json', Country.objects.filter(conference=conference), fields=('name','country_code'))
    form = NewCountryForm()
    
    return simplejson.dumps({'form':form.as_p(), 'objects':existing_countries})

def get_conference_payments(request, conference):
    existing_payments = serializers.serialize('json', Payment.objects.select_related('school').filter(school__conference=conference), fields=('school','type','date','amount','notes'), use_natural_keys=True)
    form = NewPaymentForm()
    
    return simplejson.dumps({'form':form.as_p(), 'objects':existing_payments})

def edit_committee(request, conference):
    # clean the POST data
    if request.method == 'POST':
        form = jEditableForm(data=request.POST)
        if form.is_valid():
            # get the committee PK and attribute we want to set. The id is formatted "attr_pk"
            raw_id = request.POST.get('id', '')
            committee_attr, committee_pk = raw_id.rsplit("_")
            if committee_attr and committee_pk:
                committee = get_object_or_404(Committee, pk=committee_pk)
                value = form.cleaned_data['value']
                if committee.conference == conference and value:
                    committee.__setattr__(committee_attr, value)
                    committee.save()
                    return HttpResponse(value)

def remove_committee(request, conference):
    if request.method == 'POST':
        committee_pk = request.POST.get('pk', '')
        committee = get_object_or_404(Committee, pk=committee_pk)
        committee.delete()
        return simplejson.dumps({'pk':committee_pk})

def add_committee(request, conference):
    if request.method == 'POST':
        form = NewCommitteeForm(data=request.POST)
        if(form.is_valid()):
            committee = form.save(commit=False)
            committee.conference = conference
            committee.url_name = slugify(committee.name)
            committee.save()
            return simplejson.dumps({'pk':committee.pk, 'name':committee.name})
        else:
            return simplejson.dumps({'form':form.as_p()})
   
def edit_country(request, conference):
    # clean the POST data
    if request.method == 'POST':
        form = jEditableForm(data=request.POST)
        if form.is_valid():
            # get the country PK and attribute we want to set. The id is formatted "attr_pk"
            raw_id = request.POST.get('id', '')
            country_attr, country_pk = raw_id.rsplit("_")
            if country_attr and country_pk:
                country = get_object_or_404(Country, pk=country_pk)
                value = form.cleaned_data['value']
                if country.conference == conference and value:
                    country.__setattr__(country_attr, value)
                    country.save()
                    return HttpResponse(value)

def remove_country(request, conference):
    if request.method == 'POST':
        country_pk = request.POST.get('pk', '')
        country = get_object_or_404(Country, pk=country_pk)
        country.delete()
        return simplejson.dumps({'pk':country_pk})

def add_country(request, conference):
    if request.method == 'POST':
        form = NewCountryForm(request.POST, request.FILES)
        if(form.is_valid()):
            country = form.save(commit=False)
            country.conference = conference
            country.url_name = slugify(country.name)
            country.save()
            return serializers.serialize('json', [country], fields=('name','country_code'))[1:-1]
        else:
            return simplejson.dumps({'form':form.as_p()})

def edit_payment(request, conference):
    # clean the POST data
    if request.method == 'POST':
        form = jEditableForm(data=request.POST)
        if form.is_valid():
            # get the payment PK and attribute we want to set. The id is formatted "attr_pk"
            raw_id = request.POST.get('id', '')
            payment_attr, payment_pk = raw_id.rsplit("_")
            if payment_attr and payment_pk:
                payment = get_object_or_404(Payment, pk=payment_pk)
                value = form.cleaned_data['value']
                if payment.school.conference == conference and value:
                    payment.__setattr__(payment_attr, value)
                    payment.save()
                    return HttpResponse(value)

def remove_payment(request, conference):
    if request.method == 'POST':
        payment_pk = request.POST.get('pk', '')
        payment = get_object_or_404(Payment, pk=payment_pk)
        payment.delete()
        return simplejson.dumps({'pk':payment_pk})

def add_payment(request, conference):
    if request.method == 'POST':
        form = NewPaymentForm(request.POST, request.FILES)
        if(form.is_valid()):
            payment = form.save()
            return serializers.serialize('json', [payment], fields=('school','type','date','amount','notes'), use_natural_keys=True)[1:-1]
        else:
            return simplejson.dumps({'form':form.as_p()})

def get_delegate_positions_table(committees, countries):
    table_list = []
    
    table_list.append("<thead><tr><th>Country</th>")
    for committee in committees:
        table_list.append("<th>")
        table_list.append(committee.name)
        table_list.append("</th>")
    table_list.append("</tr></thead><tbody>")
    
    counts = DelegatePosition.objects.values('committee','country').annotate(count=Count('id'))
    
    count_dict = dict()
    for item in counts:
        count_dict[(item['country'],item['committee'])] = item['count']
    
    for country in countries:
        table_list.append("<tr><td>")
        table_list.append(country.name)
        table_list.append("</td>")
        for committee in committees:
            count = count_dict.get((country.pk, committee.pk), 0)
            
            table_list.append("<td class=\"position_count\" id=\"")
            table_list.append(str(committee.pk))
            table_list.append("_")
            table_list.append(str(country.pk))
            table_list.append("\">")
            table_list.append(str(count))
            table_list.append("</td>")
        table_list.append("</tr>")
    table_list.append("</tbody>")
    
    return ''.join(table_list)

def get_delegate_positions(request, conference):
    committees = Committee.objects.filter(conference=conference)
    countries = Country.objects.filter(conference=conference)
    return simplejson.dumps({'table':get_delegate_positions_table(committees, countries)})

def dictify_queryset(set, field):
    ret = dict()
    for obj in set:
        ret[getattr(obj, field)] = obj
    return ret

def sort_queryset(list, field):
    ret = dict()
    for obj in list:
        ret.setdefault(getattr(obj, field),[]).append(obj)
    return ret

def get_school_from_position_set(positions):
    school_dict = {}
    for pos in positions:
        if pos.school != None:
            school_dict[pos.school] = school_dict.get(pos.school, 0) + 1
    
    if school_dict:
        # get the most common school
        for key, value in sorted(school_dict.iteritems(), key=lambda (k,v): (v,k), reverse=True):
            return key
    else:
        return None 

def upload_delegate_positions(request, conference):
    errors = set()
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if(form.is_valid()):
            uploaded_file = request.FILES['file']
            committees = Committee.objects.filter(conference=conference)
            committees_dict = dictify_queryset(committees, 'name')
            countries = Country.objects.filter(conference=conference)
            countries_dict = dictify_queryset(countries, 'name')
            
            all_positions = DelegatePosition.objects.filter(country__in=countries, committee__in=committees)
            positions_dict = dict()
            for pos in all_positions:
                positions_dict.setdefault((pos.country,pos.committee),[]).append(pos)
                
            positions_by_country = sort_queryset(all_positions, 'country')
            
            try:
                positions_reader = csv.DictReader(uploaded_file)
                for row in positions_reader:
                    try:
                        country_name = row["Country"].strip()
                    except KeyError:
                        errors.add("Not a valid CSV file: No Country column.")
                        break
                    else:
                        try:
                            country = countries_dict[country_name]
                        except KeyError:
                            errors.add("Could not find country " + country_name + " (skipping)")
                        else:
                            for committee_name,value in row.items():
                                committee_name = committee_name.strip()
                                value = value.strip()
                                if value == "":
                                    value = "0"
                                if committee_name != "Country":
                                    try:
                                        committee = committees_dict[committee_name]
                                    except KeyError:
                                        errors.add("Could not find committee " + committee_name + " (skipping)") 
                                    else:
                                        try:
                                            new_count = int(value)
                                        except exceptions.ValueError:
                                            errors.add("Invalid value for " + country.name + "/" + committee.name + ": " + value + " (skipping)")
                                        else:
                                            set_delegate_position_count(committee, country, 
                                                                        positions_dict.get((country,committee),[]), 
                                                                        get_school_from_position_set(positions_by_country.get(country, [])), new_count)
            except csv.Error:
                errors.add("Not a valid CSV file.")
            if len(errors) > 0:
                return simplejson.dumps({'errors':list(errors),'table':get_delegate_positions_table(committees, countries)})
            return simplejson.dumps({'table':get_delegate_positions_table(committees, countries)})

def set_delegate_position_count(committee, country, current_positions, school, new_count):
    current_count = len(current_positions)
    if new_count > current_count:   # add new positions
        for i in range(current_count, new_count):
            new_position = DelegatePosition()
            new_position.committee = committee
            new_position.country = country
            new_position.school = school
            
            new_position.save()
    elif new_count < current_count: # remove positions
        for i in range(new_count, current_count):
            current_positions[i].delete()

def set_delegate_positions(request, conference):
    if request.method == 'POST':
        form = jEditableForm(data=request.POST)
        if form.is_valid():
            # get the committee and country PK
            raw_id = request.POST.get('id', '')
            committee_pk,country_pk = raw_id.rsplit("_")
            if country_pk and committee_pk:
                committee = get_object_or_404(Committee, pk=committee_pk)
                country = get_object_or_404(Country, pk=country_pk)
                value = form.cleaned_data['value']
                if committee.conference == conference and country.conference == conference and value:
                    if value == "":
                        value = "0"
                    new_count = int(value)
                    country_positions = []
                    current_positions = DelegatePosition.objects.filter(committee=committee,country=country)
                    if len(current_positions) < new_count:
                        country_positions = DelegatePosition.objects.filter(country=country)
                    set_delegate_position_count(committee, country, current_positions, get_school_from_position_set(country_positions), new_count)
                    return HttpResponse(value)

def get_country_school_assignment_table(countries):
    table_list = ["<thead><tr><th>Country</th><th>School</th></tr></thead><tbody>"]
    
    assignments = DelegatePosition.objects.filter(country__in=countries).values('school__name','country__name','country__pk')
    
    assignment_dict = dict()
    for item in assignments:
        if item['school__name'] != None:
            assignment_dict.setdefault((item['country__name'],item['country__pk']), set()).add(item['school__name'])
        else:
            assignment_dict.setdefault((item['country__name'],item['country__pk']), set())
    
    for country in countries:
        key = (country.name, country.pk)
        if assignment_dict.has_key(key):
            table_list.append("<tr><td>")
            table_list.append(country.name)
            table_list.append("</td>")
            table_list.append("<td class=\"school_assignment\" id=\"")
            table_list.append(str(country.pk))
            table_list.append("\">")
            table_list.append(','.join(assignment_dict[key]))
            table_list.append("</td></tr>")        
    table_list.append("</tbody>")
    
    return ''.join(table_list)

def get_country_school_assignments(request, conference):
    countries = Country.objects.filter(conference=conference)
    return simplejson.dumps({'table':get_country_school_assignment_table(countries)})

def set_country_school_assignment(country_positions, school):
    for position in country_positions:
        position.school = school
        position.save()

def set_country_school_assignments(request, conference):
    if request.method == 'POST':
        form = jEditableForm(data=request.POST)
        if form.is_valid():
            country_pk = request.POST.get('id', '')
            country = get_object_or_404(Country, pk=country_pk)
            if country.conference == conference:
                country_positions = DelegatePosition.objects.filter(country=country)
                school_pk = form.cleaned_data['value']
                if school_pk == "-1":
                    set_country_school_assignment(country_positions, None)
                    return HttpResponse(" ")
                else:
                    school = get_object_or_404(School, pk=school_pk)
                    if school.conference == conference:
                        set_country_school_assignment(country_positions, school)
                        return HttpResponse(school.name)

def upload_school_country_assignments(request, conference):
    errors = set()
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if(form.is_valid()):
            uploaded_file = request.FILES['file']
            countries = Country.objects.filter(conference=conference)
            countries_dict = dictify_queryset(countries, 'name')
            schools = School.objects.filter(conference=conference)
            schools_dict = dictify_queryset(schools, 'name')
            all_positions = DelegatePosition.objects.filter(country__in=countries)
            positions_dict = sort_queryset(all_positions, 'country')
            
            try:
                assignments_reader = csv.DictReader(uploaded_file)
                for row in assignments_reader:
                    try:
                        country_name = row["Country"].strip()
                    except KeyError:
                        errors.add("Not a valid CSV file: No Country column.")
                        break
                    else:
                        try:
                            country = countries_dict[country_name]
                        except KeyError:
                            errors.add("Could not find country " + country_name + " (skipping)")
                        else:
                            try:
                                school_name = row["School"].strip()
                            except KeyError:
                                errors.add("Not a valid CSV file: No School column.")
                                break
                            else:
                                school = None
                                try:
                                    if len(school_name) > 1:
                                        school = schools_dict[school_name]
                                    try:
                                        set_country_school_assignment(positions_dict[country], school)
                                    except KeyError:
                                        errors.add("No positions for " + country_name + " - cannot assign to " + school_name)
                                except KeyError:
                                    errors.add("Could not find school " + school_name + " for " + country_name + " (skipping)")
            except csv.Error:
                errors.add("Not a valid CSV file.")
            if len(errors) > 0:
                return simplejson.dumps({'errors':list(errors),'table':get_country_school_assignment_table(countries)})
            return simplejson.dumps({'table':get_country_school_assignment_table(countries)})