from py2neo import Graph

host_ip = '192.168.0.69'
try:
    graph = Graph(f'http://{host_ip}:7474/db/data', password = 'medical')
except:
    graph = []