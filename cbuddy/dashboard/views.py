from django.shortcuts import render, HttpResponse, redirect
import global_vars
from datetime import datetime as dt
from datetime import timedelta as td

# Create your views here.

def home(request, name, role):
    if global_vars.get_and_set_login(request):
        return render(request, 'dashboard/home.html', context={
                'appuser':name, 
                'role':role, 
                'visits':getVisitsintheLastWeek(7), 
                'today_visits':getVisitsintheLastWeek(-1),
                'students': getActiveStudents(),
                'active_users': global_vars.users.shape[0],
            })
    return redirect('authen:login')


def getVisitsintheLastWeek(dd):
    current_date = dt.now()
    from_date = current_date - td(days=dd)
    from_date = from_date.strftime('%Y-%m-%d')
    query = f'match(n:Visit) where n.date >= "{from_date}" return count(n)'
    data = global_vars.graph.run(query).to_data_frame()
    print(query, data)
    return data.iloc[0,0]

def getActiveStudents():
    query = 'match(n:Person{status:false}) return count(n)'
    data = global_vars.graph.run(query).to_data_frame()
    print(query, data)
    return data.iloc[0,0]
