import requests
import json
from threading import Thread

class RTCache(object):
    python_to_json_types = {"bool":"boolean", "int":"double", "float":"double", "str":"string"}
    def __init__(self, url, cacheName, rtHistoryVars, rtIndexVars, newCache=True):
        self.cacheName = cacheName
        
        self.rtVars = rtHistoryVars.copy()
        self.rtVars.update(rtIndexVars)
        vars(self).update(self.rtVars)
        self.rtVars = list(self.rtVars.keys())
        self.rtIndexVars = list(rtIndexVars.keys())
        self.rtHistoryVars = list(rtHistoryVars.keys())
        
        self.indexString = ''
        for s in self.rtIndexVars:
            if self.indexString == '':
                self.indexString = s
            else:
                self.indexString = self.indexString + ";" + s
        self.historyString = ''
        for s in self.rtHistoryVars:
            if self.historyString == '':
                self.historyString = s
            else:
                self.historyString = self.historyString + ";" + s
        
        self.data_init = [{"propName": "indexColumnNames", "propValue": self.indexString}, {"propName": "historyColumnNames", "propValue": self.historyString}]
        self.metadata_init = [{"name":"propName","type":"string"},{"name":"propValue","type":"string"}]
        
        self.dataTable = {}
        self.dataTable['rows'] = []
        
        self.url = url
        self.creationUrl = url +'/rtview/json/cache_processor/replace/'
        self.postUrl = url + '/rtview/json/data/'
        self.initialize_cache()
        
    
    '''collects all the variables in rtVariables, with their current values, and adds them as a row in the datatable'''
    def add_row(self):
        rowData = {}
        metadata = []
        for key in self.rtVars:
            value = vars(self)[key]
            rowData[key] = value
            metadataEntry = {}
            metadataEntry['type'] = self.python_to_json_types[type(value).__name__] #checks for the type of the given variable, and searches in a Python-to-JSON dictionary to convert it to JSON type
            #except:
                #raise KeyError("the object " + key + " is not a primitive (int, float, bool, or str), so it can't be sent to RTView Cloud")
            metadataEntry['name'] = key
            metadata.append(metadataEntry)
        try:
            self.dataTable['metadata'] #checks if metadata already has an entry
            if(self.dataTable['metadata'] != metadata): #checks to make sure the current metadata is the same as the one on record in dataTable
                raise Error("metadata has changed")
        except KeyError:
            self.dataTable['metadata'] = metadata #if metadata hasn't been added to the datatable yet it adds it
        self.dataTable['rows'].append(rowData)
    
    def remove_row(self, rowIndex):
        del self.dataTable['rows'][rowIndex]

    #def send_rows(self, rowIndices):
    
    def send_row(self, rowIndex=0):
        self.send_to_rtview(self.postUrl, self.cacheName, self.dataTable['metadata'], [self.dataTable['rows'][rowIndex]])
        del self.dataTable['rows'][rowIndex]
        
    def initialize_cache(self):
        self.send_to_rtview(self.creationUrl, self.cacheName, self.metadata_init, self.data_init)
        
    def send_all_rows(self):
        self.send_to_rtview(self.postUrl, self.dataTable['metadata'], self.dataTable['rows'])
        self.dataTable['rows'] = []
     
    #please do not use outside of this class
    def send_to_rtview(self, url, cacheName, metadata, body):
        print({"metadata": metadata, "data": body})
        requests.post(url = url + cacheName, json = {"metadata": metadata, "data": body})   
