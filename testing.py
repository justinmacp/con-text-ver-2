import firebase
import firebase_admin
import numbers
from firebase_admin import db
import csv

database_node_gt = 'ISBN_numbers'
database_node_test = 'sandbox_justin'
database_node_pre_eq = 'Unscaled_Results_1'

results_test = db.reference().child(database_node_test).get()
results_gt = db.reference().child(database_node_gt).order_by_child('rating').start_at(0).end_at(100).get()
ISBN_test = results_test.keys()
ISBN_gt = results_gt.keys()
ISBN = list(set(ISBN_test) & set(ISBN_gt))
print ISBN

test_score_u = []
test_score = []
gt_score = []
count = 0

for isbn in range(len(ISBN)):
    print "#################"
    test_values = 0
    test_number = 0
    test_values_u = 0
    test_number_u = 0
    c_score = db.reference().child(database_node_test).child(ISBN[isbn]).child('Character_Depth').get()
    #print c_score
    if isinstance(c_score,numbers.Number):
        test_number += 1
        test_values += c_score
        print "Found Character Score"
    d_score = db.reference().child(database_node_test).child(ISBN[isbn]).child('Dialogue').get()
    #print d_score
    if isinstance(d_score,numbers.Number):
        test_number += 1
        test_values += d_score
        print "Found Dialogue Score"
    p_score = db.reference().child(database_node_test).child(ISBN[isbn]).child('Plot').get()
    #print p_score
    if isinstance(p_score,numbers.Number):
        test_number += 1
        test_values += p_score
        print "Found Plot Score"
    t_score = db.reference().child(database_node_test).child(ISBN[isbn]).child('Theme').get()
    #print t_score
    if isinstance(t_score,numbers.Number):
        test_number += 1
        test_values += t_score
        print "Found Theme Score"
    s_score = db.reference().child(database_node_test).child(ISBN[isbn]).child('Writing_Style').get()
    #print s_score
    if isinstance(s_score,numbers.Number):
        print "Found Style Score"
        test_number += 1
        test_values += s_score

    c_score_u = db.reference().child(database_node_pre_eq).child(ISBN[isbn]).child('Character_Depth').get()
    #print c_score
    if isinstance(c_score_u,numbers.Number):
        test_number_u += 1
        test_values_u += c_score_u
        print "Found Character Score"
    d_score_u = db.reference().child(database_node_pre_eq).child(ISBN[isbn]).child('Dialogue').get()
    #print d_score
    if isinstance(d_score_u,numbers.Number):
        test_number_u += 1
        test_values_u += d_score_u
        print "Found Dialogue Score"
    p_score_u = db.reference().child(database_node_pre_eq).child(ISBN[isbn]).child('Plot').get()
    #print p_score
    if isinstance(p_score_u,numbers.Number):
        test_number_u += 1
        test_values_u += p_score_u
        print "Found Plot Score"
    t_score_u = db.reference().child(database_node_pre_eq).child(ISBN[isbn]).child('Theme').get()
    #print t_score
    if isinstance(t_score_u,numbers.Number):
        test_number_u += 1
        test_values_u += t_score_u
        print "Found Theme Score"
    s_score_u = db.reference().child(database_node_pre_eq).child(ISBN[isbn]).child('Writing_Style').get()
    #print s_score
    if isinstance(s_score_u,numbers.Number):
        print "Found Style Score"
        test_number_u += 1
        test_values_u += s_score_u
    
    if not test_number == 0 and not test_number_u == 0:
        test_score.append(test_values/test_number*20.)
        test_score_u.append(test_values_u/test_number_u*20.)
        gt_score.append(db.reference().child('ISBN_numbers').child(ISBN[isbn]).child('rating').get())

    print "#################"

with open("score_scatter.csv", "wb") as f:
    writer = csv.writer(f)
    writer.writerows([test_score,gt_score])

with open("score_scatter_unscaled.csv", "wb") as f:
    writer = csv.writer(f)
    writer.writerows([test_score_u,gt_score])





