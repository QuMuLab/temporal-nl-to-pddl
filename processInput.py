import data
import sentenceProcessor


similarityDic = {}
actions = []
ls1 = []
ls1.append('loadTruck')
ls1.append('changeColor')
ls1.append('movecurbtocurb')
ls1.append('untrap')
ls1.append('LIGHT_MATCH')
ls1.append('lift')
ls1.append('movevehicleroad')
ls1.append('switchon')

# Removes the parenthesese and question marks from a line of PDDL code,
# and returns the modified line of code.
def translate(codeLine):
    codeLine = codeLine.replace("(","")
    codeLine = codeLine.replace(")","")
    codeLine = codeLine.replace("?","")
    return codeLine

# Takes a sentence from the database, a line of PDDL code that is supposed to 
# represent some or all what is described by the sentence, lists holding
# the parameters and predicates in the sentence, and an integer corresponding
# to the position of this part of the prompt relative to the other parts.
def makePrompt(sentence, codeLine, params1, preds1, promptNum):
    paramCount = 1
    for ls in params1:
        for param in ls:
            codeLine = codeLine.replace(param,"param"+str(promptNum)+str(paramCount))
            sentence = sentence.replace(param,"param"+str(promptNum)+str(paramCount))
        paramCount += 1
    predCount = 1
    for ls in preds1:
        for pred in ls:
            codeLine = codeLine.replace(pred,"pred"+str(promptNum)+str(predCount))
            sentence = sentence.replace(pred,"pred"+str(promptNum)+str(predCount))
        predCount += 1
    prompt = sentence + '\n' + codeLine + '\n'
    return prompt

# Takes a list holding information about the sentences in the database that are similar to
# the input sentence, and the input sentence itself. Returns a list of partial prompts that
# are created using the 'makePrompt' function, based on the information stored in the 
# 'matches' list.
def getPrompts(matches, inputSentence):
    prompts = []
    matchCount = 0
    for match in matches:
        actionNum = match[0]
        actionName = ls1[actionNum]
        annotNum = match[1]
        sentenceNum = match[2]
        matchValue = match[3]
        actionName = ls1[actionNum]
        action = data.Data.actions[actionName]
        annots = action[1]
        annot = sentenceProcessor.SentenceProcessor.tokenize(annots[annotNum])
        sentence = annot[sentenceNum]
        print(sentence)
        conditionValue = 0
        effectValue = 0
        for i in range(0,2):
            name = ''
            if i == 0: # check 'condition' similarities
                name = actionName + 'Condition'
                sims = data.Data.similarities[actionName][0]
                conditionValue = (sims[annotNum])[sentenceNum]
            else: # check 'effect' similarities
                name = actionName + 'Effect'
                sims = data.Data.similarities[actionName][1]
                effectValue = (sims[annotNum])[sentenceNum]
        if effectValue > conditionValue:
            type = 'effect'
        else:
            type = 'condition'
        actionCode = (data.Data.actions[actionName])[0]
        codeLine = actionCode[type]
        params1 = data.Data.params[actionName]
        preds1 = data.Data.preds[actionName]
        prompt = makePrompt(sentence, inputSentence, codeLine, params1, [['pickle'], ['jar']], preds1, [['on top']], matchCount)
        prompts.append(prompt)
        matchCount += 1
    return prompts

def findSimilarities(code, annots):
    brokenEnglish = translate(code['condition'])
    for i in range(0,5):
        tokenizedAnnot = sentenceProcessor.SentenceProcessor.tokenize(annots[i])
        sim = sentenceProcessor.SentenceProcessor.checkSim(brokenEnglish, tokenizedAnnot)
        #print("Similarities:")
        print(sim)
        #print(sim)
    return sim

def findSimilarities2(inputText, annot, name):
    annot = replaceParamsandPreds(annot, data.Data.params[name], data.Data.preds[name], 0)
    tokenizedAnnot = sentenceProcessor.SentenceProcessor.tokenize(annot)
    sim = sentenceProcessor.SentenceProcessor.checkSim(inputText, tokenizedAnnot)
    #print("Similarities:")
    print(sim)
    #print(sim)
    return sim

def printSimilarity(actionName, lineName, annotName):
    if actionName == 'loadTruck':
        action = actions[0]
        if lineName == 'condition':
            codeLine = action.condition
            if annotName == 'annot1Sims':
                print(codeLine.annot1Sims)
    #similarityLs = similarityDic[code][codeLine]
    #similarityLs = similarityDic[codeLine]
    #print(similarityLs)

# Takes an input string representing a piece of natural language text,
# a list of parameters and a list of predicates found in that text, 
# and an integer that corresponds to the position of this particular piece 
# of text relative to the others that are found in the same prompt.
# Returns the same text but with the parameters and predicates replaced
# by the strings 'paramXX' and 'predXX' where the 'X's are integers 
def replaceParamsandPreds(text, params, preds, num):
    paramCount = 0
    for ls1 in params:
        for param in ls1:
            text = text.replace(param,"param"+str(num)+str(paramCount))
        paramCount += 1
    predCount = 0
    for ls2 in preds:
        for pred in ls2:
            text = text.replace(pred,"pred"+str(num)+str(predCount))
        predCount += 1
    return text 

# Reverses the effects of the 'replaceParamsandPreds' function.
# To be used on the output of a GPT3 call in order to obtain 
# the proper PDDL code result.
def replaceReverse(result, params, preds):
    paramCount = 0
    for ls1 in params:
        for param in ls1:
            result = result.replace("param0"+str(paramCount),param)
        paramCount += 1
    predCount = 0
    for ls2 in preds:
        for pred in ls2:
            result = result.replace("pred0"+str(predCount),pred)
        predCount += 1
    return result

# Takes a string representing the input and checks the similarity (cosine similarity) of the sentence
# with all other sentences in the database. The location (indices) of the sentences with similarities 
# above a certain threshold are stored in a list called 'matches', which is returned at the end.
def testInputSim(inputSentence):
    inputSentence = replaceParamsandPreds(inputSentence, [['pickle'], ['jar']], [['on top']], 0)
    matches = []
    for i in range(0,8):
        name = ls1[i]
        ls = data.Data.actions[name]
        annots = ls[1]
        for j in range(0,5):
            sims = findSimilarities2(inputSentence, annots[j], name)
            count = 0
            for simMetric in sims[0]:
                if simMetric > 0.9:
                    matches.append([i, j, count, simMetric])
                count += 1    
    print("Matches: ")
    print(matches)
    return matches

def main():
    inputText = input("Type or paste in natural language that describes a durative action in PDDL.")
    #inputText = "At the start, the pickle is on top of the jar."
    print("Here are some possible parameters:")
    possibleParams = sentenceProcessor.SentenceProcessor.getPossibleParamsandPreds(inputText, 'params')
    count = 0
    for param in possibleParams:
        print(str(count)+": "+possibleParams[count])
        count += 1
    print("Select the parameters by typing the corresponding number...")
    params = []
    doneSelection = False
    while(not doneSelection):
        num = input()
        print("You have selected '"+possibleParams[int(num)]+"'")
        params.append([possibleParams[int(num)]])
        print("Would you like to select another parameter?")
        decision = input("Enter 'y' or 'n'")
        if decision != 'y':
            doneSelection = True
        else:
            print("Type another number to select another parameter...")
    print("Parameter selection complete.")
    print("The parameters are: ")
    print(params)
    #possiblePreds = ['on top', 'inside']
    possiblePreds = sentenceProcessor.SentenceProcessor.getPossibleParamsandPreds(inputText, 'preds')
    print("Here are some possible predicates:")
    count = 0
    for pred in possiblePreds:
        print(str(count)+": "+possiblePreds[count])
        count += 1
    print("Select the predicates by typing the corresponding number...")
    preds = []
    doneSelection = False
    while(not doneSelection):
        num = input()
        print("You have selected '"+possiblePreds[int(num)]+"'")
        preds.append([possiblePreds[int(num)]])
        print("Would you like to select another predicate?")
        decision = input("Enter 'y' or 'n'")
        if decision != 'y':
            doneSelection = True
        else:
            print("Type another number to select another predicate...")
    print("Predicate selection complete.")
    print("The predicates are: ")
    print(preds)
    print("Generating GPT3 prompt (this could take a few minutes).")
    #params = input("Type or paste in natural language that describes a durative action in PDDL.")
    #input = "At the start, the pickle is on top of the jar."
    matches = testInputSim(inputText)
    prompts = getPrompts(matches, inputText)
    print("Use the following text as input to GPT3.")
    for prompt in prompts:
        print(prompt)
    inputText = replaceParamsandPreds(inputText, params, preds, 0)
    print(inputText)
    print("\n")
    result = input("Paste the first line of the GPT3 output here:")
    fixedResult = replaceReverse(result, params, preds)
    print(fixedResult)
        
main()
