import fileReader

class Data:

    actions = fileReader.FileReader.getActions()
    params = fileReader.FileReader.getParams()
    preds = fileReader.FileReader.getPreds()
    similarities = fileReader.FileReader.getSimilarities()
