from flask import render_template, g, request, jsonify
from urllib2 import unquote
from util.projects import Projects
from app import app


#p = Projects('http://localhost:8080/openrdf-sesame/repositories/commit')
p = Projects('http://localhost:8080/openrdf-sesame/repositories/narcisvivo',image_url_mask = 'vu.nl')
#p = Projects('http://lod.cedar-project.nl:8888/openrdf-sesame/repositories/vua')

@app.route('/')
def index():
    # return projects(request)
    return groups()

@app.route('/projects')    
def projects():
    projects = p.listProjects()
    return render_template('projects.html',projects = projects)

@app.route('/groups') 
def groups():
    groups = p.listGroups()
    return render_template('groups.html',groups=groups)

@app.route('/persons') 
def persons():
    persons = p.listAllPersons()
    return render_template('all_persons.html',persons = persons)

@app.route('/person/<path:URI>') 
def person(URI):
    URI = unquote(URI)
    details = p.personDetails(URI)
    return render_template('person.html',details = details)

@app.route('/group/<path:URI>') 
def group(URI):
    URI = unquote(URI)
    group, parts, partOf = p.groupDetails(URI)
    persons = p.listPersons(URI)
    return render_template('group.html', group = group, parts = parts, partOf = partOf, persons = persons)
    