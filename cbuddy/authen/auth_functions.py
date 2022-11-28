from global_vars import graph

def login(username, password):
    query = 'match(n:User{name:"'+username+'"}) return n.Password = "'+password+'" and n.active'
    data = graph.run(query).to_data_frame()
    return data.iloc[0,0]

def getUserInfo(username):
    query = 'match(n:User{name:"'+username+'"})--(r:Position) return n.name, r.name'
    data = graph.run(query).to_data_frame()
    info = [x for x in data.iloc[0,:]]
    return info