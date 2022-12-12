import global_vars

def check_user_status_power(request):
    output = {'power_user':False}
    dd = global_vars.graph.run('MATCH (a:User) WHERE a.name = "' + str(global_vars.exportUserInfo(request)[0]) + '" RETURN a.poweruser')
    d1 = dd.to_data_frame()
    if d1.shape[0] != 0:
        d1 = list(d1['a.poweruser'])
        d1 = d1[0]
        if d1:
            output = {'power_user':True}
    return output

def getStaff(request):
    if global_vars.graph:
        query = "match(n:Staff{is_active:true}) return n.name+' -> '+n.id as info order by n.id"
        data = global_vars.graph.run(query).to_data_frame()
        if data.shape[0] != 0:
            staff = list(data['info'])
            # print(staff)
            return {'staff_info': staff,}
    return []