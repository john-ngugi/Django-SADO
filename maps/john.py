
dates = ['2020-04-02', '2020-04-18', '2020-05-03', '2020-05-19','2020-06-05','2020-05-19']  
datesAppend =[]

for date in dates:
    w = list(date)
    print(w)   
    datesAppend.append(w) 
print(datesAppend)
q = []

for r in range(len(datesAppend)):
    k=0
    for i in datesAppend[r]:
        if i == '-':   
            p = datesAppend[r].index(i)
            datesAppend[r].pop(p)
            k = k + 1
    print('this date ', datesAppend[r],' has a length of ', len(datesAppend[r]))

print('new dates',datesAppend)
        

for u in range(len(datesAppend)):
    l = ''.join(datesAppend[u])
    q.append(l)
 
print(q)   

intDates = []

print(type(intDates))

for e in range(len(q)):
    dates1 = int(q[e])
    intDates.append(dates1)
print('now they are ints ',intDates, type(intDates))    

f = set(intDates)
f =list(f)

dates = []
for d in range(len(f)):
    d = str(f[d])
    d = list(d)
    dates.append(d)
print(dates)   



h = 0

for date in dates: 
    dates[h].insert(4,"-")
    dates[h].insert(7,"-")
    h = h + 1

g = []

for u in range(len(dates)):
    l = ''.join(dates[u])
    g.append(l)

dates = g

print(g)


   




	    
