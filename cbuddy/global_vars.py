from py2neo import Graph
from authen import extras, auth_functions
from medicalvisit.views import getStudNos

host_ip = '192.168.0.160'

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
    print(users)
    try:
        chk = users['logs'][users['ips']==ip]
        user = users['name'][users['ips'] == ip].iloc[0]
        user, role = auth_functions.getUserInfo(user)
        return user, role
    except Exception as err:
        print(err)
        chk = False
    # print(chk, user)
    return chk, chk

def check_user_status_power(username):
    dd = graph.run('MATCH (a:User) WHERE a.name = "' + username + '" RETURN a.poweruser')
    d1 = dd.to_data_frame()
    d1 = list(d1['a.poweruser'])
    d1 = d1[0]
    return d1