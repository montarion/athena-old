from sklearn import tree
from six import StringIO
import pydotplus
class machinelearning:
    def __init__(self):
        self.datasize = 0
        self.trainingsize = 0
        self.features = []
        self.humanfeatures = {}
        self.inversehumanfeatures = {}
        self.labels = []
        self.getconfirmation = False

        #self.trainingfeatures = [{"colour": "red", "shape": "round", "surface": "glossy"}, {"colour": "green", "shape": "oblong", "surface": "rough"}, {"colour": "green", "shape": "round"}]
        #self.trainingfeatures = [[0, 1, 2], [3, 4, 5], [3, 1, 9999], {'colour': 'green', 'shape': 'square'}]

        self.trainingfeatures = [{'charging': True, 'chargingplug': 'AC', 'batterypercentage': 45, 'lon': 5.2423, 'lat': 52.1029, 'speed': 2, 'name': '"FRITZ!Box Fon WLAN 7360"', 'state': 'CONNECTED', 'type': 'WIFI'}]
        self.traininglabels = ["home"]
        self.trainingfeaturesaslist = []






    def convert(self, dataset, processtype = "predicting"):
        for index, data in enumerate(dataset):
            tmplist = []
            if type(data) == dict:
                for entry in data:
                    value = data[entry]

                    if value not in self.humanfeatures:

                        if processtype == "predicting":
                            print(f"don't know value {value}")
                            # set flag so I know to ask the user about it
                            self.getconfirmation = True
                        newvalue = len(self.humanfeatures)
                        tmplist.append(newvalue)
                        self.humanfeatures[value] = len(self.humanfeatures)
                        self.inversehumanfeatures[len(self.humanfeatures)] = value
                    else:
                        newvalue = self.humanfeatures[value]
                        tmplist.append(newvalue)
                dataset.remove(data)
                dataset.insert(index, tmplist)

        print(dataset)
        print(self.humanfeatures)
        return dataset

    def addtotraining(self, numbertoadd):
        for dataset in self.trainingfeaturesaslist:
            while len(dataset) < numbertoadd:
                dataset.append(9999)

    def normalize(self, dataset, datatype = "normal"):
        if datatype == "normal":
            if len(dataset[0]) > self.trainingsize: # check if new data is larger than training sample(it will be just one set, as a list)
                self.addtotraining(len(dataset[0]))
                self.train("retrain")
        for data in dataset:
            if len(data) > self.datasize:
                self.datasize = len(data)
        for data in dataset:
            while len(data) < self.datasize:
                data.append(9999)

        if datatype == "training":
            self.trainingsize = self.datasize # set training sample size
            self.trainingfeaturesaslist = dataset
        return dataset

    def train(self, processtype = "normal"):
        clf = tree.DecisionTreeClassifier()
        if processtype == "retrain":
            print("retraining!")
            dataset = self.trainingfeaturesaslist # use special dataset that had it's samples updated to the correct size
            print(dataset)
            dataset = self.normalize(dataset, "training")
        else:
            dataset = self.convert(self.trainingfeatures, "training")
            print("Done converting..")
            dataset = self.normalize(dataset, "training")

        self.clf = clf.fit(dataset, self.traininglabels)

    def predict(self, contextinput):
        dataset = self.convert([contextinput], "predicting")
        dataset = self.normalize(dataset)
        print(dataset)
        result = self.clf.predict(dataset)[0]

        return result


    def flattencontextdict(self, inputdict):
        tmpdictlist = []
        for minidict in inputdict:
            entry = minidict
            value = inputdict[minidict]
            if type(value) == dict:
                for val in value:
                    val2 = value[val]
                    if val2 == "true": # make true and false statements into proper booleans
                        value[val] = True
                    if val2 == "false":
                        value[val] = False
                    if val == "lat" or val == "lon":
                        coordinate = val2.split(".")
                        decimal = coordinate[1][:4]
                        newcoordinate = float(coordinate[0] + "." + decimal)
                        value[val] = newcoordinate
                tmpdictlist.append(value)

        newdict = {}
        for flatdict in tmpdictlist:
            newdict.update(flatdict)
        return newdict

ml = machinelearning()

ml.train()
#contextinput = {"colour": "green", "shape": "square"}
contextinput = {"system":{"charging":"true","chargingplug":"AC","batterypercentage":45},"location":{"lon":"5.242350914413443","lat":"52.102965044310885","speed":2},"network":{"name":"\"FRITZ!Box Fon WLAN 7360\"","state":"CONNECTED","type":"WIFI"}}
contextinput = ml.flattencontextdict(contextinput)
result = ml.predict(contextinput)
if ml.getconfirmation:
    answer = input(f"I wasn't sure about the meaning of: {contextinput}. I think it means \"{result}\", is that correct? [Y/n]")
    if answer.lower() == "yes" or answer.lower() == "y":
        answerpositive = True
    else:
        answerpositive = False
    ml.trainingfeatures.append(contextinput) # add to the training set anyway
    if answerpositive:
        ml.traininglabels.append(result)
    else:
        newlabel = input("Alright, then what was it? ")
        res = input(f"Classifying \"{contextinput}\" as \"{newlabel}\", is that correct? [Y/n]")
        if res != "n":
            ml.traininglabels.append(newlabel)

    # because I don't save them:
    print(ml.trainingfeatures)
    print(ml.traininglabels)

print(f"\nLooks like you're {result}!")


