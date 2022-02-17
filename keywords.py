class Keywords:

    commonWords = [
        'the', 
        'of', 
        'and', 
        'a', 
        'to', 
        'in', 
        'is', 
        'you', 
        'that', 
        'it',
        'he',
        'was',
        'for',
        'on',
        'are',
        'as',
        'with',
        'his',
        'they',
        'at',
        'be',
        'this',
        'have',
        'from',
        'or',
        'one',
        'had',
        'by'
    ]

    # sentence is a Sentence object, lookedAt is a list of IDs
    def findKeywords(sentences, id, wordLs, lookedAt):
        text = getattr(sentences[id], 'text')
        links = getattr(sentences[id],'links')
        wordLs.append(text.split())
        lookedAt.append(id)
        print(wordLs)
        for link in links:
            if link not in lookedAt:
                text = getattr(sentences[link], 'text')
                wordLs.append(text.split())
                lookedAt.append(link)
        return wordLs
    
    # Returns a dictionary with words as keys and number of occurances of that word in the 
    # input word list as values
    def countWords(wordLs):
        print("Wordls:")
        print(wordLs)
        dic = {}
        for ls in wordLs:
            for word in ls:
                print("WORD:")
                print(word)
                dic[str(word)] = 0
        for ls in wordLs:
            for word in ls:
                dic[str(word)] = dic[str(word)] + 1
        return dic

    # Returns a dictionary containing keywords as keys and frequency of occurance (as counted 
    # in annotation data) as values
    def getKeywords(wordCountDic, params):
        keywords = {}
        for key in wordCountDic:
            if (key not in params) and (key not in Keywords.commonWords):
                keywords[key] = wordCountDic[key]
        return keywords

    # Returns a list of parameters that have been found in the annotations
    def getParams(params):
        return ['object','truck','location']
