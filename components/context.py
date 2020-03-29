from sklearn import tree
from six import StringIO
import pydotplus
from time import sleep
import pickle
from ast import literal_eval as eval
from components.settings import Settings
from components.logger import logger as mainlogger
class Context:
    def __init__(self):
        self.tag = "context"
        self.datasize = 0
        self.trainingsize = 0
        self.features = []
        self.humanfeatures = {}
        self.inversehumanfeatures = {}
        self.labels = []
        self.getconfirmation = False
        self.tfeatures = Settings().getdata("MACHINELEARNING", "trainingfeatures")
        self.tlabels = Settings().getdata("MACHINELEARNING", "traininglabels")
        self.humanfeatures = Settings().getdata("MACHINELEARNING", "humanfeatures")
        if self.tfeatures == None:
            self.tfeatures = []
            self.tlabels = []
            self.humanfeatures = {}

        self.trainingfeaturesaslist = []

    def logger(self, msg, type="info", colour="none"):
        mainlogger().logger(self.tag, msg, type, colour)


    def convert(self, dataset, processtype = "predicting"):
        print("Converting...")
        print(self.humanfeatures)
        for index, data in enumerate(dataset):
            tmplist = []
            if type(data) == dict:
                for entry in data:
                    value = data[entry]
                    if value not in self.humanfeatures:
                        if processtype == "predicting":
                            print(f"don't know value {value}")
                            # set flag so I know to ask the user about it
                        newvalue = len(self.humanfeatures)
                        tmplist.append(newvalue)
                        self.humanfeatures[value] = len(self.humanfeatures) 
                        self.inversehumanfeatures[len(self.humanfeatures)] = value
                        #Settings().setdata({"MACHINELEARNING":{"humanfeatures":self.humanfeatures}})
                    else:
                        newvalue = self.humanfeatures[value]
                        tmplist.append(newvalue)
                dataset.remove(data)
                dataset.insert(index, tmplist)

        Settings().setdata({"MACHINELEARNING":{"humanfeatures":self.humanfeatures}})
        print("Done converting..")
        return dataset

    def addtotraining(self, numbertoadd):
        for dataset in self.trainingfeaturesaslist:
            while len(dataset) < numbertoadd:
                dataset.append(9999)

    def normalize(self, dataset, datatype = "normal"):
        print("Normalizing..")
        if datatype == "normal":
            if len(dataset[0]) > self.trainingsize: # check if new data is larger than training sample(it will be just one set, as a list)
                self.addtotraining(len(dataset[0]))
                self.train("retrain")
        newdataset = []
        for data in dataset:
            #if type(data) == str:
            data = eval(str(data))
            newdataset.append(data)
            if len(data) > self.datasize:
                self.datasize = len(data)
        dataset = newdataset
        trainingdata = Settings().getdata("MACHINELEARNING", "trainingfeatures")
        for data in dataset:
            print("comparing datalength!")
            while len(data) != self.datasize:
                if len(data) < self.datasize:
                    print("new data is smaller!")
                    data.append(9999)
                else:
                    print("new data is larger!")
                    for tdata in trainingdata:
                        while len(data) != len(tdata):
                            tdata.append(9999)
        if datatype == "training":
            self.trainingsize = self.datasize # set training sample size
            Settings().setdata({"MACHINELEARNING":{"trainingsize":self.trainingsize}})
            self.trainingfeaturesaslist = dataset
            Settings().setdata({"MACHINELEARNING":{"normalizeddataset":dataset}})
        return dataset

    def train(self, processtype = "normal"):
        preclf = tree.DecisionTreeClassifier()
        if processtype == "retrain":
            print("retraining with new data..")
            dataset = Settings().getdata("MACHINELEARNING", "normalizeddataset") # use special dataset that had it's samples updated to the correct size
            dataset = self.normalize(dataset, "training")
        else:
            dataset = self.convert(self.tfeatures, "training")
            dataset = self.normalize(dataset, "training")

        clf = preclf.fit(dataset, self.tlabels)
        with open("data/datamodel.pickle", "wb") as f:
           pickle.dump(clf, f)

    def predict(self, contextinput):
        dataset = self.convert([contextinput], "predicting")
        dataset = self.normalize(dataset)

        with open("data/datamodel.pickle", "rb") as f:
            clf = pickle.load(f)
        result = clf.predict(dataset)[0]
        featurenames = Settings().getdata("MACHINELEARNING", "humanfeaturenames")
        self.visualise(clf, featurenames)
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
                    if val == "lat" or val == "lon": #  make coordinates 3 decimals
                        coordinate = str(val2).split(".")
                        decimal = coordinate[1][:4]
                        newcoordinate = float(coordinate[0] + "." + decimal)
                        value[val] = newcoordinate
                    value[val] = str(value[val])
                tmpdictlist.append(value)

        newdict = {}
        for flatdict in tmpdictlist:
            newdict.update(flatdict)
        return newdict

    def trainmodel(self, inputdata, inputlabel):
        print("training model with new info")
        # flatten data
        flatinputdata = self.flattencontextdict(inputdata)
        humanfeaturenames = []
        for name in flatinputdata:
            humanfeaturenames.append(name)
        print(humanfeaturenames)
        Settings().setdata({"MACHINELEARNING":{"humanfeaturenames":humanfeaturenames}})
        # get trainingfeatures and labels
        #self.tfeatures = Settings().getdata("MACHINELEARNING", "trainingfeatures")
        #self.tlabels = Settings().getdata("MACHINELEARNING", "traininglabels")
        self.tfeatures.append(flatinputdata)
        self.tlabels.append(inputlabel)
        self.train("training")
        Settings().setdata({"MACHINELEARNING":{"trainingfeatures":self.tfeatures}})
        Settings().setdata({"MACHINELEARNING":{"traininglabels":self.tlabels}})
        return "Finished training"

    def getprediction(self, inputdata):
        print(f"Using: {inputdata} to predict contextstate")
        flatinputdata = self.flattencontextdict(inputdata)
        result = self.predict(flatinputdata)
        return result

    def visualise(self, clf, featurenames):
        dot_data = StringIO()
        tree.export_graphviz(clf, out_file=dot_data, feature_names=featurenames)
        graph = pydotplus.graph_from_dot_data(dot_data.getvalue())
        graph.write_pdf("ml.pdf")


    def handler(self, data):
        self.logger(f"Context handler is running!")
        self.logger(data)
contextinput = {"system":{"charging":"true","chargingplug":"AC","batterypercentage":45},"location":{"lon":"5.242350914413443","lat":"52.102965044310885","speed":2},"network":{"name":"\"FRITZ!Box Fon WLAN 7360\"","state":"CONNECTED","type":"WIFI"}}

#ml = machinelearning()
#flatinputdata = ml.flattencontextdict(contextinput)
#ml.trainmodel(flatinputdata, "home")
#result = ml.predict(flatinputdata)

#print(f"\nLooks like you're {result}!")


