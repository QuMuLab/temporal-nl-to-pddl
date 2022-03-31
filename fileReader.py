import pickle

class FileReader:

    def getObj(fileName):
        path = 'Desktop/TempNLtoPDDL/Data/' + fileName + '.xml'
        file = open(path, 'rb')
        obj = pickle.load(file)
        return obj

    def getAnnot(num):
        fileName = 'annot' + str(num)
        return FileReader.getObj(fileName)
        
    def getActions():
        fileName = 'actions'
        return FileReader.getObj(fileName)

    def getParams():
        fileName = 'params'
        return FileReader.getObj(fileName)

    def getPreds():
        fileName = 'preds'
        return FileReader.getObj(fileName)

    def getSimilarities():
        fileName = 'similarities'
        return FileReader.getObj(fileName)
