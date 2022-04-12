import data
import sentenceProcessor
import postProcessor
import nltk
from sentence_transformers import SentenceTransformer

# This class provides most of the methods used by the model to process the NL input and generate appropriate PDDL code.
class ProcessInput:
    
    num_matches = 7 # number of annotations used in each prompt
    names = ['loadTruck', 'changeColor', 'movecurbtocurb', 'untrap', 'LIGHT_MATCH', 'lift', 'movevehicleroad', 'switchon'] # action names
    durationWords = ['duration', 'takes', 'lasts'] # words that indicate a duration statement

    # removes the parenthesese and question marks from a line of PDDL code, and returns the 
    # modified line of code
    def translate(codeLine):
        codeLine = codeLine.replace("(","")
        codeLine = codeLine.replace(")","")
        codeLine = codeLine.replace("?","")
        return codeLine

    # takes a sentence from the database, a line of PDDL code that is supposed to represent some 
    # or all what is described by the sentence, lists holding the parameters and predicates in the 
    # sentence, and an integer corresponding to the position of this part of the prompt relative to
    # the other parts
    def makePrompt(text, codeLine, params1, preds1, promptNum):
        paramCount = 1
        for ls in params1:
            for param in ls:
                if param[0] == '?':
                    codeLine = codeLine.replace(param,"<<<?param"+str(promptNum)+str(paramCount)+">>>")
                else:
                    codeLine = codeLine.replace("?"+param,"<<<?param"+str(promptNum)+str(paramCount)+">>>")
                left = codeLine.split("<<<",1)
                right = codeLine.split(">>>",1)
                if len(left) > 1:
                    if ((right[1][0] != ' ') and (right[1][0] != ')')) or (left[0][-1] != ' '):
                        codeLine = codeLine.replace("<<<?param"+str(promptNum)+str(paramCount)+">>>", param) 
                text = text.replace(param,"param"+str(promptNum)+str(paramCount))  
                codeLine = codeLine.replace("<<<","")
                codeLine = codeLine.replace(">>>","")
            paramCount += 1
        predCount = 1
        for ls in preds1:
            for pred in ls:
                codeLine = codeLine.replace(pred,"<<<pred"+str(promptNum)+str(predCount)+">>>")
                left = codeLine.split("<<<",1)
                right = codeLine.split(">>>",1)
                if len(left) > 1:
                    if (right[1][0] != ' ') or (left[0][-1] != '('):
                        codeLine = codeLine.replace("<<<pred"+str(promptNum)+str(predCount)+">>>", pred)
                codeLine = codeLine.replace("<<<","")
                codeLine = codeLine.replace(">>>","")
                text = text.replace(pred,"pred"+str(promptNum)+str(predCount))
            predCount += 1
        text = nltk.sent_tokenize(text)
        indices = []
        count = 0
        for sent in text:
            if not (ProcessInput.hasPred(sent)):
                indices.append(count)
            count += 1
        indices.sort(reverse=True)
        for ind in indices:
            if ind < len(text):
                text.pop(ind)
        string = ''
        for sent in text:
            string += sent 
        prompt = 'NL: ' + string + '\n' + 'PDDL: ' + codeLine + '\n'
        return prompt

    # returns 'True' if the sentence contains a predicate, and 'False' otherwise
    def hasPred(sentence):
        val = False
        if 'pred' in sentence:
            val = True
        return val

    # takes a list holding information about the sentences in the database that are similar to
    # the input sentence, and the input sentence itself. Returns a list of partial prompts that
    # are created using the 'makePrompt' function, based on the information stored in the 
    # 'matches' list
    def getPrompts(matches):
        prompts = []
        values = []
        matchCount = 0
        for match in matches:
            actionNum = match[0]
            actionName = ProcessInput.names[actionNum]
            annotNum = match[1]
            sentenceNum = match[2]
            actionName = ProcessInput.names[actionNum]
            action = data.Data.actions[actionName]
            annots = action[1]
            conditionValue = 0
            effectValue = 0
            for i in range(0,2):
                if i == 0: # check 'condition' similarities
                    sims = data.Data.similarities[actionName][0]
                    conditionValue = (sims[annotNum])[sentenceNum]
                else: # check 'effect' similarities
                    sims = data.Data.similarities[actionName][1]
                    effectValue = (sims[annotNum])[sentenceNum]
            value = 0
            if effectValue > conditionValue:
                value = effectValue
                type = 'effect'
            else:
                value = conditionValue
                type = 'condition'
            values.append(value)
            actionCode = (data.Data.actions[actionName])[0]
            codeLine = actionCode[type]
            params1 = data.Data.params[actionName]
            preds1 = data.Data.preds[actionName]
            prompt = ProcessInput.makePrompt(annots[annotNum], codeLine, params1, preds1, matchCount)
            prompts.append(prompt)
            matchCount += 1
        return prompts

    # returns the cosine similarities obtained via the 'checkSim' function, after replacing
    # the parameters and predicates in the annotation
    def findSimilarities(inputEmbedding, annot, name, actionNum, annotNum):
        annot = ProcessInput.replaceParamsandPreds(annot, data.Data.params[name], data.Data.preds[name], 0)
        tokenizedAnnot = nltk.sent_tokenize(annot)
        sim = sentenceProcessor.SentenceProcessor.checkSim(inputEmbedding, tokenizedAnnot, actionNum, annotNum)
        return sim

    # takes an input string representing a piece of natural language text, a list of parameters 
    # and a list of predicates found in that text, and an integer that corresponds to the position
    # of this particular piece of text relative to the others that are found in the same prompt.
    # Returns the same text but with the parameters and predicates replaced by the strings 'paramXX'
    # and 'predXX' where the 'X's are integers 
    def replaceParamsandPreds(text, params, preds, num):
        paramCount = 0
        for ls1 in params:
            for param in ls1:
                text = text.replace(" "+param+" "," param"+str(num)+str(paramCount)+" ")
                text = text.replace(" "+param+","," param"+str(num)+str(paramCount)+",")
                text = text.replace(" "+param+"."," param"+str(num)+str(paramCount)+".")
            paramCount += 1
        predCount = 0
        for ls2 in preds:
            for pred in ls2:
                text = text.replace(" "+pred+" "," pred"+str(num)+str(predCount)+" ")
                text = text.replace(" "+pred+","," pred"+str(num)+str(predCount)+",")
                text = text.replace(" "+pred+"."," pred"+str(num)+str(predCount)+".")
            predCount += 1
        return text 

    # reverses the effects of the 'replaceParamsandPreds' function. To be used on the output 
    # of a GPT3 call in order to obtain the proper PDDL code result
    def replaceReverse(result, params, preds):
        paramCount = 0
        for ls1 in params:
            for param in ls1:
                result = result.replace("param0"+str(paramCount)," "+param)
            paramCount += 1
        predCount = 0
        for ls2 in preds:
            for pred in ls2:
                result = result.replace("pred0"+str(predCount),pred)
            predCount += 1
        return result

    # gets the match with the lowest cosine similarity to the input sentence
    def getMin(matches):
        lowest = 1
        lowestInd = 0
        count = 0
        for match in matches:
            if match[3] < lowest:
                lowest = match[3]
                lowestInd = count
            count += 1
        return lowestInd

    # takes a string representing the input and checks the cosine similarity of the sentence with 
    # all other sentences in the database. The indices of the sentences with similarities above a
    # certain threshold are stored in a list called 'matches', which is returned at the end
    def testInputSim(inputSentence, model):
        input_embedding = model.encode([inputSentence])
        matches = []
        for i in range(0,8):
            name = ProcessInput.names[i]
            ls = data.Data.actions[name]
            annots = ls[1]
            for j in range(0,5):
                sims = ProcessInput.findSimilarities(input_embedding, annots[j], name, i, j)
                count = 0
                for simMetric in sims[0]:
                    if (len(matches) < ProcessInput.num_matches):
                        matches.append([i, j, count, simMetric])
                    elif matches:
                        lowestInd = ProcessInput.getMin(matches)
                        lowest = (matches[lowestInd])[3]
                        if simMetric > lowest:
                            matches[lowestInd] = [i, j, count, simMetric]
                    count += 1
        return matches

    # takes the relevant information, and prints the PDDL code for a durative action
    # example usage: printPDDL('movePickle', [['pickle'], ['jar']], 5, 
    # ['(and (at start (on ?pickle ?jar))'], ['(and (at end (in ?pickle ?jar))'])
    def printPDDL(name, params, duration, conditions, effects):
        print("(:durative-action "+name)
        print("    :parameters")
        print("        (")
        for ls in params:
            print("        ?"+ls[0])
        print("        )")
        print("    :duration")
        print("        (= ?duration " + duration + ")")
        print("    :condition")
        print("        (and ")
        for condition in conditions:
            print("        "+condition)
        print("        )")
        print("    :effect")
        print("        (and ")
        for effect in effects:
            print("        "+effect)
        print("        )")
        print(")")

    # checks whether the sentence contains a word associated with a duration statement 
    # (i.e. a word in 'durationWords')
    def checkDuration(sentence):
        found = False
        for word in ProcessInput.durationWords:
            if word in sentence:
                found = True
        return found
