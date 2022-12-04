from py2neo import Graph
import global_vars


def getUserList():
    if global_vars.graph:
        query = 'match(n:User{active:true}) return n.name as name'
        data = global_vars.graph.run(query).to_data_frame()
        data['ips'] = ['0.0.0.0']*data.shape[0]
        data['logs'] = [False]*data.shape[0]
        data['inits'] = [{}]*data.shape[0]
        return data
    return []

def getAttributes(studentno):
    data_out = []
    query = 'match(n:Person{id:'+studentno+'})-[]-(a:Attribute) return a.name'
    data = global_vars.graph.run(query).to_data_frame()
    print(data)

    if data.shape[0] > 0:
        data_out = list(data['a.name'])
    return data_out

    