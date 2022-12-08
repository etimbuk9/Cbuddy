from py2neo import Graph
from authen import extras, auth_functions
from medicalvisit.views import getStudNos

host_ip = '192.168.0.69'
# host_ip = '192.168.1.101'
# host_ip = '192.168.8.175'

try:
    graph = Graph(f'http://{host_ip}:7474/db/data', password = 'medical')
except:
    graph = []


loggedIn = False
user = 'etimbukabraham'
users = extras.getUserList()
role = 'DOCTOR'
students = getStudNos()

def get_and_set_login(request):
    chk = False
    user = ""
    ip = request.META['REMOTE_ADDR']
    # print(users)
    try:
        chk = users['logs'][users['ips']==ip]
        user = users['name'][users['ips'] == ip].iloc[0]
        chk = chk.iloc[0]
    except Exception as err:
        print(err)
        chk = False
    # print(chk, user)
    return chk

def exportUserInfo(request):
    user = ""
    ip = request.META['REMOTE_ADDR']
    # print(users)
    try:
        chk = users['logs'][users['ips']==ip]
        user = users['name'][users['ips'] == ip].iloc[0]
        user, role = auth_functions.getUserInfo(user)
        return user, role
    except Exception as err:
        print(err)
        chk = True
    # print(chk, user)
    return chk, chk


def getPreviousVisits(studentno):
    d2 = []
    query = 'MATCH(n:Person{id:' + studentno + '})-[:VISITED]->(m) ' + 'RETURN m.Complain,m.Diagnosis,m.Prescription,m.date,m.time, m.name order by m.name desc'
    d1 = graph.run(query).to_data_frame()
    if d1.shape[0] != 0:
        d1 = d1[['m.Complain', 'm.Diagnosis', 'm.Prescription', 'm.date', 'm.time', 'm.name']]
        d2 = [list(d1.iloc[x,:]) for x in range(d1.shape[0])]
    return d2

def getLabVisits(studentno):
    d2 = []
    query = 'MATCH(n:Person{id:' + studentno + '})-[*2]-(m:LabVisit) ' + 'RETURN m.Results,m.doctor,m.date,m.time, m.name'
    d = graph.run(query)
    d1 = d.to_data_frame()
    if d1.shape[0] != 0:
        d1 = d1[['m.date', 'm.Results', 'm.doctor', 'm.time', 'm.name']]
        d2 = [list(d1.iloc[x,:]) for x in range(d1.shape[0])]
    return d2

def getDrugs():
    if graph:
        query = "match(n:Drug) return n.name as info"
        data = graph.run(query).to_data_frame()
        studs = list(data['info'])
        return studs
    return []

def getDrugQtys():
    if graph:
        query = "match(n:Drug) return n.quantity as info"
        data = graph.run(query).to_data_frame()
        studs = list(data['info'])
        return studs
    return []