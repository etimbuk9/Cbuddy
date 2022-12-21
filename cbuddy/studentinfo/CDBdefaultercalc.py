
import numpy as np
import pandas as pa
from datetime import timedelta as td
from datetime import datetime as dt


def trial(data):
    st1 = data['m.state']
    dtimes = data['m.times']
    ddays = data['m.days']
    hu1 = []
    for stater,day1,time1 in zip(st1,ddays,dtimes):
        st = stater
        hu = []
        #print(day1, time1)
        count = 0
        #for a, b in zip(time1,day1):
        if type(time1) is list:
            for c in range(len(time1)):
                A = time1[c] * day1[c]
                if c + 1 != len(time1):
                    h = st[count:count + A]
                else:
                    h = st[count:]
                h = np.array(h)
                # print(h1)
                if time1[c] * day1[c] > 1:
                    h = np.resize(h, [time1[c], day1[c]])
                else:
                    try:
                        h = np.vstack(h)
                    except:
                        h = np.vstack(np.zeros((time1[c], day1[c])))
                count += A
                hu.append(h)
        elif type(time1) is int:
            A = time1 * day1
            h = np.array(st)
            # print(h1)
            if time1 * day1 > 1:
                h = np.resize(h, [time1, day1])
            else:
                try:
                    h = np.vstack(h)
                except:
                    h = np.vstack(np.zeros((time1, day1)))
            hu.append(h)
        hu1.append(hu)
    return hu1


def screw(dd):
    B1 = []
    B2 = []
    for pack in dd:
        B = []
        #print(pack)
        for gig in pack:
            B.append(len(gig))
        #print(B)
        A = []
        for a in range(max(B)):
            A1 = []
            for gig in pack:
                try:
                    A1.append(not(gig[a]))
                except:
                    A1.append(False)
            A.append(not(any(A1)))
        B1.append(A)
        B2.append(max(B))
    return B1,B2

def detector(d1, edate):
    states = trial(d1)
    #print(states)
    count = 0
    comments = []
    g2 = []
    truth = []
    for state1 in states:
        days = []
        tot = []
        g1 = []
        for state in state1:
            dimS = state.shape
            #print(dimS)
            dd = np.array(range(dimS[1]))
            g = []
            for a in range(dimS[1]):
                g.append(not(np.any(state[:,a])))
            g1.append(g)
        g2.append(g1)
        #print(g2)
        dd1 = np.array(range(screw(g2)[1][count]))
        lastd = dd1[screw(g2)[0][count]]
        tot.append(lastd)

        try:
            days.append(min(lastd))
        except:
            days.append(screw(g2)[1][count])
        #print(days)
        tot = list(set([j for i in tot for j in i]))
        #print(d1['n.days'].iloc[count])
        #print(tot)
        if len(tot)>0:
            tot = np.array(tot)
            #print(tot)
        g = dt.strptime(d1['m.startdate'].iloc[count], '%Y-%m-%d')
        # enddays.append(g+td(days=max(d1['n.days'].iloc[count])))
        # print(g)
        # print(enddays)
        # edate = dt(2019,1,23)
        try:
            sdate = g+td(days=max(d1['m.days'].iloc[count]))
        except:
            sdate = g+td(days=d1['m.days'].iloc[count])
        
        
        
        if  sdate <= edate:
            truth.append(False)
            if len(tot)==0:
                comm = "Completed Treatment"
            else:
                #print('Patient missed drugs on days '+ str(list(tot)))
                try:
                    if len(tot)/max(d1['m.days'].iloc[count]) <= 0.4:
                        comm = 'Patient missed drugs for '+ str(len(tot))+ ' day(s) out of '+str(max(d1['m.days'].iloc[count]))+' days'
                    else:
                        comm = 'Patient missed drugs for '+ str(len(tot))+ ' day(s) out of '+str(max(d1['m.days'].iloc[count]))+' days. Please join us in our efforts to encourage your ward to promptly and religiously come for treatment.'
                except:
                    if len(tot)/d1['m.days'].iloc[count] <= 0.4:
                        comm = 'Patient missed drugs for '+ str(len(tot))+ ' day(s) out of '+str(d1['m.days'].iloc[count])+' days'
                    else:
                        comm = 'Patient missed drugs for '+ str(len(tot))+ ' day(s) out of '+str(d1['m.days'].iloc[count])+' days. Please join us in our efforts to encourage your ward to promptly and religiously come for treatment.'
        else:
            truth.append(True)
            dift = edate-g
            days = days[:dift.days]
            dif1 = sdate-edate
            # print(dift.days)
            # print(days)

            if len(tot[:dift.days])==0:
                comm = "Completed Treatment before vacation.\nHowever, Please endeavour to complete dosage for the next "+str(dif1.days)+' day(s) while at home'
            else:
                tot1 = np.array(tot)
                tot2 = tot1[tot1<=dift.days]
                dif1 = sdate-edate
                #print('Patient missed drugs on days '+ str(list(tot)))
                if len(tot2)/dift.days+1 <= 0.4:
                    comm = 'Patient missed drugs for '+ str(len(tot2))+ ' day(s) out of '+str(dift.days+1)+' days before vacation.\nPlease endeavour to complete dosage for the next '+str(dif1.days)+' day(s) while at home'
                else:
                    comm = 'Patient missed drugs for '+ str(len(tot2))+ ' day(s) out of '+str(dift.days+1)+' days before vacation. Please join us in our efforts to encourage your ward to promptly and religiously come for treatment.\nPlease endeavour to complete dosage for the remaining '+str(dif1.days)+' day(s) while at home'
        count+=1

        # if days == d1['m.days'].iloc[count]:
        #     comm = "Completed Treatment"
        # else:
        #     #print('Patient missed drugs on days '+ str(list(tot)))
        #     comm = 'Patient missed drugs for '+ str(len(tot))+ ' day(s) out of '+str(max(d1['m.days'].iloc[count]))+' days'
        # count+=1
        comments.append(comm)
    print(comments)
    return comments, truth


#detector(d1)
