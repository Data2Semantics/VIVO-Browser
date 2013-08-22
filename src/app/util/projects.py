'''
Created on Jan 29, 2013

@author: hoekstra
'''
from SPARQLWrapper import SPARQLWrapper, JSON
from urllib2 import unquote
import requests
import json

class Projects(object):
    '''
    classdocs
    '''

    namespaces = """
        PREFIX vivo: <http://vivoweb.org/ontology/core#>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX commitv: <http://commit.data2semantics.org/ontology/>
    """        
        
        
    list_projects_query = namespaces + """
        SELECT DISTINCT ?p ?l ?pn WHERE {
            ?p a commitv:Project .
            ?p skos:prefLabel ?l .
            ?p skos:altLabel ?pn .
        } ORDER BY ASC(?pn) 
    """
    
    list_groups_query = namespaces + """
        SELECT DISTINCT ?g ?l WHERE {
            { ?g a foaf:Organization } 
              UNION
            { ?g a vivo:Project }
            ?g skos:prefLabel ?l .
            MINUS { ?g vivo:partOf ?og .}
        } ORDER BY ASC(?l) 
    """

    list_persons_query = namespaces + """
        SELECT DISTINCT ?p ?l ?rt ?rl ?wp ?wpl WHERE {
            { ?r vivo:roleRealizedIn <CONTEXTURI> . }
            UNION
            { ?r vivo:roleContributesTo <CONTEXTURI> . }
            UNION
            { ?r commitv:roleConstrainedTo <CONTEXTURI> . }
            OPTIONAL { 
                ?r commitv:roleConstrainedTo ?wp .
                ?wp skos:prefLabel ?wpl
            }
            ?p vivo:hasRole ?r .
            ?r a ?rt .
            ?rt rdfs:label ?rl .
            ?p a foaf:Person .
            ?p foaf:name ?l .
            FILTER (?rt != vivo:Role && ?rt != vivo:ResearcherRole)
        } ORDER BY ASC(?l) 
    """
    
    list_all_persons_query = namespaces + """
        SELECT DISTINCT ?p ?l WHERE {
            ?p a foaf:Person .
            ?p foaf:name ?l .
            ?p commitv:sortName ?ln .
        } ORDER BY ASC(?ln) 
    """
    
    person_details_query = namespaces + """
        SELECT DISTINCT ?l ?fn ?ln ?o ?ol ?rt ?rl ?email ?homepage WHERE {
              <CONTEXTURI> a foaf:Person .
              <CONTEXTURI> foaf:name ?l .
              OPTIONAL {<CONTEXTURI> foaf:firstName ?fn . }
              OPTIONAL {<CONTEXTURI> commitv:sortName ?ln . }
              <CONTEXTURI> vivo:hasRole ?r .
              OPTIONAL { <CONTEXTURI> vivo:primaryEmail ?email . }
              OPTIONAL { <CONTEXTURI> foaf:homePage ?homepage . }
              ?r a ?rt .
              ?rt rdfs:label ?rl .
              { 
                { ?r vivo:roleRealizedIn ?o . }
                UNION
                {?r vivo:roleConstrainedTo ?o .}
              }
              UNION
              { 
                ?r vivo:roleContributesTo ?o .       
              }
              ?o skos:prefLabel ?ol .
              FILTER(?rt != vivo:Role && ?rt != vivo:ResearcherRole)
        } ORDER BY ASC(?l) 
    """

    group_details_query = namespaces + """
        SELECT DISTINCT ?l ?p ?pl ?po ?pol WHERE {
          { <CONTEXTURI> a foaf:Organization } 
          UNION
          { <CONTEXTURI> a vivo:Project }
          <CONTEXTURI> skos:prefLabel ?l .
          OPTIONAL {
            <CONTEXTURI> vivo:hasPart ?p . 
            ?p skos:prefLabel ?pl .
          }    
          OPTIONAL {
            <CONTEXTURI> vivo:partOf ?po . 
            ?po skos:prefLabel ?pol .
          }
        } ORDER BY ASC(?l) 
    """

    def __init__(self, endpoint):
        '''
        Constructor
        '''
        
        self.sparql = SPARQLWrapper(endpoint)
        self.sparql.setReturnFormat(JSON)
        
    def listProjects(self):
        self.sparql.setQuery(self.list_projects_query)
        
        results = self.sparql.query().convert()
        
        projectList = []
        
        for result in results["results"]["bindings"]:
            project = {"uri": result["p"]["value"], "label": result["l"]["value"], "project": result["pn"]["value"] }
            projectList.append(project)
            
        return projectList
    
    def listGroups(self):
        self.sparql.setQuery(self.list_groups_query)
        
        results = self.sparql.query().convert()
        
        groupList = []
        
        for result in results["results"]["bindings"]:
            group = {"uri": result["g"]["value"], "label": result["l"]["value"] }
            print group
            groupList.append(group)
            
        return groupList
    
    
    def listPersons(self, projectURI):
        q = self.list_persons_query.replace("CONTEXTURI",projectURI)

        self.sparql.setQuery(q)
        
        results = self.sparql.query().convert()
        
        personsList = []
        
        for result in results["results"]["bindings"]:
            
            person = {"uri": result["p"]["value"], "label": result["l"]["value"], "role": result["rt"]["value"], "roleLabel": result["rl"]["value"]}
            
            if "wp" in result :
                person["wp"] = result["wp"]["value"]
                person["wpLabel"] = result["wpl"]["value"]
        
            
            personsList.append(person)
            
        return personsList      
    
    def listAllPersons(self):
        q = self.list_all_persons_query
        self.sparql.setQuery(q)
        
        results = self.sparql.query().convert()
        
        personsList = []
        
        for result in results["results"]["bindings"]:
            
            person = {"uri": result["p"]["value"], "label": result["l"]["value"]}
            
            personsList.append(person)
            
        return personsList     
        
    def personDetails(self, personURI):
        q = self.person_details_query.replace("CONTEXTURI",personURI)
        self.sparql.setQuery(q)
        
        results = self.sparql.query().convert()
        
        detailsList = []
        # ?l ?fn ?p ?o ?wp ?rt ?rl
        
        name = ""
        
        for result in results["results"]["bindings"]:
            detail = {"uri": personURI, "label": result["l"]["value"], "role": result["rt"]["value"], "roleLabel": result["rl"]["value"]}
            
            
                
            if "o" in result:
                detail["group"]= result["o"]["value"]
                detail["groupLabel"] = result["ol"]["value"]
            
            if "fn" in result :
                detail["firstname"] = result["fn"]["value"]
                first = result["fn"]["value"]
            if "ln" in result :
                detail["lastname"] = result["ln"]["value"]
                last = result["ln"]["value"]
            
            full = result['l']['value']

                
            if "homepage" in result:
                detail["homepage"] = result["homepage"]["value"]
                
            if "email" in result:
                detail["email"] = result["email"]["value"]
                
            detailsList.append(detail)
            
        if first and last :
            name = first + " " + last
        else :
            name = full
            
        print name
        image = self.getImage(name)
        details = {'image': image, 'details': detailsList }
            
        return details
    
    def groupDetails(self, groupURI):
        q = self.group_details_query.replace("CONTEXTURI",groupURI)
        self.sparql.setQuery(q)
        
        results = self.sparql.query().convert()
        
        detailsList = []
        
        parts = {}
        partOf = {}
        
        
        for result in results["results"]["bindings"]:
            detail = {"uri": groupURI, "label": result["l"]["value"]}
            
                
            if "p" in result:
                parts[result["p"]["value"]] = result["pl"]["value"]
                
            if "po" in result:
                partOf[result["po"]["value"]] = result["pol"]["value"]
            
            
            detailsList.append(detail)
            
        return detailsList, parts, partOf
          
    def getImage(self, q):
        APIKEY = "AIzaSyBTdZniWL-51geqo9kfGg1YxjtIfgVdkIs"
        param = {'q':q,
                 'key': APIKEY,
                 'alt': 'json',
                 'cx': '003884928642434432549:ayu4psypbr4',
                 'imgType': 'face',
                 'num': 1,
                 'searchType': 'image'}
        
        r = requests.get("https://www.googleapis.com/customsearch/v1", params=param)
        
        response = json.loads(r.text)
        
        return response['items'][0]['link']
        