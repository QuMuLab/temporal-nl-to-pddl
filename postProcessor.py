# This class provides methods to process the output of the LLM before it is returned to the user.
class PostProcessor:

    # takes a PDDL condition or effect statement and makes it into a string that can be converted to
    # a list using the 'eval' function
    def listify(result):
        result = "['" + result + "']"
        result = result.replace("['(and ","['")
        result = result.replace(")'] ","']")
        result = result.replace(")) ","))', '")
        result = result.replace(", ]","]")
        return result

    # returns a list of indices, where each index corresponds to an item in the list
    # of code segments that contains a predicate which is not present in the input text.
    def checkPreds(codeLs, inputText, preds):
        indices = []
        count = 0
        for code in codeLs:
            predCount = 0
            for ls in preds:
                string = "pred0"+str(predCount)
                if (string in code) and (string not in inputText):
                    indices.append(count)
                predCount += 1
            count += 1
        return indices

    # returns a list of indices, where each index corresponds to an item in the list of 
    # code segments that does not have correct PDDL syntax
    def checkSyntax(codeLs, params, preds):
        count = 0
        indices = []
        for code in codeLs:
            code = '0' + code
            code = code.replace("(","+1")
            code = code.replace(")","-1")
            predCount = 0
            for ls in preds:
                string = "pred0"+str(predCount)
                code = code.replace(string,"+1")
                predCount += 1
            code = code.replace("?","/")
            paramCount = 0
            for ls in params:
                string = "param0"+str(paramCount)
                code = code.replace(string,"1")
                paramCount += 1
            code = code.replace("at start","")
            code = code.replace("at end","")
            code = code.replace("over all","")
            code = code.replace("not","")
            code = code.replace("?","?")
            correctSyntax = False
            try:
                num = eval(code)
                if int(num):
                    if (num == 1):
                        correctSyntax = True # correct syntax
                    else:
                        correctSyntax = True # incorrect number of brackets, but this is ignored
            except (SyntaxError, NameError):
                pass
            if not correctSyntax:
                indices.append(count)
            count += 1
        return indices

    # modifies the list of code segments so that it cotains only those segments with
    # predicates that are present in the input, and that have correct syntax
    def removeIrrelevantCode(codeLs, inputText, params, preds):
        indices1 = PostProcessor.checkPreds(codeLs, inputText, preds)
        indices1.sort(reverse=True)
        for ind in indices1:
            if ind < len(codeLs):
                codeLs.pop(ind)
        indices2 = PostProcessor.checkSyntax(codeLs, params, preds)
        indices2.sort(reverse=True)
        for ind in indices2:
            if ind < len(codeLs):
                codeLs.pop(ind)
        return codeLs
