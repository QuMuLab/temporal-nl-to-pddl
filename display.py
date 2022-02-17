class Display:

    def printDic(dic):
        if dic: #not empty
            for key in dic:
                print(key)
                for ls in dic[key]:
                    #print("Next list (similarity with next annot):")
                    print(ls) 
                print('\n')

    def printSentInfo(sent):
        print("Text: %s", getattr(sent,'text')) 
        links = getattr(sent,'links')
        if links != None:
            for num in links:
                print("Link: %s", num)

    def printSentenceDic(dic):
        if dic: #not empty
            for key in dic:
                print("Key: %i", key)
                Display.printSentInfo(dic[key]) 
                print('\n')
        else: 
            print("Dictionary is empty")
