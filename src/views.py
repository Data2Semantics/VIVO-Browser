"""
Module: views
Author:  hoekstra
Created: Jan 29, 2013


"""

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from urllib2 import unquote

from plugins.projects import Projects





p = Projects('http://localhost:8080/openrdf-sesame/repositories/commit')



def index(request):
    return projects(request)
    
def projects(request):
    projects = p.listProjects()
    return render_to_response('projects.html',{'projects': projects})

def groups(request):
    groups = p.listGroups()
    return render_to_response('groups.html',{'groups': groups})

def persons(request):
    persons = p.listAllPersons()
    return render_to_response('all_persons.html',{'persons': persons})

def person(request, URI):
    URI = unquote(URI)
    person = p.personDetails(URI)
    return render_to_response('person.html',{'person': person})

def group(request, URI):
    URI = unquote(URI)
    group, parts, partOf = p.groupDetails(URI)
    persons = p.listPersons(URI)
    return render_to_response('group.html',{'group': group, 'parts': parts, 'partOf': partOf, 'persons': persons})
    