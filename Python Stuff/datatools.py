'''
Tools for locally logging and optionally
sending data to RTView DataServer.
 
RTView DataServer provided by SL Corporation
'''
 
from __future__ import absolute_import, division, print_function
#from builtins import (bytes, str, open, super, range,
                      #zip, round, input, int, pow, object)
 
import sys
import os
import copy
import requests
import json
import time
import datetime
import traceback
 
class DataTools(object):
    '''
    The code below provides a function to locally save a set of data
    rows, or send to an RTView DataServer for caching and archival.
 
    The retry logic could be simplified as it may not be needed here
 
    For testing real-time data cache, set the following in environment:
    set RTV_HTTPURL=http://tom-project2.slsandbox.com/custom_rtvpost
    '''
    def __init__(self, local_log=None, url=None, verbose=True):
        '''
        INITIALIZATIION
 
        local_log = (fileobj) optional file object to write data to
        url = (str) optional URL to use for RTView logging
        '''
        self.local_log_fp = local_log
        self.verbose = verbose
 
        self.g_rtvHttpUrl = url     # just used in building g_rtvUrlWrite, and not elsewhere
        self.g_rtvUrlWrite = url
        self.g_rtvUrlCommand = url
         
        # A dictionary of user-defined data tables
        self.g_datatables = { } 
 
        self.sendErrorOccurrred = False;
        self.lastSendTime = 0;
        self.retryDelayTime = 20;
 
    def validateTargetUrl(self):
        '''
        Be sure there is a valid target RTView HTTP URL 
        '''
        if (self.g_rtvHttpUrl is not None):
            return
         
        # Obtain target URL for dataserver from environment
        self.g_rtvHttpUrl = os.getenv('RTV_HTTPURL', 'http://localhost:3275')     # do NOT default to local process
        #self.g_rtvHttpUrl = os.getenv('RTV_HTTPURL', '')
        if not self.g_rtvHttpUrl:
            if self.verbose:
                print("[DataTools] Warning: environment had empty RTV_HTTPURL - not doing remote logging")
            return
 
        # Append the autocache routes
        self.g_rtvUrlWrite = self.g_rtvHttpUrl + '/rtview/json/data/'
        self.g_rtvUrlCommand = self.g_rtvHttpUrl + '/rtview/json/cache_processor/'
         
        if self.verbose:
            print('... RTView DataServer Target URL <%s>' % self.g_rtvHttpUrl)
     
    def initialize(self, url=None, local_log=None):
        self.g_rtvHttpUrl = url or self.g_rtvHttpUrl        # just used in building g_rtvUrlWrite, and not elsewhere
        self.g_rtvUrlWrite = url or self.g_rtvUrlWrite
        self.local_log_fp = local_log or self.local_log_fp  # fallback to whatever was used when class was instantiated, if unspecified
        self.validateTargetUrl()
        if self.verbose:
            print("[DataTools] using URL=%s, local_log=%s" % (self.g_rtvUrlWrite, self.local_log_fp))
  
    # DATA TABLE MANAGER methods
     
    def datatable_begin(self, tablename, metadata):
        '''
        Begin a new, empty, named data table
        '''
        if (tablename is None or tablename == ''):
            return
        if (metadata is None or len(metadata) < 1):
            return
         
        datatable = { 'metadata' : metadata, 'data':[] }
         
        self.g_datatables[tablename] = datatable
     
    def datatable_clear(self, tablename):
        '''
        Remove all data from the named data table
        '''
        if (tablename is None or tablename == ''):
            return
        if tablename not in self.g_datatables:
            print('ERROR: tablename not found in datatables <%s>' % tablename)
            return
         
        self.g_datatables[tablename]['data'][:] = []
         
    def datatable_addrow(self, tablename, datarow):
        '''
        Add row to data to be sent, but do not actually send it.
 
        tablename = (str) name of table
        datarow = (list) list of data to add to the table
        '''
        if (tablename is None or tablename == ''):
            return
        if (datarow is None or len(datarow) < 1):
            return
        if tablename not in self.g_datatables:
            print('ERROR: tablename not found in datatables <%s>' % tablename)
            return
         
        datatable = self.g_datatables[tablename]
        datatable['data'].append(datarow)
         
    def datatable_get(self, tablename, reset=False):
        '''
        Return the given datatable.
         
        If reset requested, make a deepcopy of the table for return,
        and clear out data from original table.
        '''
        if not tablename:
            return None
 
        if tablename not in self.g_datatables:
            print('ERROR: tablename not found in datatables <%s>' % tablename)
            return None
         
        datatable = self.g_datatables[tablename]
 
        # if requested, clean out data after copying it for return
        if reset:
            origdata = datatable
            datatable = copy.deepcopy(origdata)
            origdata['data'] = []
                 
        return datatable
         
    def datatable_send(self, tablename, cachename):
        '''
        Send a datatable.  This goes to the target URL (if doing remote logging)
 
        Returns True if successful, False otherwise.
        '''
        if not tablename:
            return
        if not cachename:
            return
        if tablename not in self.g_datatables:
            print('ERROR: tablename not found in datatables <%s>' % tablename)
            return
         
        datatable = self.g_datatables[tablename]
        if (len(datatable['data']) < 1):
            return True
 
        status = False
        if (datatable is not None):
            if self.local_log_fp:
                try:
                    datastr = json.dumps({'cache': cachename, 'table': datatable})
                    self.local_log_fp.write(datastr + "\n")
                    self.local_log_fp.flush()
                    status = True
                except Exception as err:
                    if self.verbose:
                        print("[DataTools] logging locally to %s, but encountered error %s while writing %s bytes" % (self.local_log_fp, str(err), len(datastr)))
                        traceback.print_exc()
            if self.g_rtvUrlWrite:
                status = self.send_to_rtview(datatable, cachename)
            if status:
                datatable['data'] = []  # clean out data which was just sent successfully
        return status
     
    def send_to_rtview(self, table, cacheName):
        '''
        Send one row of data to RTView DataServer
 
        TODO: handle such sending in a separate python thread, to avoid bottlenecking main processing.
        '''
        # If there is no place to write to, just return
        if not self.g_rtvUrlWrite:
            return False
         
        if self.sendErrorOccurrred == True:
            # wait N seconds before trying again, return false or fall thru to try
            now = self.current_timestamp()
            print('    ... now on error condition: ', now, ' last: ', self.lastSendTime, ' check: ', (now - self.lastSendTime), ' delay: ', self.retryDelayTime)
            if (now - self.lastSendTime) < self.retryDelayTime:
                print('*** cannot send due to previous error')
                return False
            #print(' ^^^^^^^^^ falling thru');
            sys.exit(1);
         
        try:
            self.sendErrorOccurrred = False
            self.lastSendTime = self.current_timestamp()
            #print('    ... last send time: ', self.lastSendTime)
            x = json.dumps(table)
            print(x)
            print("URL: " + self.g_rtvUrlWrite + cacheName)
            print('')
            headers = {'content-type': 'application/json'}
            response = requests.post(self.g_rtvUrlWrite + cacheName, data=x, headers=headers)
            # TODO: check return code before declaring success
            #print('... response: ' + str(response))
            return True
     
        except requests.exceptions.RequestException as e:
            print('ERROR: ', e)
            self.sendErrorOccurrred = True
            return False
 
    def current_timestamp(self):
        try:
           return int(datetime.datetime.now().timestamp())
        except Exception as err:
            unixtime = time.mktime(datetime.datetime.now().timetuple())
            return int(unixtime)
 
    # Shortcut, duplicate code alert; just done for expediency
    def command_to_rtview(self, table, command, cacheName):
        '''
        Execute command on RTView DataServer
 
        TODO: handle such sending in a separate python thread, to avoid bottlenecking main processing.
        '''
        # If there is no place to write to, just return
        if not self.g_rtvUrlCommand:
            return False
         
        if self.sendErrorOccurrred == True:
            # wait N seconds before trying again, return false or fall thru to try
            now = self.current_timestamp()
            print('    ... now on error condition: ', now, ' last: ', self.lastSendTime, ' check: ', (now - self.lastSendTime), ' delay: ', self.retryDelayTime)
            if (now - self.lastSendTime) < self.retryDelayTime:
                print('*** cannot send due to previous error')
                return False
            #print(' ^^^^^^^^^ falling thru');
            sys.exit(1);
         
        try:
            self.sendErrorOccurrred = False
            self.lastSendTime = self.current_timestamp()
            #print('    ... last send time: ', self.lastSendTime)
            headers = {'content-type': 'application/json'}
            x = json.dumps(table)
            print(x)
            response = requests.post(self.g_rtvUrlCommand + command + '/' + cacheName, data=x, headers=headers)
            # TODO: check return code before declaring success
            #print('... response: ' + str(response))
            return True
     
        except requests.exceptions.RequestException as e:
            print('ERROR: ', e)
            self.sendErrorOccurrred = True
            return False
       
    ######################################################################
     
    def datacache_create(self, cacheName, properties):
        '''
        Create a named data cache with the given properties.
        '''
        postdata = { 
            'metadata': [
                { 'name': 'propName', 'type': 'string' },
                { 'name': 'propValue', 'type':'string' }
            ]
        }
 
        # If there is no place to write to, just return
        if not self.g_rtvUrlCommand:
            return False
             
        if properties == None:
            return False
 
        postdata['data'] = properties
         
        status = self.command_to_rtview(postdata, 'replace', cacheName)
        return status
 
    def datacache_delete(self, cacheName):
        '''
        Delete the named data cache.
        '''
        # If there is no place to write to, just return
        if not self.g_rtvUrlCommand:
            return False
           
        status = self.command_to_rtview(None, 'delete', cacheName)
        return status
         
       
#-----------------------------------------------------------------------------
# instantiations for module use
 
DT = DataTools()    # instantiate class, which keeps its own internal variables private
 
# public interface calls
initialize = DT.initialize
datatable_send = DT.datatable_send
datatable_begin = DT.datatable_begin
datatable_clear = DT.datatable_clear
datatable_addrow = DT.datatable_addrow
datatable_get = DT.datatable_get
datacache_create = DT.datacache_create
datacache_delete = DT.datacache_delete
 
#-----------------------------------------------------------------------------
# unit tests
#
# Run this, e.g. using "py.test datatools.py"
 
def run_test_http_server(PORT=9275, fp=None):
    try:
        import SimpleHTTPServer
    except:
        import http.server as SimpleHTTPServer
    try:
        import SocketServer
    except:
        import socketserver as SocketServer
    class MyServer(SimpleHTTPServer.SimpleHTTPRequestHandler):
        def do_GET(self):
            return
        def do_POST(self):
            print("--> received post")
            print("headers = ", self.headers)
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            print("data string = ", data_string)
            fp.send(data_string)
 
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
 
    httpd = SocketServer.TCPServer(("", PORT), MyServer)
    print("test http serving at port", PORT)
    httpd.serve_forever()
 
def test_send_data1():
    import time
    from multiprocessing import Process, Pipe
 
    PORT = 9275
    parent_conn, child_conn = Pipe()
    p = Process(target=run_test_http_server, args=(PORT, child_conn))
    p.start()
 
    test_metadata = [
        {"name":"name","type":"string"},
        {"name":"value2","type":"long"},
        {"name":"value3","type":"long"}
    ]
    test_datarow = { 
        'name' : 'A',  
        'value2' : 23, 
        'value3' : 46
    } 
     
    initialize(url="http://localhost:%s/logger" % PORT)
    print('... sending test data: ' + str(test_datarow))
    datatable_begin('test_data', test_metadata)
    datatable_addrow('test_data', test_datarow)
    status = datatable_send('test_data', 'QTestData')
    print('... status = ' + str(status))
    assert status
 
    time.sleep(2)
    written_data = parent_conn.recv()
    rd = json.loads(written_data)
    assert 'metadata' in rd
 
    p.terminate()
 
 
def test_send_data2():
    os.environ["RTV_HTTPURL"] =  ""
    test_metadata = [
        {"name":"name","type":"string"},
        {"name":"value2","type":"long"},
        {"name":"value3","type":"long"}
    ]
    test_datarow = { 
        'name' : 'A',  
        'value2' : 23, 
        'value3' : 46
    } 
 
    DT = DataTools()    # re-instantiate class, to keep things clean
    initialize = DT.initialize
    datatable_send = DT.datatable_send
    datatable_begin = DT.datatable_begin
    datatable_clear = DT.datatable_clear
    datatable_addrow = DT.datatable_addrow
    datatable_get = DT.datatable_get
    datacache_create = DT.datacache_create
    datacache_delete = DT.datacache_delete
 
    ofn = "test_local_rtview_data.dat"
    if os.path.exists(ofn):
        os.unlink(ofn)
    fp = open(ofn, 'w')
    initialize(local_log=fp, url=None)
    print('... sending test data: ' + str(test_datarow))
    datatable_begin('test_data', test_metadata)
    datatable_addrow('test_data', test_datarow)
    status = datatable_send('test_data', 'QTestData')
    print('... status = ' + str(status))
    assert status
 
    fp.close()
    data = json.loads(open(ofn).read())
    assert 'metadata' in data
    