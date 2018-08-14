import json
import yaml
import nltk.data
import math
from unidecode import unidecode
import unicodedata
import numpy as np
from pycorenlp import StanfordCoreNLP


'''
    uses json
    uses nltk.data
    result used in retrieve_wordcount
    retrieve_sentences(path) takes in the path to a json file that is structured as follows:
    
    {"collection":[{"rating": "78", "text": "This is a review."},...]}
    
    it returns 5 lists for each of the different ratings, neglecting any rating that is not an integer number from 1 to 5
'''
def retrieve_sentences(path):                                       #function to retrieve word statistics
    nlp = StanfordCoreNLP('http://localhost:9000')                  #define location of server at localhost port 9000
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')   #create an instance of the english tokenizer
    with open(path, 'r') as json_file:                              #open file
        data = json.load(json_file)                                 #load file into data
#    list90 = list()                                                 #initialize list for sentences ranked in the 90s
#    list80 = list()                                                 #initialize list for sentences ranked in the 80s
#    list70 = list()                                                 #initialize list for sentences ranked in the 70s
#    list60 = list()                                                 #initialize list for sentences ranked in the 60s
#    list50 = list()                                                 #initialize list for sentences ranked in the 50s
    sentencedict = []                                               #create dictionary to store the output sentnces
    for review in data['collection']:                                               #go through all collected reviews
        if not review['review'] == None:                                            #verify if the review contains a string
            sentences = tokenizer.tokenize(review['review'])                        #tokenize each review
            for i in sentences:                                                     #go through tokens in review
                if i:
                    i = unicodedata.normalize('NFKD', i).encode('ascii','ignore')       #convert unicode to str
                    output = nlp.annotate(i,properties={'annotators': 'tokenize,ssplit,pos,lemma','outputFormat': 'json'})  #invoke nlp to convert word to lemma
                    if output['sentences']:
                        lemma_sentence = ''                                                 #initlialize lemma sentence
                        for word in output['sentences'][0]['tokens']:                       #for each word in the sentence
                            lemma_sentence += word['lemma']                                 #place the lemma in the sentence
                            lemma_sentence += ' '                                           #followed by a space
                        lemma_sentence = lemma_sentence[:-1]                                #remove last space of the sentnece
                        sentencedict.append({'sentence': lemma_sentence, 'rating': review['rating']})    #add token
        
        '''
        if eval(review['rating']) > 90 :                            #if review is ranked 90 or above
            sentences = tokenizer.tokenize(review['review'])        #tokenize data into sentences
            for p in sentences:
                list90.append(p)                                    #add sentences to list of rank 90 sentences
        elif eval(review['rating']) > 80 :                          #if review is ranked in the 80s
            sentences = tokenizer.tokenize(review['review'])        #tokenize data into sentences
            for p in sentences:
                list80.append(p)                                    #add sentences to list of rank 80 sentences
        elif eval(review['rating']) > 70 :                          #if review is ranked in the 70s
            sentences = tokenizer.tokenize(review['review'])        #tokenize data into sentences
            for p in sentences:
                list70.append(p)                                    #add sentence to list of rank 70 sentences
        elif eval(review['rating']) > 60 :                          #if review is ranked in the 60s
            sentences = tokenizer.tokenize(review['review'])        #tokenize data into sentences
            for p in sentences:
                list60.append(p)                                    #add sentence to list of rank 60 sentences
        elif eval(review['rating']) <= 60 :                         #if review is ranked in the 50s
            sentences = tokenizer.tokenize(review['review'])        #tokenize data into sentences
            for p in sentences:
                list50.append(p)                                    #add sentence to list of rank 50 sentences
        '''

    return sentencedict                       #return dictionary

'''
    uses results from retrieve_sentences
    retrieve_wordcount(sentencelist) takes in a list that is generated by retrieve_sentences, i.e. this list will contain all sentences from a review in a list and it returns the individual words in all the sentences along with their total count in a dictionary
'''
def retrieve_wordcount(sentencelist,outfile):               #function to retrieve wordcount
    wordlist = []                                           #create list to store words
    total_num_words = 0
    for sentence in sentencelist:                           #FOR LOOP (1): go through all the sentences in sentencelist
        words_in_p = sentence_cleanup(sentence['sentence'])     #clean up each sentence and return a list of words
        if not wordlist:                                        #if the wordlist is still empty
            wordlist.append({'word': words_in_p[0], 'local_data' :[{'count': 0, 'rating': sentence['rating']}], 'global_count': 0}) #add first word
        for word in words_in_p:                                 #FOR LOOP (2): go through all the words in the sentence
            word_element_exists = False                             #initialize boolean indicating existence of a word in the dictionary
            for element in wordlist:                                #FOR LOOP (3): go through all the words in the dictionary
                if element['word'] == word:                             #if the word exists in the dictionary
                    word_element_exists = True                          #set boolean to true indicating existence of word in dictionary
                    element['global_count'] +=1                         #increment its global count
                    total_num_words += 1
                    local_rating_exists = False                         #initialize a boolean indicating wheither the local data for that word exists yet
                    for local_rating in element['local_data']:          #FOR LOOP (4): go through all the local ratings
                        if  local_rating['rating'] == sentence['rating']:   #if local rating already exists
                            local_rating['count'] += 1                      #increment the local count
                            local_rating_exists = True                      #set boolean to true indicating existence of local rating
                            break                                           #break out of loop (4)
                    if not local_rating_exists:                         #if local rating doesn't exist
                        element['local_data'].append({'count': 1, 'rating': sentence['rating']})    #add it to local data
            if not word_element_exists:                         #if word doesn't exist in dictionary
                print ("new word found: ", word)
                wordlist.append({'word': word, 'local_data' :[{'count': 1, 'rating': sentence['rating']}], 'global_count': 1}) #add new entry
                total_num_words += 1
    
#    with open(outfile,'w') as file:                                                     #open the txt file to hold wordcount
#        for element in wordlist:                                                        #for each registered word
#            file.write(element['word'] + " " + str(element['global_count']) + "\n")     #dump the wordcount
    return wordlist, total_num_words                                                     #return the dictionary indicating word, count and rating

'''
    uses results from retrieve_sentences
    retrieve_wordcount(sentencelist) takes in a list that is generated by retrieve_sentences, i.e. this list will contain all sentences from a review in a list and it returns the individual words in all the sentences along with their total count in a dictionary
    '''
def retrieve_wordcount_max(sentencelist,outfile):           #function to retrieve wordcount
    
    #fill overall count of words per document
    total_wordcounts = []
    for i in range(101):
        total_wordcounts.append(0)
    for i in range(101):
        for sentence in sentencelist:
            words_in_sen = sentence_cleanup(sentence['sentence'])
            total_wordcounts[sentence['rating']] += len(words_in_sen)

    #get term numbers
    wordlist = []                                           #create list to store words
    total_num_words = 0
    for sentence in sentencelist:                           #FOR LOOP (1): go through all the sentences in sentencelist
        words_in_p = sentence_cleanup(sentence['sentence'])     #clean up each sentence and return a list of words
        if not wordlist:                                        #if the wordlist is still empty
            wordlist.append({'word': words_in_p[0], 'local_data' :[{'count': 0, 'rating': sentence['rating']}], 'global_count': 0}) #add first word
        for word in words_in_p:                                     #FOR LOOP (2): go through all the words in the sentence
            word_element_exists = False                             #initialize boolean indicating existence of a word in the dictionary
            for element in wordlist:                                #FOR LOOP (3): go through all the words in the dictionary
                if element['word'] == word:                             #if the word exists in the dictionary
                    word_element_exists = True                          #set boolean to true indicating existence of word in dictionary
                    element['global_count'] +=1                         #increment its global count
                    total_num_words += 1
                    local_rating_exists = False                         #initialize a boolean indicating wheither the local data for that word exists yet
                    for local_rating in element['local_data']:          #FOR LOOP (4): go through all the local ratings
                        if  local_rating['rating'] == sentence['rating']:   #if local rating already exists
                            local_rating['count'] += 1                      #increment the local count
                            local_rating_exists = True                      #set boolean to true indicating existence of local rating
                            break                                           #break out of loop (4)
                    if not local_rating_exists:                         #if local rating doesn't exist
                        element['local_data'].append({'count': 1, 'rating': sentence['rating']})    #add it to local data
            if not word_element_exists:                         #if word doesn't exist in dictionary
                wordlist.append({'word': word, 'local_data' :[{'count': 1, 'rating': sentence['rating']}], 'global_count': 1}) #add new entry
                total_num_words += 1

    #get term frequencies
    print "Wordcounts by rating: " + str(total_wordcounts)
    for word in range(len(wordlist)):
        for counts in range(len(wordlist[word]['local_data'])):
            a = wordlist[word]['local_data'][counts]['count']
            b = float(total_wordcounts[wordlist[word]['local_data'][counts]['rating']])
            wordlist[word]['local_data'][counts]['count'] = a / b
        wordlist[word]['idf'] = math.log(100/float(len(wordlist[word]['local_data'])))

    #    with open(outfile,'w') as file:                                                     #open the txt file to hold wordcount
#        for element in wordlist:                                                        #for each registered word
#            file.write(element['word'] + " " + str(element['global_count']) + "\n")     #dump the wordcount
    return wordlist, total_num_words                                                     #return the dictionary indicating word, count and rating

    '''
    #instantiate a dictionary object to give the number of times a word has been counted for each word
    dict = [{}]                     #instantiate the dictionary object
    for element in wordlist:        #go throught the wordlist
        if not element in dict:     #if word doesn't exist in dictionary
            dict[element] = 1       #add word to dictionary
        else:                       #if word already exists in dictionary
            dict[element] += 1      #increment count of word
    return dict                     #return dictionary
    '''

'''
    uses json
    wordbias(wordlist1,wordlist2,wordlist3,wordlist4,wordlist5) takes in dictionaries of words and their wordcounts as generated by retrieve_wordcount. wordbias will perform statistical analysis to check for dependence of a word to the ranking and it will output a dictionary that contains all dependent words with their calcuated bias. Optionally it will also return the expected ranking of a word and the standard deviation of that ranking
    returns list of dependent words in a json file
'''
def word_bias_max(wordlist,jsonfile,thresh):   #function to filter out words and give their biases
    wordbias = []
    dictionary = {}
    ################################ Using probabilistic calculations to calcuate dependence ################################
    unique_words = 0
    total_tokens = 0
    
    for word in wordlist:  #iterate through wordlist1 since it has been augmented to contain all words in all 5 lists
        
        #MAX OF A WORD
        max_count = 0
        for rating in word['local_data']:
            if max_count < rating['count']:
                max_count = rating['count']
                max_freq = rating['rating']
        
        unique_words += 1
        wordbias.append([word['word'], max_freq, word['global_count']])
    
    dictionary['dct'] = wordbias
    
    with open(jsonfile,'w') as json_file:       #open the json file to hold the dependent dictionary
        json.dump(dictionary, json_file)        #dump the dependent dictionary into the json file
    print "#### unique:" + str(unique_words)
    print "#### tokens:" + str(total_tokens)
    return wordbias

def word_bias(wordlist,jsonfile,thresh):   #function to filter out words and give their biases
    wordbias = []
    dictionary = {}
    ################################ Using probabilistic calculations to calcuate dependence ################################
    unique_words = 0
    total_tokens = 0
    
    for word in wordlist:  #iterate through wordlist1 since it has been augmented to contain all words in all 5 lists
        
        total_tokens += 1
        expected_value = 0.
        standard_deviation = 0.
        #EXPECTED VALUE FOR THE RATING OF A WORD
        for rating in word['local_data']:
            expected_value += rating['rating']*rating['count']
        expected_value /= word['global_count']
        
        #STANDARD DEVIATION OF THE RATING OF A WORD
        for rating in word['local_data']:
            standard_deviation += rating['count']*(rating['rating']-expected_value)**2
        standard_deviation = (standard_deviation/word['global_count'])**0.5
        
        #MAX OF A WORD
        max_count = 0
        for rating in word['local_data']:
            if max_count < rating['count']:
                max_count = rating['count']
                max_freq = rating['rating']

        unique_words += 1
        wordbias.append([word['word'], expected_value, standard_deviation, max_freq, word['idf']])
    
    dictionary['dct'] = wordbias
    
    with open(jsonfile,'w') as json_file:       #open the json file to hold the dependent dictionary
        json.dump(dictionary, json_file)        #dump the dependent dictionary into the json file
    print "#### unique:" + str(unique_words)
    print "#### tokens:" + str(total_tokens)
    return wordbias

'''
    uses json
    sentence_filter takes in the path to the unfiltered json file and the path to a new json file which is to hold the output of this function. It also takes the list of dependent words. Comparing the dependent words to the words in the input file it removes any sentence that doesn't contain any dependent word. The output is dumped into the output json file
'''
def sentence_filter(inpath, outpath, dictpath):                     #function to remove noise sentences from a json file
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')   #create an instance of the english tokenizer
    with open(dictpath, 'r') as json_dictfile:                      #open the dictionary of dependent words
        dep_dict = json.load(json_dictfile)['dct']                  #extract the dictionary
    with open(inpath, 'r') as json_infile:                          #open the input json file that contains the unfiltered review
        '''this line is causing unicode characters to be interpreted as ascii'''
        data = json.load(json_infile)                               #load data from input json file
    sentences = []                                                  #instantiate list to hold sentences of review
    full_review = ""
    for i in range(len(data['review'])):                            #go through review and remove all non ascii characters


            #LOOKUP TABLE FOR UNICODE CHARACTERS
        data['review'][i] = data['review'][i].replace('\\u00a3','pounds ')
        data['review'][i] = data['review'][i].replace('\\u00fc','ue')
        data['review'][i] = data['review'][i].replace('\\u2026','... ')
        data['review'][i] = data['review'][i].replace('\\u200b','')
        data['review'][i] = data['review'][i].replace('\\u2018','\' ')
        data['review'][i] = data['review'][i].replace('\\u00a0',' ')
        data['review'][i] = data['review'][i].replace('\\u00e1','a')
        data['review'][i] = data['review'][i].replace('\\u00e9','e')
        data['review'][i] = data['review'][i].replace('\\u00c9','E')
        data['review'][i] = data['review'][i].replace('\\u00ad','')
        data['review'][i] = data['review'][i].replace('\\u2011','- ')
        data['review'][i] = data['review'][i].replace('\\u00e7','c')
        data['review'][i] = data['review'][i].replace('\\u00a9','copyright symbol')
        data['review'][i] = data['review'][i].replace('\\u00ed','i')
        data['review'][i] = data['review'][i].replace('\\u00e2','a')
        data['review'][i] = data['review'][i].replace('\\u00f8','o')
        data['review'][i] = data['review'][i].replace('\\u00fb','u')
        data['review'][i] = data['review'][i].replace('\\u2022','.')
        data['review'][i] = data['review'][i].replace('\\u00f3','o')
        data['review'][i] = data['review'][i].replace('\\u009d','trademark symbol')
        data['review'][i] = data['review'][i].replace('\\u2030','per mille')
        data['review'][i] = data['review'][i].replace('\\u02bc','\' ')
        data['review'][i] = data['review'][i].replace('\\u00eb','e')
        data['review'][i] = data['review'][i].replace('\\u00e4','ae')
        data['review'][i] = data['review'][i].replace('\\u00f6','oe')
        data['review'][i] = data['review'][i].replace('\\u00e0','e')
        data['review'][i] = data['review'][i].replace('\\u00f4','o')
        data['review'][i] = data['review'][i].replace('\\u201d','"')
        data['review'][i] = data['review'][i].replace('\\u201c','"')
        data['review'][i] = data['review'][i].replace('\\u2019','\' ')
        data['review'][i] = data['review'][i].replace('\\u2014','- ')
        data['review'][i] = data['review'][i].replace('\\u2013','- ')
        data['review'][i] = data['review'][i].replace('\r','')
        data['review'][i] = data['review'][i].replace('\n',' ')
        full_review += data['review'][i]
        full_review += " "

    tokens = tokenizer.tokenize(full_review)  #tokenize data into sentences
    for token in tokens:                            #for each token
        sentences.append(token)                     #append to sentences

    dep_sentences = []                                              #create list that will contain all dependent sentences
    for ia in sentences:                                            #FOR LOOP (1): go though all sentences in that file
        contains_dep = False                                        #boolean variable indicating wheither or not a sentence contains a dependent word
        wordlist = sentence_cleanup(ia)                             #extract words in a list for each of those sentences
        for word in wordlist:                                       #FOR LOOP (2): go though each of those words
            for dep_word in dep_dict:                               #FOR LOOP (3): go through the list of dependent words given in the function call
                if dep_word[2] < 10:                                #if the word matches with a dependent word
                    contains_dep = True                             #set contains_dep to true
                    break                                           #break out of FOR LOOP (3) and go into FOR LOOP (2)
            if contains_dep:                                        #if a dependent word exists in the sentence
                break                                               #break out of FOR LOOP (2) and go into FOR LOOP (1)
        if contains_dep:                                            #if no dependent word exists in the sentence
            dep_sentences.append(ia)                                #remember that sentence
    for i in range(len(dep_sentences)):                             #go through dependent sentences
        if isinstance(dep_sentences[i],unicode):                    #check if sentence is encoded in unicode format
            dep_sentences[i] = unidecode(dep_sentences[i])          #decode that sentence
    with open(outpath, 'w') as outfile:                             #open the output json file to save the filtered data
        outfile.write(str(dep_sentences))                           #dump the filtered sentences into the output file



'''
    sentence_cleanup takes in a sentence and returns a list of the words contained in that sentence removing punctuation
'''
def sentence_cleanup(sentence):                     #function to extract the word list from a sentence
    wordlist = sentence.split()                     #split sentences into individual words
    wordlist = [x for x in wordlist if x != '-']    #remove all dashes from the wordlist
    for i in range(len(wordlist)):                  #iterate through all words to remove punctuation etc.
        newstring = wordlist[i]                     #place full word into a placeholder
    
        #check beginning of word for apostrophes etc.
        if not (newstring[0].isalnum()):    #if first character is not aphanumeric
            newstring = newstring[1:]       #remove it
        
        #check end of word for punctuation, elipses etc.
        if len(newstring) >= 1:                                                 #if word still has characters
            if not (newstring[len(newstring)-1].isalnum()):                     #in a 3x nested if statement check the last 3 characters
                newstring = newstring[:len(newstring)-1]                        #if last char is a symbol remove it
                if len(newstring) >= 1:                                         #if word still has characters
                    if not (newstring[len(newstring)-1].isalnum()):             #if second last char is a symbol
                        newstring = newstring[:len(newstring)-1]                #remove it
                        if len(newstring) >= 1:                                 #if word still has characters
                            if not (newstring[len(newstring)-1].isalnum()):     #if third last char is a symbol
                                    newstring = newstring[:len(newstring)-1]    #remove it
        
        wordlist[i] = newstring.lower() #replace word from list with the cleaned up string in lowercase
    return wordlist                     #return the wordlist

'''
    uses numpy
    create_cluster takes a list of keywords, a file containing GloVe vectors and the dimmensinality of the GloVe space.
    It returns a list of all words synonymous to the given keywords in the format of a dictionary.
'''
def create_cluster(keywords,vector_file,dimms,th):      #definition of function
    vector_dict = []                                    #instantiate a list to hold all word vectors as read from the vector file
    synonyms_dict = []                                  #instantiate a list to hold all synonyms of the key words
    key_vect = []                                       #instantiate a list to hold the GloVe vectors of all the key words
    

    #write vector file to dict
    with open(vector_file,'r') as vector_txt:                           #open the file
        vectors_and_key = vector_txt.readlines()                        #read each line into vector and key list
    for line in vectors_and_key:                                        #for each line in list
        vector = line.split(" ")                                        #split at each space
        word = vector[0]                                                #the first entry of each line is the word in question
        del vector[0]                                                   #remove the word from the line, so that the rest of the line can be interpreted as a list of numbers
        dict_entry = {}                                                 #create dictionary to hold word and vector
        dict_entry[word] = map(float,vector)                            #map the rest of the line into a list of floats and place them under the word as a key
        vector_lenght = 0.                                              #instantiate vector length, which will be used to normalize each vector
        for i in range(dimms):                                          #for each entry in the vector
            vector_lenght += dict_entry[word][i]**2.                    #add the square of that entry
        vector_lenght = vector_lenght**(.5)                             #take the root of that sum, which gives the length of the vector
        for i in range(dimms):                                          #for each dimmension
            dict_entry[word][i] = dict_entry[word][i]/vector_lenght     #divide entry by the vector length (normalize)
        vector_dict.append(dict_entry)                                  #append each unit vector to the vector list

    #find keywords in the vector file
    for i in range(len(keywords)):                          #for each keyword
        for words in vector_dict:                           #for each word
            if keywords[i] in words:                        #if the keyword is the current word
                if not words[keywords[i]] in key_vect:      #if the keyword is also not already in the list of keyword vectors
                    key_vect.append(words[keywords[i]])     #add the vector of the keyword to the key vector list
                    break                                   #break and go to next keyword
    
    for i in range(len(key_vect)):                                                          #go through key words
        synonyms_list = []                                                                  #reset the synonyms list
        synonyms_append = {}                                                                #reset synonyms to append to dictionary
        print("###################",keywords[i],"#######################\n")                #print the word in question
        for words in vector_dict:                                                           #go through all words
            cosine_similarity = np.dot(key_vect[i],words[next(iter(words))])                #get cosine similarity
            if cosine_similarity >= th:                                                     #if cosine similarity is greater than the threshold
                synonyms_list.append(next(iter(words)))                                     #add word to listo of synonyms
                print(str(next(iter(words)))+ ": Cosine Similarity: ", cosine_similarity)   #print the cosine similarity of each synonym
        synonyms_append[keywords[i]] = synonyms_list                                        #add all synonyms to a dictionary whose key is the key word
        synonyms_dict.append(synonyms_append)                                               #append that dictionary to the synonyms dictionary

    return synonyms_dict    #return the synonyms

'''
    unused
    uses numpy
    create_cluster takes a list of keywords, a file containing GloVe vectors and the dimmensinality of the GloVe space.
    It returns a list of all words synonymous to the given keywords in the format of a dictionary.
    '''
def create_sent_cluster(keywords,vector_file,dimms):    #definition of function
    vector_dict = []                                    #instantiate a list to hold all word vectors as read from the vector file
    synonyms_dict = {}                                  #instantiate a list to hold all synonyms of the key words
    key_vect = []                                       #instantiate a list to hold the GloVe vectors of all the key words
    
    
    #write vector file to dict
    with open(vector_file,'r') as vector_txt:                           #open the file
        vectors_and_key = vector_txt.readlines()                        #read each line into vector and key list
    for line in vectors_and_key:                                        #for each line in list
        vector = line.split(" ")                                        #split at each space
        word = vector[0]                                                #the first entry of each line is the word in question
        del vector[0]                                                   #remove the word from the line, so that the rest of the line can be interpreted as a list of numbers
        dict_entry = {}                                                 #create dictionary to hold word and vector
        dict_entry[word] = map(float,vector)                            #map the rest of the line into a list of floats and place them under the word as a key
        vector_lenght = 0.                                              #instantiate vector length, which will be used to normalize each vector
        for i in range(dimms):                                          #for each entry in the vector
            vector_lenght += dict_entry[word][i]**2.                    #add the square of that entry
        vector_lenght = vector_lenght**(.5)                             #take the root of that sum, which gives the length of the vector
        for i in range(dimms):                                          #for each dimmension
            dict_entry[word][i] = dict_entry[word][i]/vector_lenght     #divide entry by the vector length (normalize)
        vector_dict.append(dict_entry)                                  #append each unit vector to the vector list
    
    #find keywords in the vector file
    for i in range(len(keywords)):                          #for each keyword
        for words in vector_dict:                           #for each word
            if keywords[i] in words:                        #if the keyword is the current word
                if not words[keywords[i]] in key_vect:      #if the keyword is also not already in the list of keyword vectors
                    key_vect.append(words[keywords[i]])     #add the vector of the keyword to the key vector list
                    break                                   #break and go to next keyword

    synonyms_list = []                                                                                      #reset the synonyms list
    maximum = 0.
    for words in vector_dict:                                                                               #go through all words
        cosine_similarity_good = np.dot(key_vect[0],words[next(iter(words))])                               #get cosine similarity
        cosine_similarity_bad = np.dot(key_vect[1],words[next(iter(words))])                                #get cosine similarity
        if cosine_similarity_good > 0 and cosine_similarity_bad > 0:
            cosine_similarity = cosine_similarity_good/cosine_similarity_bad
            if cosine_similarity > maximum:
                maximum = cosine_similarity
        if cosine_similarity > 0:
            synonyms_list.append([next(iter(words)),cosine_similarity])                                     #add word to list of synonyms
            print(str(next(iter(words)))+ ": Cosine Similarity: ", cosine_similarity)                       #print the cosine similarity of each synonym
    for i in range(len(synonyms_list)):
        synonyms_list[i][1] /= maximum
    synonyms_dict['dct'] = synonyms_list                                                                    #append that dictionary to the synonyms dictionary
    
    return synonyms_dict    #return the synonyms

