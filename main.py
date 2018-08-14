from utils import *
import firebase
from firebase_admin import db
from unidecode import unidecode
import sys
from unidecode import unidecode
from pycorenlp import StanfordCoreNLP


'''
    training on training.json; results placed in dict3.json
'''
training_data = 'Pre_Post_Processing/Preprocessing/Training_Data/training.json'
vocab_count = 'Pre_Post_Processing/vocab2.txt'
word_biases = 'Pre_Post_Processing/Preprocessing/Training_Results/dict5.json'
testing_data = 'Pre_Post_Processing/Preprocessing/Test_Data/data.txt'
testing_results = 'Pre_Post_Processing/Preprocessing/Results/dataout.txt'
glove_training = 'Pre_Post_Processing/text8.txt'
keywords = 'Pre_Post_Processing/keywords.json'
testing_set = {}
testing_set['collection'] = []


input = sys.argv[1]
    
if input is '':
    print("\n###DATABASE:###")
    print("Getting ISBNs of training books")
    ISBN = db.reference().child('ISBN_numbers').order_by_child('rating').start_at(0).end_at(100).get().keys()
    print("Get Training set and parse into file")
    count = 0
    for i in range(len(ISBN)):
        print "reading: " , i , "\r"
        for j in range(100):
            child = 'review_' + str(j)
            string1 = db.reference().child('ISBN_numbers').child(ISBN[i]).child(child).get()
            if isinstance(string1,unicode):
                string1 = unidecode(string1)
            if not string1 == None:
                testing_set['collection'].append({})
                testing_set['collection'][count]['rating'] = int(float(db.reference().child('ISBN_numbers').child(ISBN[i]).child('rating').get()))
                testing_set['collection'][count]['review'] = string1
                count += 1

    print("Number of Words used: "+str(count))
    print("\nDump data into datafiles")
    with open(training_data,'w') as data_file:
        json.dump(testing_set,data_file)
    print("Number of Books used: "+str(len(ISBN)))


if input is '1':
    print("\n###TRAINING SEMANTIC:###")
    print("Retrieving sentences from:\t"+training_data)
    sentence_list = retrieve_sentences(training_data)
    print("Writing wordcounts into:\t"+vocab_count)
    [word_count, word_num] = retrieve_wordcount_max(sentence_list,vocab_count)  #make this write to a text file for GloVe purposes
    print("Number of Reviews used: "+str(word_num))
    print("Writing word biases into:\t"+word_biases)
    word_bias(word_count,word_biases,5)


if input is '2':
    print("\n###TRAINING GLOVE:###")
    print("Getting ISBN of all books")
    text8string = ''
    separator = 15
    total_reviews = 0
    results = db.reference().child('ISBN_numbers').get()
    ISBN = results.keys()
    print("filling all book reviews")
    wordcount = 0
    current_book = 0
    nlp = StanfordCoreNLP('http://localhost:9000')
    while wordcount < 17000000 and current_book < len(ISBN):
        for x in range(40):
            child = 'review_' + str(x)
            str1 = db.reference().child('ISBN_numbers').child(ISBN[current_book]).child(child).get()
            if str1:
                i = unicodedata.normalize('NFKD', str1).encode('ascii','ignore')       #convert unicode to str
                output = nlp.annotate(i,properties={'annotators': 'tokenize,ssplit,pos,lemma','outputFormat': 'json'})  #invoke nlp to convert word to lemma
                str1 = ''                                                 #initlialize lemma sentence
                if output['sentences']:
                    for sentence in output['sentences']:                       #for each word in the sentence
                        for word in sentence['tokens']:
                            str1 += word['lemma']                                 #place the lemma in the sentence
                            str1 += ' '                                           #followed by a space
                        str1 = str1[:-1]
                    if isinstance(str1,unicode):
                        str1 = unidecode(str1)
                        total_reviews += 1
                    if isinstance(str1,str):
                        str1 = str1.lower()
                        str1 = ''.join([ c if c.isalnum() else ' ' for c in str1 ])
                        str1.replace('1','one ')
                        str1.replace('2','two ')
                        str1.replace('3','three ')
                        str1.replace('4','four ')
                        str1.replace('5','five ')
                        str1.replace('6','six ')
                        str1.replace('7','seven ')
                        str1.replace('8','eight ')
                        str1.replace('9','nine ')
                        str1.replace('0','zero ')
                        text8string += str1 + ' ' + separator * 'placeholder_string '
                        text8string.replace('  ',' ')
                        wordcount += len(str1.split(' '))
        current_book += 1
        print "Appending book Number: " , current_book , " New wordcount: " , wordcount , "\r"
    with open(glove_training, 'w') as glove_text:
        print("Writing all " + str(total_reviews) + " reviews into:\t"+glove_training)
        glove_text.write(text8string)



print("\n###FILTERING:###")

'''
    testing on data.txt using dict.json; results placed in dataout.json
'''
#print("Writing filtered document into:\t"+testing_results)
#sentence_filter(testing_data,testing_results,word_biases)

'''
    Post processing: employing the GloVe algorithm
'''
#CC_mat, decoding_list = fill_co_occurrence_matrix('Preprocessing/Results/dataout.json','Postprocessing/cooccur.json')
#prob_mat = probability_word1_given_word2(CC_mat)
#synonyms_dict = create_cluster(['plot','character','theme','dialogue','style'],'vectors.txt',50)
