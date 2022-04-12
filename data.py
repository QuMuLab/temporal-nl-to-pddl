import fileReader

# This class holds all of the data used by the model
class Data:

    actions = fileReader.FileReader.getActions()
    params = fileReader.FileReader.getParams()
    preds = fileReader.FileReader.getPreds()
    similarities = fileReader.FileReader.getSimilarities()
