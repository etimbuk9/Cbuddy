from global_vars import graph

def login(username, password):
    query = 'match(n:User{name:"'+username+'"}) return n.Password = "'+password+'"'
    data = graph.run(query).to_data_frame()
    return data.iloc[0,0]