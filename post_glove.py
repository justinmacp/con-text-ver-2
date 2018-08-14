from utils import *
'''
    Post processing: employing the GloVe algorithm
'''
keywords = ['plot','character','theme','dialogue','style']
vector_file = 'vectors.txt'
output_file = 'Pre_Post_Processing/synonyms.json'
sentiment_file = 'dict4.json'
dimmensions = 300
threshold = 0.4
threshold_sent = 0.5
sentiment_words = ['good','bad']

print("Creating the synonyms dictionary")
synonyms_dict = create_cluster(keywords,vector_file,dimmensions,threshold)
with open(output_file,'w') as json_out:
    json.dump(synonyms_dict,json_out)

#print("Creating the sentiment dictionary")
#sentiment_dict = create_cluster(sentiment_words,vector_file,dimmensions,threshold_sent)
#with open(sentiment_file,'w') as json_out:
#    json.dump(sentiment_dict,json_out)

