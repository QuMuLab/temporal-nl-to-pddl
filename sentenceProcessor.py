from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from display import Display
import nltk

class Sentence:
    def __init__(sentence, text, id, links):
        sentence.text = text
        sentence.id = id # first number is the domain, second number is the annotation number, third number is the sentence number within the annotation
        sentence.links = links # a group number for similar sentences (the groups are numbered based on the order of sentences in the first annotation)

class SentenceProcessor:

    # Check the similarity between a sentence and a list of other sentences using cosine similarity
    def checkSim(sentence, others):
        model = SentenceTransformer('bert-base-nli-mean-tokens')
        list = [sentence]
        for sent in others:
            list.append(sent)
        sentence_embeddings = model.encode(list)
        #print(sentence_embeddings.shape)
        sim = cosine_similarity([sentence_embeddings[0]], sentence_embeddings[1:])
        #print(sim)
        return sim

    def tokenize(annot):
        annot = nltk.sent_tokenize(annot)
        return annot

    # Use NLTK to tokenize (break up into a list of sentences) each annotation
    def tokenizeAll(annotLs):
        for i in range(0,5):
            print("Annotation",i)
            print(annotLs[i])
            annotLs[i] = SentenceProcessor.tokenize(annotLs[i])
        return annotLs

     #tokenize sentences
    def getPossibleParamsandPreds(sentence, POS):
        #sentence = nltk.sent_tokenize(sentence)
         #empty to array to hold all nouns
        sentence = sentence.replace('.','')
        sentence = sentence.replace(',','')
        words = []
        if POS == 'params':
            for word,pos in nltk.pos_tag(nltk.word_tokenize(str(sentence))):
                if (pos == 'NN' or pos == 'NNP' or pos == 'NNS' or pos == 'NNPS'):
                    #words.append(word+" ("+pos+")")
                    words.append(word)
        elif POS == 'preds':
            for word,pos in nltk.pos_tag(nltk.word_tokenize(str(sentence))):
                if (pos == 'JJ' or pos == 'JJR' or pos == 'JJS' or pos == 'IN' or pos == 'RBR' or pos == 'RBS' or pos == 'VBD' or 'VBG' or pos == 'VBN' or pos == 'VBZ'):
                    #words.append(word+" ("+pos+")")
                    words.append(word)
        return words
    
    # Create a new dictionary based on the input dictionary where each key in the new dictionary
    # holds the indices corresponding to sentences with the highest similarity the key sentence 
    def getGroups(dic):
        newDic = {}
        for key in dic:
            #print(key)
            newLs = []
            for ls in dic[key]:
                for innerLs in ls:
                    highest = 0
                    index = 0
                    highestIndex = 0
                    for num in innerLs:
                        if num > highest:
                            highest = num
                            highestIndex = index
                        index += 1
                    newLs.append(highestIndex)  
            newDic[key] = newLs 
        return newDic

    # For each sentence in the index dictionary created by getGroups(), create a sentence object
    # that holds the text, id, and links for the sentence. Store these sentences in a dictionary
    # and return the dictionary
    def createSentenceObjects(indexDic, fileNum):
        #Display.printDic(indexDic)
        sentenceNum = 0
        prevNum = 0
        annotNum = 0
        sentences = {}
        for key in indexDic:
            prevNum = annotNum
            annotNum = 5 - len(indexDic[key]) # important line
            if (annotNum != prevNum):
                sentenceNum = 0
            count = 0
            for num in indexDic[key]:
                (indexDic[key])[count] = str(fileNum) + str(count + annotNum + 1) + str(num)
                count += 1
            id = str(fileNum) + str(annotNum) + str(sentenceNum)
            #print("Id: %s", id)
            #print("Key %s", key)
            #print("Links: %s", indexDic[key])
            #print(": %s", indexDic[key])
            sentences[id] = Sentence(key, [fileNum, annotNum, sentenceNum], indexDic[key])
            sentenceNum += 1
        return sentences

    # Takes a list of annotations, and returns a dictionary storing lists of similarity scores
    # for each sentence in that annotation
    def createSimilarityDic(annot):
        #Display.printSentenceDic(annot)
        similarityDic = {}
        for i in range(0,5):
            for sentence in annot[i]:
                newLs = []
                if (i == 4):
                    similarityDic[sentence] = newLs
                else:
                    for j in range(i+1,5):
                        newLs.append(SentenceProcessor.checkSim(sentence, annot[j]))
                        similarityDic[sentence] = newLs
        return similarityDic

    # Takes a dictionary of sentence objections and alters the dictionary so that if sentence
    # A contains a link to sentence B, sentence B also contains a link to sentence A
    def createReverseLinks(sentences):
        for id in sentences:
            links1 = getattr(sentences[id],'links')
            if links1 != None:
                for num in links1:
                    #print("Num: %s, ID: %s, Int Num: %s, Int ID: %s", num, id, int(num), int(id))
                    if int(num) > int(id) and sentences.get(num) != None :
                        links2 = getattr(sentences[num],'links')
                        if links2 == None:
                            ls = []
                            ls.append(id)
                            setattr(sentences[num],'links',ls)
                        else:
                            links2.append(id)
                            setattr(sentences[num],'links', links2)
