import nltk
import pickle
from sklearn.metrics.pairwise import cosine_similarity

class SentenceProcessor:

    # Check the similarity between a sentence and a list of other sentences using cosine similarity
    def checkSim(inputEmbedding, others, actionNum, annotNum):
        path = 'Desktop/TempNLtoPDDL/Embeddings/action' + str(actionNum) + '/embeddings' + str(annotNum) + '.xml'
        file = open(path, 'rb')
        sentence_embeddings = pickle.load(file)
        print(sentence_embeddings)
        sim = cosine_similarity(inputEmbedding, sentence_embeddings)
        return sim

    def getPossibleParamsandPreds(sentence, type):
        sentence = sentence.replace('.','')
        sentence = sentence.replace(',','')
        words = []
        if type == 'params':
            for word,pos in nltk.pos_tag(nltk.word_tokenize(str(sentence))):
                if (pos == 'NN' or pos == 'NNP' or pos == 'NNS' or pos == 'NNPS'):
                    words.append(word)
        elif type == 'preds':
            for word,pos in nltk.pos_tag(nltk.word_tokenize(str(sentence))):
                if (pos == 'JJ' or pos == 'JJR' or pos == 'JJS' or pos == 'IN' or pos == 'RBR' or pos == 'RBS' or pos == 'VBD' or 'VBG' or pos == 'VBN' or pos == 'VBZ'):
                    words.append(word)
        return words
