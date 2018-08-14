import firebase
import firebase_admin
import numbers
from firebase_admin import db
import csv

database_node_source = 'Unscaled_Results_1'
database_node_destination = 'sandbox_islams'

results = db.reference().child(database_node_source).get()
ISBN = results.keys()
print ISBN

c_hist = [None] * 401
d_hist = [None] * 401
p_hist = [None] * 401
t_hist = [None] * 401
s_hist = [None] * 401

na_count = 0
value_count = 0

for i in range(len(c_hist)):
    c_hist[i] = 0.
    d_hist[i] = 0.
    p_hist[i] = 0.
    t_hist[i] = 0.
    s_hist[i] = 0.

print("###Create Hists###")

for isbn in range(len(ISBN)):
    c_score = db.reference().child(database_node_source).child(ISBN[isbn]).child('Character_Depth').get()
    #print c_score
    d_score = db.reference().child(database_node_source).child(ISBN[isbn]).child('Dialogue').get()
    #print d_score
    p_score = db.reference().child(database_node_source).child(ISBN[isbn]).child('Plot').get()
    #print p_score
    t_score = db.reference().child(database_node_source).child(ISBN[isbn]).child('Theme').get()
    #print t_score
    s_score = db.reference().child(database_node_source).child(ISBN[isbn]).child('Writing_Style').get()
    #print s_score

    if isinstance(c_score,numbers.Number):
        c_hist[int((c_score-1.)*100.)] += 1.
    else:
        na_count += 1
    if isinstance(d_score,numbers.Number):
        d_hist[int((d_score-1.)*100.)] += 1.
    else:
        na_count += 1
    if isinstance(p_score,numbers.Number):
        p_hist[int((p_score-1.)*100.)] += 1.
    else:
        na_count += 1
    if isinstance(t_score,numbers.Number):
        t_hist[int((t_score-1.)*100.)] += 1.
    else:
        na_count += 1
    if isinstance(s_score,numbers.Number):
        s_hist[int((s_score-1.)*100.)] += 1.
    else:
        na_count += 1

with open("histograms.csv", "wb") as f:
    writer = csv.writer(f)
    writer.writerows([c_hist,d_hist,p_hist,t_hist,s_hist])

print("###Create PDFs###")

c_sum = sum(c_hist)
if not c_sum == 0:
    for i in range(len(c_hist)):
        c_hist[i] /= c_sum

d_sum = sum(d_hist)
if not d_sum == 0:
    for i in range(len(d_hist)):
        d_hist[i] /= d_sum

p_sum = sum(p_hist)
if not p_sum == 0:
    for i in range(len(p_hist)):
        p_hist[i] /= p_sum

t_sum = sum(t_hist)
if not t_sum == 0:
    for i in range(len(t_hist)):
        t_hist[i] /= t_sum

s_sum = sum(s_hist)
if not s_sum == 0:
    for i in range(len(s_hist)):
        s_hist[i] /= s_sum

value_count = s_sum + t_sum + p_sum + d_sum + c_sum

print "########################"
print "### \"NA\" ratio: " + str(na_count/(value_count+na_count)) + " ###"
print "########################"

with open("PDFs.csv", "wb") as f:
    writer = csv.writer(f)
    writer.writerows([c_hist,d_hist,p_hist,t_hist,s_hist])

print("###Create CDFs###")

if not c_sum == 0:
    for i in range(len(c_hist)-1):
        c_hist[i+1] += c_hist[i]

if not d_sum == 0:
    for i in range(len(d_hist)-1):
        d_hist[i+1] += d_hist[i]

if not p_sum == 0:
    for i in range(len(p_hist)-1):
        p_hist[i+1] += p_hist[i]

if not t_sum == 0:
    for i in range(len(t_hist)-1):
        t_hist[i+1] += t_hist[i]

if not s_sum == 0:
    for i in range(len(s_hist)-1):
        s_hist[i+1] += s_hist[i]

with open("CDFs.csv", "wb") as f:
    writer = csv.writer(f)
    writer.writerows([c_hist,d_hist,p_hist,t_hist,s_hist])

print("###Pushing to Database Node: " + database_node_destination + " ###")

for isbn in range(len(ISBN)):
    c_ind = db.reference().child(database_node_source).child(ISBN[isbn]).child('Character_Depth').get()
    if not c_sum == 0 and isinstance(c_ind,numbers.Number):
        c_result = c_hist[int((c_ind-1)*100.)]*4.+1.
        db.reference().child(database_node_destination).child(ISBN[isbn]).update({'Character_Depth':round(c_result,2)})
    d_ind = db.reference().child(database_node_source).child(ISBN[isbn]).child('Dialogue').get()
    if not d_sum == 0 and isinstance(d_ind,numbers.Number):
        d_result = d_hist[int((d_ind-1)*100.)]*4.+1.
        db.reference().child(database_node_destination).child(ISBN[isbn]).update({'Dialogue':round(d_result,2)})
    p_ind = db.reference().child(database_node_source).child(ISBN[isbn]).child('Plot').get()
    if not p_sum == 0 and isinstance(p_ind,numbers.Number):
        p_result = p_hist[int((p_ind-1)*100.)]*4.+1.
        db.reference().child(database_node_destination).child(ISBN[isbn]).update({'Plot':round(p_result,2)})
    t_ind = db.reference().child(database_node_source).child(ISBN[isbn]).child('Theme').get()
    if not t_sum == 0 and isinstance(t_ind,numbers.Number):
        t_result = t_hist[int((t_ind-1)*100.)]*4.+1.
        db.reference().child(database_node_destination).child(ISBN[isbn]).update({'Theme':round(t_result,2)})
    s_ind = db.reference().child(database_node_source).child(ISBN[isbn]).child('Writing_Style').get()
    if not s_sum == 0 and isinstance(s_ind,numbers.Number):
        s_result = s_hist[int((s_ind-1)*100.)]*4.+1.
        db.reference().child(database_node_destination).child(ISBN[isbn]).update({'Writing_Style':round(s_result,2)})

print("###Create Equalized Hists###")

results = db.reference().child(database_node_destination).get()
ISBN = results.keys()

for isbn in range(len(ISBN)):
    c_score = db.reference().child(database_node_destination).child(ISBN[isbn]).child('Character_Depth').get()
    #print c_score
    d_score = db.reference().child(database_node_destination).child(ISBN[isbn]).child('Dialogue').get()
    #print d_score
    p_score = db.reference().child(database_node_destination).child(ISBN[isbn]).child('Plot').get()
    #print p_score
    t_score = db.reference().child(database_node_destination).child(ISBN[isbn]).child('Theme').get()
    #print t_score
    s_score = db.reference().child(database_node_destination).child(ISBN[isbn]).child('Writing_Style').get()
    #print s_score
    
    if isinstance(c_score,numbers.Number):
        c_hist[int((c_score-1.)*100.)] += 1.
    if isinstance(d_score,numbers.Number):
        d_hist[int((d_score-1.)*100.)] += 1.
    if isinstance(p_score,numbers.Number):
        p_hist[int((p_score-1.)*100.)] += 1.
    if isinstance(t_score,numbers.Number):
        t_hist[int((t_score-1.)*100.)] += 1.
    if isinstance(s_score,numbers.Number):
        s_hist[int((s_score-1.)*100.)] += 1.

with open("eqhistograms.csv", "wb") as f:
    writer = csv.writer(f)
    writer.writerows([c_hist,d_hist,p_hist,t_hist,s_hist])



