from py2neo import Graph
import global_vars



def getUserList():
    query = 'match(n:User{active:true}) return n.name as name'
    data = global_vars.graph.run(query).to_data_frame()
    data['ips'] = ['0.0.0.0']*data.shape[0]
    data['logs'] = [False]*data.shape[0]
    return data
    