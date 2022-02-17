import fileReader
import model
from display import Display
from keywords import Keywords
from sentenceProcessor import Sentence

def main():
    print("Running main...")
    trained = False
    numFiles = 1
    files = ['TextEdit/Load Truck.txt']
    sentences = []
    print("Finding annotation data...")
    if trained:
        # find json file with sentence dictionaries
        pass
    else: 
        for i in range(0,numFiles):
            sentence = fileReader.fileTest(files[i])
            #Display.printDic(sentences)
            Display.printSentenceDic(sentence)
            #sentences.append(sentence) # returns a list of sentence objects
    print("Data loaded.")
    print("Finding keywords...")
    for i in range(0,2):
        id = '00' + str(i)
        words = Keywords.findKeywords(sentence, id, [], [])
    print("WORDS:")
    print(words)
    wordCountDic = Keywords.countWords(words)
    #Display.printSentenceDic(wordCountDic)
    print("WORDCOUNTDIC:")
    for key in wordCountDic:
        print(key)
        print(wordCountDic[key])
    params = Keywords.getParams('')
    keywords = Keywords.getKeywords(wordCountDic, params)
    print("Printing keywords...")
    for key in keywords:
        print(key)
        print(wordCountDic[key])
    print("Acquiring input natural language text...")
    input = "Dummy input"
    model.runModel(input, sentences)

if __name__ == '__main__':
    main()
    
