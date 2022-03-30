import data
import sentenceProcessor
import nltk
from sentence_transformers import SentenceTransformer

num_actions = 7
names = ['loadTruck', 'changeColor', 'movecurbtocurb', 'untrap', 'LIGHT_MATCH', 'lift', 'movevehicleroad', 'switchon']
durationWords = ['duration', 'takes', 'lasts']

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
    values = []
    matchCount = 0
    for match in matches:
        actionNum = match[0]
        actionName = names[actionNum]
        annotNum = match[1]
        sentenceNum = match[2]
        matchValue = match[3]
        actionName = names[actionNum]
        action = data.Data.actions[actionName]
        annots = action[1]
        annot = nltk.sent_tokenize(annots[annotNum])
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
        value = 0.0
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
        prompt = makePrompt(sentence, codeLine, params1, preds1, matchCount)
        prompts.append(prompt)
        matchCount += 1
    avg = 0
    if len(values) > 0:
        avg = sum(values) / len(values)
    print("AVG VALUE: "+str(avg))
    if avg < 0.4:
        prompts = []
    return prompts

def findSimilarities(inputEmbedding, annot, name, actionNum, annotNum):
    annot = replaceParamsandPreds(annot, data.Data.params[name], data.Data.preds[name], 0)
    tokenizedAnnot = nltk.sent_tokenize(annot)
    sim = sentenceProcessor.SentenceProcessor.checkSim(inputEmbedding, tokenizedAnnot, actionNum, annotNum)
    return sim

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
            result = result.replace("param0"+str(paramCount)," "+param)
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
def testInputSim(inputSentence, model):
    input_embedding = model.encode([inputSentence])
    matches = []
    for i in range(0,num_actions):
        name = names[i]
        ls = data.Data.actions[name]
        annots = ls[1]
        for j in range(0,5):
            sims = findSimilarities(input_embedding, annots[j], name, i, j)
            count = 0
            for simMetric in sims[0]:
                if simMetric > 0.7:
                    matches.append([i, j, count, simMetric])
                count += 1    
    return matches

# Example usage: printPDDL('movePickle', [['pickle'], ['jar']], [['top']], 5, ['(and (at start (on ?pickle ?jar))'], ['(and (at end (in ?pickle ?jar))'])
def printPDDL(name, params, preds, duration, conditions, effects):
    print("(:durative-action "+name)
    print("    :parameters")
    print("        (")
    for ls in params:
        print("        ?"+ls[0])
    print("        )")
    print("    :duration")
    print("        (= ?duration " + duration + ")")
    print("    :condition")
    for condition in conditions:
        print("        "+condition)
    print("    :effect")
    for effect in effects:
        print("        "+effect)
    print(")")

# checks whether the sentence contains a word associated with a duration statement (i.e. a word in 'durationWords')
def checkDuration(sentence):
    found = False
    for word in durationWords:
        if word in sentence:
            found = True
    return found

def main():
    model = SentenceTransformer('bert-base-nli-mean-tokens')
    nlText = input("Type or paste in natural language that describes a durative action in PDDL.")
    inputLs = nltk.sent_tokenize(nlText)
    conditions = []
    effects = []
    print("Here are some possible parameters:")
    possibleParams = sentenceProcessor.SentenceProcessor.getPossibleParamsandPreds(nlText, 'params')
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
    possiblePreds = sentenceProcessor.SentenceProcessor.getPossibleParamsandPreds(nlText, 'preds')
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
    for inputText in inputLs:
        if (checkDuration(inputText)):
            for word in inputText.split():
                modWord = word.replace(",","")
                modWord = modWord.replace(".","")
                if (modWord.isdigit()):
                    duration = modWord
        print("Generating GPT3 prompt (this could take a few minutes).")
        inputText = replaceParamsandPreds(inputText, params, preds, 0)
        matches = testInputSim(inputText, model)
        prompts = getPrompts(matches, inputText)
        if prompts:
            print("Use the following text as input to GPT3.")
            for prompt in prompts:
                print(prompt)
            #inputText = replaceParamsandPreds(inputText, params, preds, 0)
            print(inputText)
            print("\n")
            result = input("Paste the first line of the GPT3 output here:")
            result = replaceReverse(result, params, preds)
            print("Here is the generated code for this sentence:")
            print(result)
            print("Select whether the above line of code is a condition or an effect.")
            print("1: condition")
            print("2: effect")
            print("3: both")
            print("4: neither")
            type = input()
            if (type == '1'):
                conditions.append(result)
            elif (type == '2'):
                effects.append(result) 
            elif (type == '3'):
                pass
            elif (type == '4'):
                pass
    name = input("What would you like to call this action?")
    printPDDL(name, params, preds, duration, conditions, effects)   

main()
