import json, unicodedata, collections, ast, timeit
from jsonrpc import ServerProxy, JsonRpc20, TransportTcpIp
from pprint import pprint

tic = timeit.default_timer()
# StanfordNLP class instantiates default constructor 
class StanfordNLP:
    def __init__(self):
        self.server = ServerProxy(JsonRpc20(),
                                  TransportTcpIp(addr=("127.0.0.1", 8080)))
    
    def parse(self, text):
        return json.loads(self.server.parse(text))

nlp = StanfordNLP()


##################### For investigative purposes, please ignore this commented out blob #####################
# print type(data_refined) #Prints the data type of object data_refined. In this case it is a list of dictionaries
# print len(data_refined) #Prints how many sentences are in list data_refined. In this json file, there are 2 sentences.
# print data_refined[1] #Prints one of the sentences in list data_refined. 
# print type(data_refined[1]) #Prints the data type of that particular object within the list. That particular objecet is of type dictionary.
# pprint(nlp.parse(data_refined[1]['sentence'])) #Prints stanford dependency tree of that particular object
with open('dataout.txt', 'r') as sentences:
    data = sentences.read()   
    data_refined = ast.literal_eval(data) # Load all data in 'review'

#print type(data_refined)

##################### To view unfiltered NLP JSON dictionary & save it to a JSON file #####################
output_json = {}
for index in range(len((data_refined))):
    sentence_value = data_refined[index]
    output_json[index] = nlp.parse(sentence_value)

#print type(output_json[index])
pprint(output_json) 
with open('./outfile.json', 'w') as object:
    json.dump(output_json, object, indent = 4, ensure_ascii = True)


##################### To filter out unwanted keys, and pass on the parsetree & dependencies subkeys #####################
##################### To print & save filtered out dictionary into JSON file #####################
# variable i: The OUTER index of the list item output_json (which is a list of dictionaries)
# variable j: Iterating over HIGH LEVEL nlp response keys (which are coref & sentences). You are now in particular object (dictionary) of the list.
# variable inner_dict: This is a list of length 1. You are getting the objects inside that list (basically 1 row x 4 columns)
# Variable k: This variable goes over the four columns mentioned in the previous sentence (parsetree, text, dependencies, & words). You only care about parsetree & dependencies.
required_dict = {}
for i in output_json:
    response_dict = output_json[i]
    for j in response_dict:
        if('sentences' in j):
            inner_dict = response_dict[j][0]
            required_dict[i] = {}
            for k in inner_dict:
                if('dependencies' in k):
                    required_dict[i]['dependencies'] = inner_dict['dependencies']
                elif('words' in k):
                    required_dict[i]['words'] = inner_dict['words']

print('##################################### RESULTS #########################################')
pprint(required_dict)
print('#######################################################################################')
toc = timeit.default_timer()
print('This is how long the processing takes: ' +str(toc-tic))
print('#######################################################################################')
ticc = timeit.default_timer()
with open('./parsed_and_filtered_out_sentences.json', 'w') as o:
    json.dump(required_dict, o, indent = 4, ensure_ascii = True)
tocc = timeit.default_timer()
print('This is how long the storing takes: ' +str(tocc-ticc))
