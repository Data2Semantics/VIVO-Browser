'''
Created on Jan 29, 2013

@author: hoekstra
'''
from SPARQLWrapper import SPARQLWrapper, JSON
from urllib2 import unquote
import requests
import json

# Taken from http://stackoverflow.com/a/1144405/2195799
def multikeysort(items, columns):
    from operator import itemgetter
    comparers = [ ((itemgetter(col[1:].strip()), -1) if col.startswith('-') else (itemgetter(col.strip()), 1)) for col in columns]  
    def comparer(left, right):
        for fn, mult in comparers:
            result = cmp(fn(left), fn(right))
            if result:
                return mult * result
        else:
            return 0
    return sorted(items, cmp=comparer)



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
        
        
    #list_projects_query = namespaces + """
    #    SELECT DISTINCT ?p ?l ?pn WHERE {
    #        ?p a commitv:Project .
    #        ?p rdfs:label ?l .
    #        ?p skos:altLabel ?pn .
    #    } ORDER BY ASC(?pn) 
    #"""
    #
    #list_groups_query = namespaces + """
    #    SELECT DISTINCT ?g ?l WHERE {
    #        { ?g a foaf:Organization } 
    #          UNION
    #        { ?g a vivo:Project }
    #        ?g rdfs:label ?l .
    #        MINUS { ?g vivo:partOf ?og .}
    #    } ORDER BY ASC(?l) 
    #"""
    #
    #list_persons_query = namespaces + """
    #    SELECT DISTINCT ?p ?l ?rt ?rl ?wp ?wpl WHERE {
    #        { ?r vivo:roleRealizedIn <CONTEXTURI> . }
    #        UNION
    #        { ?r vivo:roleContributesTo <CONTEXTURI> . }
    #        UNION
    #        { ?r commitv:roleConstrainedTo <CONTEXTURI> . }
    #        OPTIONAL { 
    #            ?r commitv:roleConstrainedTo ?wp .
    #            ?wp rdfs:label ?wpl
    #        }
    #        ?p vivo:hasRole ?r .
    #        ?r a ?rt .
    #        ?rt rdfs:label ?rl .
    #        ?p a foaf:Person .
    #        ?p foaf:name ?l .
    #        FILTER (?rt != vivo:Role && ?rt != vivo:ResearcherRole)
    #    } ORDER BY ASC(?l) 
    #"""
    #
    #list_all_persons_query = namespaces + """
    #    SELECT DISTINCT ?p ?l WHERE {
    #        ?p a foaf:Person .
    #        ?p foaf:name ?l .
    #        ?p commitv:sortName ?ln .
    #    } ORDER BY ASC(?ln) 
    #"""
    #
    #person_details_query = namespaces + """
    #    SELECT DISTINCT ?l ?fn ?ln ?o ?ol ?rt ?rl ?email ?homepage WHERE {
    #          <CONTEXTURI> a foaf:Person .
    #          <CONTEXTURI> foaf:name ?l .
    #          OPTIONAL {<CONTEXTURI> foaf:firstName ?fn . }
    #          OPTIONAL {<CONTEXTURI> commitv:sortName ?ln . }
    #          <CONTEXTURI> vivo:hasRole ?r .
    #          OPTIONAL { <CONTEXTURI> vivo:primaryEmail ?email . }
    #          OPTIONAL { <CONTEXTURI> foaf:homePage ?homepage . }
    #          ?r a ?rt .
    #          ?rt rdfs:label ?rl .
    #          { 
    #            { ?r vivo:roleRealizedIn ?o . }
    #            UNION
    #            {?r vivo:roleConstrainedTo ?o .}
    #          }
    #          UNION
    #          { 
    #            ?r vivo:roleContributesTo ?o .       
    #          }
    #          ?o rdfs:label ?ol .
    #          FILTER(?rt != vivo:Role && ?rt != vivo:ResearcherRole)
    #    } ORDER BY ASC(?l) 
    #"""
    #
    #group_details_query = namespaces + """
    #    SELECT DISTINCT ?l ?p ?pl ?po ?pol WHERE {
    #      { <CONTEXTURI> a foaf:Organization } 
    #      UNION
    #      { <CONTEXTURI> a vivo:Project }
    #      <CONTEXTURI> rdfs:label ?l .
    #      OPTIONAL {
    #        <CONTEXTURI> vivo:hasPart ?p . 
    #        ?p rdfs:label ?pl .
    #      }    
    #      OPTIONAL {
    #        <CONTEXTURI> vivo:partOf ?po . 
    #        ?po rdfs:label ?pol .
    #      }
    #    } ORDER BY ASC(?l) 
    #"""

    list_projects_query = namespaces + """
        SELECT DISTINCT ?p ?l WHERE {
            ?p a vivo:Project .
            ?p rdfs:label ?l .
        } ORDER BY ASC(?pn) 
    """
    
    list_groups_query = namespaces + """
        SELECT DISTINCT ?g ?l WHERE {
            ?g a foaf:Organization .
            ?g rdfs:label ?l .
            ?pos vivo:positionInOrganization ?g . 
            MINUS { { ?g vivo:partOf ?og . } UNION { ?g vivo:subOrganizationWithin ?og } }
            MINUS { ?g a vivo:Project .}
        } ORDER BY ASC(?l) 
    """

    list_persons_query = namespaces + """
        SELECT DISTINCT ?p ?l ?rt ?rl ?wp ?wpl WHERE {
            { ?r vivo:roleRealizedIn <CONTEXTURI> . }
            UNION
            { ?r vivo:roleContributesTo <CONTEXTURI> . }
            UNION
            { ?r vivo:positionInOrganization <CONTEXTURI> . }
            UNION
            { ?r commitv:roleConstrainedTo <CONTEXTURI> . }
            OPTIONAL { 
                ?r commitv:roleConstrainedTo ?wp .
                ?wp rdfs:label ?wpl
            }
            
            { ?p vivo:hasRole ?r . }
            UNION
            { ?p vivo:personInPosition ?r .}
            ?r a ?rt .
            ?rt rdfs:label ?rl .
            ?p a foaf:Person .
            ?p rdfs:label ?l .
            FILTER (?rt != vivo:Role )
        } ORDER BY ASC(?l) 
    """
    
    list_all_persons_query = namespaces + """
        SELECT DISTINCT ?p ?l WHERE {
            ?p a foaf:Person .
            ?p rdfs:label ?l .
            { ?p foaf:lastName ?ln } UNION { ?p commitv:sortName ?ln }.
        } ORDER BY ASC(?ln) 
    """
    
    person_bio_query = namespaces + """
        SELECT DISTINCT ?l ?fn ?ln ?email ?homepage WHERE {
              <CONTEXTURI> a foaf:Person .
              <CONTEXTURI> rdfs:label ?l .
              OPTIONAL {<CONTEXTURI> foaf:firstName ?fn . }
              OPTIONAL {<CONTEXTURI> foaf:lastName?ln . }
              OPTIONAL { { <CONTEXTURI> vivo:primaryEmail ?email . } UNION { <CONTEXTURI> vivo:email ?email . } }
              OPTIONAL {<CONTEXTURI> foaf:homePage ?homepage . }
        } ORDER BY ASC(?l) 
    """
    
    person_organizations_query = namespaces + """
        SELECT DISTINCT ?o ?ol ?rt ?rl WHERE {
              <CONTEXTURI> vivo:personInPosition ?r .
              ?r a ?rt .
              ?rt rdfs:label ?rl .
              ?r vivo:positionInOrganization ?o .
              ?o rdfs:label ?ol .
        } ORDER BY ASC(?l) 
    """
    person_roles_query = namespaces + """
        SELECT DISTINCT ?o ?ol ?rt ?rl WHERE {
              <CONTEXTURI> vivo:hasRole ?r .
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
              ?o rdfs:label ?ol .
              FILTER(?rt != vivo:Role)
        } ORDER BY ASC(?l) 
    """
    
    
    
    

    group_details_query = namespaces + """
        SELECT DISTINCT ?l ?p ?pl ?po ?pol ?g1 ?g2 WHERE {
          { <CONTEXTURI> a foaf:Organization } 
          UNION
          { <CONTEXTURI> a vivo:Project }
          <CONTEXTURI> rdfs:label ?l .
          OPTIONAL {
            GRAPH ?g1 {
                ?p vivo:subOrganizationWithin <CONTEXTURI> . 
                ?p rdfs:label ?pl .
            }
          }    
          OPTIONAL {
            GRAPH ?g2 {
                <CONTEXTURI> vivo:subOrganizationWithin ?po . 
                ?po rdfs:label ?pol .
            }
          }
          
          
        } ORDER BY ASC(?l) 
    """

    def __init__(self, endpoint, image_url_mask=None):
        '''
        Constructor
        '''
        
        self.sparql = SPARQLWrapper(endpoint)
        self.sparql.setReturnFormat(JSON)
        
        self.image_url_mask = image_url_mask
        
    def listProjects(self):
        self.sparql.setQuery(self.list_projects_query)
        
        results = self.sparql.query().convert()
        
        projects = {}
        
        for result in results["results"]["bindings"]:
            projects.setdefault(result['p']['value'],{})['label'] = result["l"]["value"] 
            
        return projects
    
    def listGroups(self):
        self.sparql.setQuery(self.list_groups_query)
        
        print self.list_groups_query
        
        
        results = self.sparql.query().convert()
        
        groups = {}
        
        for result in results["results"]["bindings"]:
            
            groups.setdefault(result["g"]["value"],{})['label'] = result["l"]["value"] 
            
        return groups
    
    
    def listPersons(self, projectURI):
        q = self.list_persons_query.replace("CONTEXTURI",projectURI)
        print q
        self.sparql.setQuery(q)
        
        results = self.sparql.query().convert()
        
        persons = {}
        
        for result in results["results"]["bindings"]:
            
            uri = result["p"]["value"]
            
            if 'rl' in result :
                role_label = result["rl"]["value"]
            else :
                (ignore, role_label) = result['rt']['value'].split('#')
            
            person = {"uri": result["p"]["value"], "label": result["l"]["value"], "role": result["rt"]["value"], "roleLabel": role_label}
            
            if "wp" in result :
                person["wp"] = result["wp"]["value"]
                person["wpLabel"] = result["wpl"]["value"]
        
            
            persons.setdefault(role_label,[]).append(person)
        
        print persons
        
        return persons      
    
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
        
        ## BIO
        q = self.person_bio_query.replace("CONTEXTURI",personURI)
        self.sparql.setQuery(q)
        
        results = self.sparql.query().convert()
        result = results['results']['bindings'][0]
        
        bio = { 'uri': personURI }
        
        if "fn" in result :
            bio["firstname"] = result["fn"]["value"]
            first = result["fn"]["value"]
        if "ln" in result :
            bio["lastname"] = result["ln"]["value"]
            last = result["ln"]["value"]
  
        name = ""
        first = None
        last = None     
        full = result['l']['value']

        if first and last :
            name = first + " " + last
        else :
            name = full
        
        bio['name'] = name
            
        if "homepage" in result:
            bio["homepage"] = result["homepage"]["value"]
            
        if "email" in result:
            bio["email"] = result["email"]["value"]
            
        bio['image'] = self.getImage(name)
          
          
        ## ORGANIZATIONS
        
        q = self.person_organizations_query.replace("CONTEXTURI",personURI)
        self.sparql.setQuery(q)
        
        results = self.sparql.query().convert()
        
        organizations = {}
        for result in results['results']['bindings']:
            organization_uri = result['o']['value']
            organization_label = result['ol']['value']
            role_label = result['rl']['value']
            
            organizations.setdefault(organization_uri,{})['label'] = organization_label
            organizations[organization_uri].setdefault('roles',set()).add(role_label)
        
        
        ## GROUPS/ROLES
        
        q = self.person_roles_query.replace("CONTEXTURI",personURI)
        self.sparql.setQuery(q)
        
        results = self.sparql.query().convert()
            
        groups = {}
        for result in results['results']['bindings']:
            group_uri = result['o']['value']
            group_label = result['ol']['value']
            role_label = result['rl']['value']
            
            groups.setdefault(group_uri,{})['label'] = group_label
            groups[group_uri].setdefault('roles',set()).add(role_label)        
        
        details = {'bio' : bio, 'organizations' : organizations, 'groups': groups}    
        
        
        import pprint  
        pprint.pprint(details)
        
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
                 'num': 10,
                 'searchType': 'image'}
        
        print param
        r = requests.get("https://www.googleapis.com/customsearch/v1", params=param)
        
        
        
        response = json.loads(r.text)
        image_url = "none"
        if not 'error' in response : 
            if self.image_url_mask :
                
                for i in response['items']:
                    print i['link']
                    if self.image_url_mask in i['link'] :
                        print "Success!"
                        image_url = i['link']
                        break
            else :
                image_url = response['items'][0]['link']

        return image_url
        