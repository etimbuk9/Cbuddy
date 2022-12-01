import global_vars

def get_students_processor(request):
    if global_vars.graph:
        query = "match(n:Person)--(s:Set) return n.name+' -> '+n.id + ' ('+s.name+')' as info order by n.id"
        data = global_vars.graph.run(query).to_data_frame()
        if data.shape[0] != 0:
            studs = list(data['info'])
            return {'student_info': studs,}
    return []