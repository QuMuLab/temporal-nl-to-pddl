import json
import nltk
import sys
import keywords
from sentenceProcessor import SentenceProcessor
from display import Display

# Read annotations from a single text file and return the annotations
def getAnnotations(filePath):
    file = open(filePath)
    annot = []
    annot.append(file.readline(-1))
    for i in range(0,6):
        blank = file.readline(-1)
        annot.append(file.readline(-1))
    file.close()
    return annot

# Use NLTK to tokenize (break up into a list of sentences) each annotation
def tokenize(annot):
    for i in range(0,6):
        print("Next line:")
        print(annot[i])
        annot[i] = nltk.sent_tokenize(annot[i])
        print(annot[i])
    return annot

# Read and tokenize annotations from text file, create sentence objects with links between 
# similar sentences
def fileTest(filePath):
    annot = tokenize(getAnnotations(filePath))
    similarityDic = SentenceProcessor.createSimilarityDic(annot)
    print("SIMILARITY DIC:")
    Display.printDic(similarityDic)
    indexDic = SentenceProcessor.getGroups(similarityDic)
    print("INDEX DIC:")
    Display.printDic(indexDic)
    sentences = SentenceProcessor.createSentenceObjects(indexDic, 0)
    #Display.printSentenceDic(sentences)
    #SentenceProcessor.createReverseLinks(sentences)
    #Display.printSentenceDic(sentences)
    return(sentences)
