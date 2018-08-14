import json, firebase, unicodedata, collections, ast, timeit
import numpy as np
from pprint import pprint
from unidecode import unidecode
from utils import sentence_filter, sentence_cleanup
from firebase_admin import db
from jsonrpc import ServerProxy, JsonRpc20, TransportTcpIp
import sys

isbn = int(sys.argv[1])

########################### To decode dependencies to non-unicode ###########################
def convert_dependencies(f):
	decoded_dependencies=[]
	z=0
	while(z<len(f)):
		decoded_dependencies.append(f[z])
		s=0
		while(s<len(decoded_dependencies[z])):
			p=0
			while(p<len(decoded_dependencies[z][s])):
				if isinstance(decoded_dependencies[z][s][p], unicode):
					decoded_dependencies[z][s][p] = unidecode(decoded_dependencies[z][s][p])
				p=p+1
			s=s+1
		z=z+1
	return(decoded_dependencies)


########################### To decode synonyms dictionary to non-unicode ###########################
def convert_synonyms_dictionary(f):
	temp_list=[]
	decoded_dictionary=[]
	for dictionaries in f: 										# Loop to iterate "number of sentences in sample.txt" times. 
		for k in dictionaries.keys(): 							# Extracts keys from synonyms dictionary.
			if isinstance(k, unicode):  						# If key is in unicode, then decode that key.
				k=unidecode(k)  								# Replace unicoded key with decoded key.
			for v in dictionaries.values():						# Extracts values from corresponding key of synonym dictionary.
				temp_list_1=[]									# Declare empty temp_list_1, it is placed out of next for loop so that it is reinitialized. That gets rid of accumulated entries.
				for x in v:										# Loop to access internal list entries of each dictionary value (each value happens to be a list containing string objects).
					if isinstance(x, unicode):					# If value is in unicde, then decode that value.
						x=unidecode(x)							# Replace unicoded value with decoded value.
					temp_list_1.append(x)						# Append decoded values to temp_list_1.
			temp_list.append([{k:temp_list_1} for i in range(len(dictionaries.keys()))]) # List comprehension to zip decoded key & its corresponding values together. # Mother of inefficiency.

	counter=0													# Declare temporary counter								
	while(counter<len(temp_list)):								# Use while loop to access each object of temp_list. Using a while was better than for loop because you needed to access INTEGER indeces of the list.
		decoded_dictionary.append(temp_list[counter][0])		# Append extracted dictionary object from each list item.
		counter=counter+1										# Increase value of temporary counter.
	return(decoded_dictionary)									# Returns decoded dictionary.

#######################################################################################################

# get ISBN of books that dont have results
results = db.reference().child('ISBN_numbers').get()
ISBN = results.keys()
final_ISBN = ISBN

#pprint(final_ISBN)

review={}
filtered_review=[]

#Make sure to return this: "len(final_ISBN)" in range() next line
#print "##### Get reviews of an ISBN number (needed for testing): ####"
#isbn=final_ISBN.index(u'9781122716482')
review2 =[]
for x in range(40):
	child = 'review_' + str(x)
	str1 = db.reference().child('ISBN_numbers').child(final_ISBN[isbn]).child(child).get()
	review2.append(str1)
filtered_review=filter(None, review2)
if filtered_review:
	review[final_ISBN[isbn]]=filtered_review

title = db.reference().child('ISBN_numbers').child(final_ISBN[isbn]).child('title').get()
author = db.reference().child('ISBN_numbers').child(final_ISBN[isbn]).child('author').get()	

temp=[]
list_1=[]

dictionary={}
temp=review[unidecode(final_ISBN[isbn])]
string=''
for x in temp:
	string = string + x
list_1.append(string)
dictionary['review']=list_1
#print(len(dictionary['review']))
#pprint(dictionary['review'])
#print(' ')
#pprint(final_ISBN[isbn])

Character_Depth=[]
Theme=[]
Dialogue=[]
Plot=[]
Writing_Style=[]
Plot=[]

Plot_score=0
Plot_Rating=0
Plot_count=0

Character_Depth_Score=0
Character_Depth_Rating=0
Character_count=0

Theme_Score=0
Theme_Rating=0
Theme_count=0

Dialogue_Scores=0
Dialogue_Rating=0
Dialogue_count=0

Writing_Style_Scores=0
Writing_Style_Rating=0
Writing_count=0


data={}			
data['review']=dictionary['review']
#print('########################################################################################################')
with open('data.txt','w') as json_file:
	json.dump(data, json_file, indent = 4, ensure_ascii = True)

sentence_filter('data.txt','dataout.txt','Pre_Post_Processing/Preprocessing/Training_Results/dict4.json')
#print "invoking the client"
# 	print(final_ISBN[isbn])
import client
SDT = json.load(open('parsed_and_filtered_out_sentences.json')) # Cleaned out Stanford Dependency Tree.
dict3 = json.load(open('Pre_Post_Processing/Preprocessing/Training_Results/dict4.json'))							# Trained dictionary that contains 1# Expected Value and 2# Variance.
synonyms = json.load(open('Pre_Post_Processing/Preprocessing/synonyms.json'))						# Synonyms dictionary.
Dependencies =[]
sentences =[]

print "going through the SDT"
for i in SDT:													# Loop to iterate through SDT
	Dependencies.append(SDT[str(i)]['dependencies'])			# Extrated dependency values from SDT 'dependencies' key.
	sentences.append(SDT[str(i)]['words'])						# Extrated words from SDT 'word' key # Need to somehow integrate it into this script to do negation.

converted_synonyms = convert_synonyms_dictionary(synonyms)		# Calls function to convert dependencies into non-unicode, and stores it in variable.
#pprint(converted_synonyms)										# Prints converted_list. # Print not needed, but keep it for investigative purposes.
#print('##########################################################################')
converted_list = convert_dependencies(Dependencies)				# Calls function to convert dependencies into non-unicode, and stores it in variable.
#pprint(converted_list)											# Prints converted_list. # Print not needed, but keep it for investigative purposes.

########################## Script to keep branches of interest, and remove unwanted ones ##########################
parents=[]
children=[]
grandChildren=[]
SDT_Final=[]
for synonyms in converted_synonyms:
	key = synonyms.keys()[0]
    #print "####### Searching for information about: " + key + " #######"
	for entries in synonyms[key]:
		for dependencies in converted_list:
			final_sdt = []
			for i in range(len(dependencies)):
				if(dependencies[i][1].lower()==entries.lower()):
                    #print "child found:"
					children.append(dependencies[i][2]) # Isn't this supposed to be [i][1] because we are appending the parent, not the child?
					final_sdt.append(dependencies[i])
                    #print str(dependencies[i])
					for j in range(len(dependencies)):
						if(dependencies[j][1].lower()==dependencies[i][2].lower()):
                            #print "grandchild found:"
 							final_sdt.append(dependencies[j])
                            #print str(dependencies[i])
				if(dependencies[i][2].lower()==entries.lower()):
                    #print "parent found:"
					children.append(dependencies[i][2]) #Here you appended the last entry of the list which is the child to the children list, does that suggest we change the above not to parent?
					final_sdt.append(dependencies[i])
                    #print str(dependencies[i])
			if not final_sdt:
				pass
			else:
				SDT_Final.append(final_sdt)


#print('Final SDT:')
#pprint(SDT_Final)

########################## Script to retrieve expected values of the matched dependency parent words ##########################
##### Remaining:
############### 4) Ask Justin if we need to take the child node into consideration when scoring


for sentences in SDT_Final:
    #pprint(sentences)
	for individual_dependency in sentences:
        #print('Individual Dependency:')
        #pprint(individual_dependency)
        #print('Parent')
		parent=individual_dependency[1]
		children=individual_dependency[2]
        #pprint(parent)
		if(parent.lower() in converted_synonyms[0]['plot'] or children.lower() in converted_synonyms[0]['plot']):
				Plot.append(individual_dependency)
		elif(parent.lower() in converted_synonyms[1]['character'] or children.lower() in converted_synonyms[1]['character']):
 				Character_Depth.append(individual_dependency)
		elif(parent.lower() in converted_synonyms[2]['theme'] or children.lower() in converted_synonyms[2]['theme']):
				Theme.append(individual_dependency)
		elif(parent.lower() in converted_synonyms[3]['dialogue'] or children.lower() in converted_synonyms[3]['dialogue']):
				Dialogue.append(individual_dependency)		
		elif(parent.lower() in converted_synonyms[4]['style'] or children.lower() in converted_synonyms[4]['style']):
 				Writing_Style.append(individual_dependency)


#print('################ Character_Depth ####################')
#pprint(Character_Depth)
#print('#####################################################')

for character_1 in Character_Depth:
	negation=False
    #pprint(character_1)
	if(character_1[0]=='neg'):
		negation=True
        #print('negation DETECTED')
	Character_Depth_parent = character_1[1]
	Character_Depth_children= character_1[2]
    #pprint(Character_Depth_parent)
	for entries in dict3['dct']:
		if(Character_Depth_parent.lower() == entries[0]):
            #print('Detected Word:')
            #print str(Character_Depth_parent)
            #print "Value:"
			value=float(entries[1])
			if(negation==True):
				value=100-value 
			Character_Depth_Score = Character_Depth_Score + (value)
            #print(value)
#			print(entries[2]) #This line proves that there is a logical problem of finding non-exact case matches in the dictionary, which messes up the score.			
			Character_count = Character_count + 1
		if(Character_Depth_children.lower() == entries[0]):
            #print('Detected Word:')
            #print str(Character_Depth_children)
            #print "Value:"
			value=float(entries[1])
			if(negation==True):
				value=100-value 
			Character_Depth_Score = Character_Depth_Score + (value)
            #print(value)
#			print(entries[2]) #This line proves that there is a logical problem of finding non-exact case matches in the dictionary, which messes up the score.			
			Character_count = Character_count + 1
if(Character_count==0):
	Character_Depth_Rating='NA'
    #print('Score is ' + Character_Depth_Rating)
else:
    #print('Sum of scores:')
    #print(Character_Depth_Score)
    #print('Number of scores:')
    #print(Character_count)
    #print('Average Score:')
	average=float(Character_Depth_Score/Character_count)
    #print(average)
    #print('Score out of 5:')
	Character_Depth_Rating=round(((average/100)*5),2)
	if (Character_Depth_Rating<1):
		Character_Depth_Rating=1
    #print(Character_Depth_Rating)


#print('############# Theme ################')
#pprint(Theme)
#print('####################################')

for theme_1 in Theme:
	negation=False
    #pprint(theme_1)
	if(theme_1[0]=='neg'):
		negation=True
        #print('negation DETECTED')
	Theme_parent = theme_1[1]
	Theme_child = theme_1[2]
    #pprint(Theme_parent)
	for entries_1 in dict3['dct']:
		if(Theme_parent.lower() == entries_1[0]):
            #print('Detected Word:')
            #print str(Theme_parent)
            #print "Value:"
			value=float(entries_1[1])
			if(negation==True):
				value=100-value
			Theme_Score = Theme_Score + (value)			
            #print(value)
#			print(entries_1[2]) #This line proves that there is a logical problem of finding non-exact case matches in the dictionary, which messes up the score.			
			Theme_count = Theme_count + 1
		if(Theme_child.lower() == entries_1[0]):
            #print('Detected Word:')
            #print str(Theme_child)
            #print "Value:"
			value=float(entries_1[1])
			if(negation==True):
				value=100-value
			Theme_Score = Theme_Score + (value)			
            #print(value)
#			print(entries_1[2]) #This line proves that there is a logical problem of finding non-exact case matches in the dictionary, which messes up the score.			
			Theme_count = Theme_count + 1				
if(Theme_count==0):
	Theme_Rating='NA'
    #print('Score is ' + Theme_Rating)
else:
    #print('Sum of scores:')
    #print(Theme_Score)
    #print('Number of scores:')
    #print(Theme_count)
    #print('Average Score:')
	average=float(Theme_Score/Theme_count)
    #print(average)
    #print('Score out of 5:')
	Theme_Rating=round(((average/100)*5),2)
	if(Theme_Rating<1):
		Theme_Rating=1
    #print(Theme_Rating)


#print('############### Dialogue ##############')
#pprint(Dialogue)
#print('#######################################')

for dialogue_1 in Dialogue:
	negation=False	
    #pprint(dialogue_1)
	if(dialogue_1[0]=='neg'):
		negation=True
        #print('negation DETECTED')
	Dialogue_parent = dialogue_1[1]
	Dialogue_children = dialogue_1[2]
    #pprint(Dialogue_parent)
	for entries_2 in dict3['dct']:
		if(Dialogue_parent.lower() == entries_2[0]):
            #print('Detected Word:')
            #print str(Dialogue_parent)
            #print "Value:"
			value=float(entries_2[1])
			if(negation==True):
				value=100-value			
			Dialogue_Scores = Dialogue_Scores + (value)
            #print(value)
#			print(entries_2[2]) #This line proves that there is a logical problem of finding non-exact case matches in the dictionary, which messes up the score.			
			Dialogue_count = Dialogue_count + 1
		if(Dialogue_children.lower() == entries_2[0]):
            #print('Detected Word:')
            #print str(Dialogue_children)
            #print "Value:"
			value=float(entries_2[1])
			if(negation==True):
				value=100-value			
			Dialogue_Scores = Dialogue_Scores + (value)
            #print(value)
#			print(entries_2[2]) #This line proves that there is a logical problem of finding non-exact case matches in the dictionary, which messes up the score.			
			Dialogue_count = Dialogue_count + 1				
if(Dialogue_count==0):
	Dialogue_Rating='NA'
    #print('Score is ' + Dialogue_Rating)
else:
    #print('Sum of scores:')
    #print(Dialogue_Scores)
    #print('Number of scores:')
    #print(Dialogue_count)
    #print('Average Score:')
	average=float(Dialogue_Scores/Dialogue_count)
    #print(average)
    #print('Score out of 5:')
	Dialogue_Rating=round(((average/100)*5),2)
	if(Dialogue_Rating<1):
		Dialogue_Rating=1
    #print(Dialogue_Rating)


#print('############ Writing_Style ################')
#pprint(Writing_Style)
#print('###################################')

for style_1 in Writing_Style:
	negation=False
    #pprint(style_1)
	if(style_1[0]=='neg'):
		negation=True
        #print('negation DETECTED')
	Writing_Style_parent = style_1[1]
	Writing_Style_children = style_1[2]
    #pprint(Writing_Style_parent)
	for entries_3 in dict3['dct']:
		if(Writing_Style_parent.lower() == entries_3[0]):
            #print('Detected Word:')
            #print str(Writing_Style_parent)
            #print "Value:"
			value=float(entries_3[1])
			if(negation==True):
				value=100-value 			
			Writing_Style_Scores = Writing_Style_Scores + (value)
            #print(value)
#			print(entries_3[2]) #This line proves that there is a logical problem of finding non-exact case matches in the dictionary, which messes up the score.
			Writing_count = Writing_count + 1
		if(Writing_Style_children.lower() == entries_3[0]):
            #print('Detected Word:')
            #print str(Writing_Style_children)
            #print "Value:"
			value=float(entries_3[1])
			if(negation==True):
				value=100-value 			
			Writing_Style_Scores = Writing_Style_Scores + (value)
            #print(value)
#			print(entries_3[2]) #This line proves that there is a logical problem of finding non-exact case matches in the dictionary, which messes up the score.
			Writing_count = Writing_count + 1				
if(Writing_count==0):
	Writing_Style_Rating='NA'
    #print('Score is ' + Writing_Style_Rating)
else:	
    #print('Sum of scores:')
    #print(Writing_Style_Scores)
    #print('Number of scores:')
    #print(Writing_count)
    #print('Average Score:')
	average=float(Writing_Style_Scores/Writing_count)
    #print(average)
    #print('Score out of 5:')
	Writing_Style_Rating=round(((average/100)*5),2)
	if(Writing_Style_Rating<1):
		Writing_Style_Rating=1
    #print(Writing_Style_Rating)


#print('############ Plot ################')
#pprint(Plot)
#print('###################################')

for plot_1 in Plot:
	negation=False
    #pprint(plot_1)
	if(plot_1[0]=='neg'):
		negation=True
        #print('negation DETECTED')
	Plot_parent = plot_1[1]
	Plot_children = plot_1[2]
    #pprint(Plot_parent)
	for entries_4 in dict3['dct']:
		if(Plot_parent.lower() == entries_4[0]):
            #print('Detected Word:')
            #print str(Plot_parent)
            #print "Value:"
			value=float(entries_4[1])
			if(negation==True):
				value=100-value 
			Plot_score = Plot_score + (value)				
            #print(value)
#			print(entries_4[2]) #This line proves that there is a logical problem of finding non-exact case matches in the dictionary, which messes up the score.			
			Plot_count = Plot_count + 1
		if(Plot_children.lower() == entries_4[0]):
            #print('Detected Word:')
            #print str(Plot_children)
            #print "Value:"
			value=float(entries_4[1])
			if(negation==True):
				value=100-value 
			Plot_score = Plot_score + (value)				
            #print(value)
#			print(entries_4[2]) #This line proves that there is a logical problem of finding non-exact case matches in the dictionary, which messes up the score.			
			Plot_count = Plot_count + 1
if(Plot_count==0):
	Plot_Rating='NA'
    #print('Score is ' + Plot_Rating)
else:
    #print('Sum of scores:')
    #print(Plot_score)
    #print('Number of scores:')
    #print(Plot_count)
    #print('Average Score:')
	average=float(Plot_score/Plot_count)
    #print(average)
    #print('Score out of 5:')
	Plot_Rating=round(((average/100)*5),2)
	if(Plot_Rating<1):
		Plot_Rating=1
    #print(Plot_Rating)

sentence_string=[]
sentence_score=[]
most_positive_sentence=''
most_negative_sentence=''


#print('############### SDT ###############')
#pprint(Dependencies)
#print('###################################')

with open('dataout.txt', 'r') as sentences:
    data = sentences.read()   
    data_refined = ast.literal_eval(data) # Load all data in 'review'

max_plot = 0
max_character = 0
max_dialogue = 0
max_style = 0
max_theme = 0
sentence_counter = 0
plot_index = None
character_index = None
dialogue_index = None
theme_index = None
style_index = None

for sentence in converted_list:
    pprint(sentence)
    score=0
    value=0
    counter=0
    plot = False
    character = False
    dialogue = False
    style = False
    theme = False
    #print('##################### New Sentence #####################')
    for word in sentence:
        negation=False
        if(word[1].lower() in converted_synonyms[0]['plot']):
            plot = True
        if(word[1].lower() in converted_synonyms[1]['character']):
            character = True
        if(word[1].lower() in converted_synonyms[4]['style']):
            style = True
        if(word[1].lower() in converted_synonyms[2]['theme']):
            theme = True
        if(word[1].lower() in converted_synonyms[3]['dialogue']):
            dialogue = True
        for entries_5 in dict3['dct']:
            decoded_entry=unidecode(entries_5[0])
            if(word[1].lower() == decoded_entry):
                if(word[0]=='neg'):
                    negation=True
                value=float(entries_5[1])
                if(negation==True):
                    value=100-value
                score = score + value
                counter=counter+1
            if(word[2].lower() == decoded_entry):
                if(word[0]=='neg'):
                    negation=True
                value=float(entries_5[1])
                if(negation==True):
                    value=100-value
                score = score + value
                counter=counter+1
    if(counter != 0):
        if plot:
            if max_plot < score:
                max_plot = score
                plot_index = sentence_counter
        if character:
            if max_character < score:
                max_character = score
                character_index = sentence_counter
        if dialogue:
            if max_dialogue < score:
                max_dialogue = score
                dialogue_index = sentence_counter
        if theme:
            if max_theme < score:
                max_theme = score
                theme_index = sentence_counter
        if style:
            if max_style < score:
                max_style = score
                style_index = sentence_counter

        sentence_score.append(score/counter)
    else:
        sentence_score.append(score)
    sentence_counter += 1

#print('List of scores:')
#pprint(sentence_score)

#print('Number of total scores:')
#print(len(sentence_score))

#print('Number of dependencies found in SDT dictionary a.k.a sentences:')
#print(len(Dependencies))

#print('Number of sentences from JSON file:')
#print(len(data_refined))

#To fill database with
#print "Updating Database"
ISBN = unidecode((final_ISBN[isbn]))

db.reference().child('sandbox_justin').update({ISBN:{'Author':author}})

if not plot_index == None:
    most_positive_sentence_p=str(data_refined[plot_index])
    db.reference().child('sandbox_justin').child(ISBN).update({'Most_Positive_Sentence_Plot':most_positive_sentence_p})
if not dialogue_index == None:
    most_positive_sentence_d=str(data_refined[dialogue_index])
    db.reference().child('sandbox_justin').child(ISBN).update({'Most_Positive_Sentence_Dialogue':most_positive_sentence_d})
if not character_index == None:
    most_positive_sentence_c=str(data_refined[character_index])
    db.reference().child('sandbox_justin').child(ISBN).update({'Most_Positive_Sentence_Character':most_positive_sentence_c})
if not style_index == None:
    most_positive_sentence_s=str(data_refined[style_index])
    db.reference().child('sandbox_justin').child(ISBN).update({'Most_Positive_Sentence_Style':most_positive_sentence_s})
if not theme_index == None:
    most_positive_sentence_t=str(data_refined[theme_index])
    db.reference().child('sandbox_justin').child(ISBN).update({'Most_Positive_Sentence_Theme':most_positive_sentence_t})

#dict_character = {'Character_Depth':Character_Depth_Rating}
db.reference().child('Unscaled_Results_1').child(ISBN).update({'Character_Depth':Character_Depth_Rating})

#dict_theme = {'Theme':Theme_Rating}
db.reference().child('Unscaled_Results_1').child(ISBN).update({'Theme':Theme_Rating})

#dict_dialogue = {'Dialogue':Dialogue_Rating}
db.reference().child('Unscaled_Results_1').child(ISBN).update({'Dialogue':Dialogue_Rating})

#dict_plot = {'Plot':Plot_Rating}
db.reference().child('Unscaled_Results_1').child(ISBN).update({'Plot':Plot_Rating})

#dict_writingstyle = {'Writing_Style':Writing_Style_Rating}
db.reference().child('Unscaled_Results_1').child(ISBN).update({'Writing_Style':Writing_Style_Rating})

#Title
db.reference().child('sandbox_justin').child(ISBN).update({'Title':title})

#ISBN List
db.reference().child('List_of_isbns_for_your_record').child(ISBN).update({'-':ISBN})

print(ISBN)
#print(isbn)
