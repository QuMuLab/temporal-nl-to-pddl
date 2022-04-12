import processInput
import sentenceProcessor
import postProcessor
import nltk
from sentence_transformers import SentenceTransformer

# This file provides code to demonstrate the model in action.

def main():
    model = SentenceTransformer('bert-base-nli-mean-tokens')
    nlText = input("Type or paste in natural language that describes a durative action in PDDL.")
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
        addedLs = False
        try:
            ls = eval(num)
            if isinstance(ls, list):
                string = ''
                for num in ls:
                    string += possibleParams[int(num)]
                    string += ' '
                print("You have selected '"+string+"'")
                params.append([string])
                addedLs = True
        except SyntaxError:
            pass
        if not addedLs:
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
    nlText = processInput.ProcessInput.replaceParamsandPreds(nlText, params, preds, 0)
    inputLs = nltk.sent_tokenize(nlText)
    duration = '0'
    for inputText in inputLs:
        if (processInput.ProcessInput.checkDuration(inputText)):
            for word in inputText.split():
                modWord = word.replace(",","")
                modWord = modWord.replace(".","")
                if (modWord.isdigit()):
                    duration = modWord
        if processInput.ProcessInput.hasPred(inputText):
            print("Generating GPT3 prompt (this could take a few minutes).")
            matches = processInput.ProcessInput.testInputSim(inputText, model)
            prompts = processInput.ProcessInput.getPrompts(matches)
            print("Use the following text as input to GPT3:\n")
            for prompt in prompts:
                print(prompt)
            print('NL: '+inputText+' '+inputText+' '+inputText)
            print('PDDL: ')
            print("\n")
            result = input("Paste the first line of the GPT3 output here:")
            result = postProcessor.PostProcessor.listify(result)
            result = eval(result)
            if isinstance(result, list):
                result = postProcessor.PostProcessor.removeIrrelevantCode(result, inputText, params, preds)
                for code in result:
                    code = processInput.ProcessInput.replaceReverse(code, params, preds)
                    code = code.replace("? ", "?")
                    code = code.replace("?", " ?")
                    print("The following line of code has been generated:\n")
                    print(code)
                    print("\n")
                    print("Select whether the above line of code is a condition or an effect.")
                    print("1: condition")
                    print("2: effect")
                    print("3: neither")
                    type = input()
                    if (type == '1'):
                        conditions.append(code)
                    elif (type == '2'):
                        effects.append(code) 
                    elif (type == '3'):
                        pass
            else:
                print("Error: Could not create list")
    name = input("What would you like to call this action?")
    processInput.ProcessInput.printPDDL(name, params, duration, conditions, effects) 

main()