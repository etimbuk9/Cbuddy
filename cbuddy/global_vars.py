from py2neo import Graph
from authen import extras

host_ip = '192.168.0.160'
try:
    graph = Graph(f'http://{host_ip}:7474/db/data', password = 'medical')
except:
    graph = []


loggedIn = False
user = 'etimbukabraham'
users = extras.getUserList()
role = 'DOCTOR'

def get_and_set_login(request):
    chk = False
    user = ""
    ip = request.META['REMOTE_ADDR']
    print(users)
    try:
        chk = users['logs'][users['ips']==ip]
        user = users['name'][users['ips'] == ip].iloc[0]
        chk = chk.iloc[0]
    except Exception as err:
        print(err)
        chk = False
    print(chk, user)
    return chk