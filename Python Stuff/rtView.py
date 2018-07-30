import requests
class Cache(object):
    def __init__(self, url, cacheName, rtVars):
        self.cacheName = cacheName
        
        self.url = url
        self.vars = rtVars
        self.creationUrl = url +'/rtview/json/cache_processor/replace/'
        self.postUrl = url + '/rtview/json/data/'
        
        self.rtVars = []
        indexString = ''
        historyString = ''
        for x in rtVars:
            if x.varType == "index":
                if indexString == '':
                    indexString = x.name
                else:
                    indexString = indexString + ";" + x.name
            if x.varType == "history":
                if historyString == '':
                    historyString = x.name
                else:
                    historyString = historyString + ";" + x.name
            self.rtVars.append(x)
            
        metadata = [{"name":"propName","type":"string"},{"name":"propValue","type":"string"}]
        body = [{"propName": "indexColumnNames", "propValue": indexString}, {"propName": "historyColumnNames", "propValue": historyString}]
        self.send_to_rtview(self.creationUrl, cacheName, metadata, body)
        
        self.rowMetadata = []
        for x in rtVars:
            self.rowMetadata.append({"name": x.name, "type": x.valueType})
        
        
    def send_data_row(self):
        subDict = {}
        for x in self.rtVars:
            subDict[x.name] = x.unflushedValues[0]
            del(x.unflushedValues[0])
        data = [subDict]
        self.send_to_rtview(self.postUrl, self.cacheName, self.rowMetadata, data)
        
    
    def send_to_rtview(self, url, cacheName, metadata, body):
        print({"metadata": metadata, "data": body})
        requests.post(url = url + cacheName, json = {"metadata": metadata, "data": body})
        
class rtVar(object):
    
    def __init__(self, name, valueType, varType, value=None):
        self.name = name
        self.valueType = valueType
        self.value = value
        self.varType = varType
        self.valueHistory = []
        if value != None:
            self.valueHistory.append(value)
        self.unflushedValues = self.valueHistory
        
    def updateValue(self, value):
        self.value = value
        self.valueHistory.append(value)