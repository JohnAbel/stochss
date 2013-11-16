'''
This class exposes all the services offered by the backend
It accepts calls from the front-end and pass them on to the backend.
All the input validation is performed in this class.
'''
from infrastructure_manager import InfrastructureManager
import threading
import os, subprocess, signal, uuid, sys, shlex, time
import logging
from datetime import datetime
from tasks import *

class backendservices():
    ''' 
    constructor for the backend service class.
    It should be passed the agent creds
    ''' 
        
    tablename = "stochss"
    def backendservices(self):
        '''
        constructor to set the path of various libraries
        ''' 
        sys.path.append(os.path.join(os.path.dirname(__file__), 'lib/boto'))
        sys.path.append(os.path.join(os.path.dirname(__file__), 'lib/celery'))
        sys.path.append(os.path.join(os.path.dirname(__file__), 
                                     '/Library/Python/2.7/site-packages/amqp'))
        createtable(self.tablename)
            
    def executeTask(self,params):
        '''
        This method instantiates celery tasks in the cloud.
        '''
        logging.info('inside execute task for cloud : Params - %s', str(params))
        try:
            from tasks import task,updateEntry
            taskid = str(uuid.uuid4())
            #create a celery task
            logging.debug("executeTask : executing task with uuid : %s ",
                           taskid)
            timenow = datetime.now() 
            data = {'status':"pending","start_time":timenow.strftime('%Y-%m-%d %H:%M:%S'), 'Message':"Task sent to Cloud"}
            updateEntry(taskid, data, self.tablename)
            tmp = task.delay(taskid, params)
            logging.debug("executeTask :  result of task : %s", str(tmp))
            return tmp,taskid
        except Exception, e:
            logging.error("executeTask : error - %s", str(e))
    
    def executeTaskLocal(self, params):
        '''
        This method spawns a stochkit process. It doesn't wait for the process to finish. The status of the
        process can be tracked using the pid and the output directory returned by this method. 
        
        @param  params['file'] = the absolute path of the xml file 
        @param  params['paramstring'] = the parameter to be passed to the stochkit execution
        'STOCHKIT_HOME' = this is the environment variable which has the path of the stochkit executable
        @return: 
           {"pid" : 'the process id of the task spawned', "output": "the directory where the files will be generated"}
         
        '''

        try:           
            logging.info("executeTaskLocal : inside method with params : %s ", 
                         str(params))
            res = {}
            
            #xmlfilepath = params['file']
            paramstr =  params['paramstring']
            uuidstr = str(uuid.uuid4())
            res['uuid'] = uuidstr
            create_dir_str = "mkdir -p output/%s " % uuidstr
            os.system(create_dir_str)
            
            # Write the model document to file
            xmlfilepath = "output/" + uuidstr +"/"+uuidstr+".xml"
            xmlfilepath = os.path.abspath(xmlfilepath)
            mfhandle = open(xmlfilepath,'w')
            mfhandle.write(params['document'])
            mfhandle.close()
            
            # Pipe output to these files
            res['stdout'] = os.path.abspath('output/' + uuidstr + '/stdout')
            res['stderr'] = os.path.abspath('output/' + uuidstr + '/stderr')
            
            # The following executiong string is of the form :
            # stochkit_exec_str = "~/StochKit2.0.6/ssa -m ~/output/%s/dimer_decay.xml -t 20 -i 10 -r 1000" % (uuidstr)
            stochkit_exec_str = "{backenddir}/wrapper.sh {stdout} {stderr} {0} --model {1} --out-dir output/{2}/result ".format(paramstr,xmlfilepath,uuidstr, stdout = res['stdout'], stderr = res['stderr'], backenddir = os.path.abspath(os.path.dirname(__file__)))
            logging.info("STOCHKIT_EXEX_STR: "+stochkit_exec_str)
            logging.debug("executeTaskLocal : Spawning StochKit Task. String : %s",
                           stochkit_exec_str)
            
            p = subprocess.Popen(stochkit_exec_str, shell=True, stdin=subprocess.PIPE)

            #logging.debug("executeTaskLocal: the result of task {0} or error {1} ".format(output,error))
            pid = p.pid

            res['pid'] = pid 
            filepath = "output/%s//" % (uuidstr)
            logging.debug("executeTaskLocal : PID generated - %s", pid)
            absolute_file_path = os.path.abspath(filepath)
            logging.debug("executeTaskLocal : Output file - %s", absolute_file_path)
            res['output'] = absolute_file_path

            logging.info("executeTaskLocal: exiting with result : %s", str(res))
            return res
        except Exception as e:
            logging.error("executeTaskLocal : exception raised : %s" , str(e))
            return None

    def executeRTaskLocal(self, params):
        '''
        This method spawns an R process.
        params = dictionary of parameters for execution
        '''
        logging.info("executeRTaskLocal: inside method with params: %s", str(params))
        try:
            default_params = {
                'model_file': '/path/to/default/model_file',
                'model_data': '/path/to/default/data_file',
                'steps': 'CEU',
                'seed': '1',
                'cores': '2',
                'Kce': '10000',
                'Kem': '10',
                'Klik': '10000',
                'Kcov': '10000',
                'rho': '.001',
                'perturb': '.25',
                'alpha': '.25',
                'beta': '.25',
                'gamma': '.25',
                'k': '3',
                'pcutoff': '.0001',
                'qcutoff': '.005',
                'numIter': '10',
                'numConverge': '1',
                'exec': 'bash &',
                'options': ''
            }
            default_params.update(params)
            logging.info("executeRTaskLocal: params after merging with defaults: %s", str(default_params))
            print str(default_params)
            
            res = {}
            
            uuidstr = str(uuid.uuid4())
            res['uuid'] = uuidstr
            output_dir = "output/%s" % uuidstr
            create_dir_str = "mkdir -p %s" % output_dir
            os.system(create_dir_str)
            
            # model_file_path = "app/output/" + uuidstr +"/model-"+uuidstr+".R"
            # model_file_path = os.path.abspath(model_file_path)
            # mf_handle = open(model_file_path,'w')
            # mf_handle.write(params['model_file'])
            # mf_handle.close()
            # 
            # model_data_path = "app/output/" + uuidstr +"/data-"+uuidstr+".txt"
            # model_data_path = os.path.abspath(model_data_path)
            # md_handle = open(model_data_path,'w')
            # md_handle.write(params['model_data'])
            # md_handle.close()
            
            res['stdout'] = os.path.abspath(output_dir + '/stdout')
            res['stderr'] = os.path.abspath(output_dir + '/stderr')
            stdout_handle = open(res['stdout'], 'w')
            stderr_handle = open(res['stderr'], 'w')
            
            cmd = "stochoptim/exec/mcem2.r --model {model_file} --data {model_data} --steps {steps} --seed {seed} --cores {cores} --K.ce {Kce} --K.em {Kem} --K.lik {Klik} --K.cov {Kcov} --rho {rho} --perturb {perturb} --alpha {alpha} --beta {beta} --gamma {gamma} --k {k} --pcutoff {pcutoff} --qcutoff {qcutoff} --numIter {numIter} --numConverge {numConverge} --command '{exec}' --options '{options}'".format(**default_params)
            logging.info("executeRTaskLocal: about to start execution with command string: %s" % cmd)
            process_handle = subprocess.Popen(shlex.split(cmd), stdout = stdout_handle, stderr = stderr_handle)
            
            res['pid'] = process_handle.pid
            res['output'] = os.path.abspath(output_dir)
            print res
            logging.info("executeRTaskLocal: exiting with result: %s", str(res))
            return res
        except Exception as e:
            logging.info("executeRTaskLocal: exception raised: %s", str(e))
            print "exception " + str(e)
    
    def checkTaskStatusLocal(self, pids):
        '''
        checks the status of the pids and returns true if the task is running or else returns false
        pids = [list of pids to check for status]
        returns a dictionary as {"pid1":"status", "pid2":"status", "pid3":"status"}
        '''
        res = {}
        logging.info("checkTaskStatusLocal : inside with params %s", str(pids))
        try:
            for pid in pids:
                try:
                    os.getpgid(pid)
                    res[pid] = True
                except Exception,e:
                    res[pid] = False
            logging.info("checkTaskStatusLocal : exiting with result : %s", str(res))
            return res
        except Exception as e:
            logging.error("checkTaskStatusLocal: Exiting with error : %s", str(e))
            return None
    
    def checkTaskStatusCloud(self, ids):
        '''
        checks the status of the pids and returns true if the task is running or else returns false
        pids = [list of pids to check for status]
        returns a dictionary as {"pid1":"status", "pid2":"status", "pid3":"status"}
        '''
        res = {}
        
        return res
    
    
    def describeTask(self, params):
        '''
        @param params: A dictionary with the following fields
         "AWS_ACCESS_KEY_ID" : AWS access key
         "AWS_SECRET_ACCESS_KEY": AWS security key
         taskids : list of celery taskids
         @return: 
         a dictionary of the form :
         {"taskid":"result:"","state":""} 
        '''
        logging.info("describeTask : inside method with params : %s", params)
        logging.debug("describeTask : setting environment variables : AWS_ACCESS_KEY_ID - %s", params['AWS_ACCESS_KEY_ID']) 
        os.environ["AWS_ACCESS_KEY_ID"] = params['AWS_ACCESS_KEY_ID']
        logging.debug("describeTask : setting environment variables : AWS_SECRET_ACCESS_KEY - %s", params['AWS_SECRET_ACCESS_KEY'])
        os.environ["AWS_SECRET_ACCESS_KEY"] = params['AWS_SECRET_ACCESS_KEY']
        result = {}
        try:
                result = describetask(params['taskids'], self.tablename)
        except Exception, e:
            logging.error("describeTask : exiting with error : %s", str(e))
            return None
        logging.info("describeTask : exiting with result : %s", str(result))
        return result
    
    def deleteTasks(self, taskids):
        '''
        @param taskid:the list of taskids to be removed 
        this method revokes scheduled tasks as well as the tasks in progress. It 
        also removes task from the database. It ignores the taskids which are not active.
        '''
        logging.info("deleteTasks : inside method with taskids : %s", taskids)
        try:
            for taskid in taskids:
                removeTask(taskid) #this removes task from celery queue
                removetask(self.tablename,taskid) #this removes task information from DB. ToDo: change the name of method
            logging.info("deleteTasks: All tasks removed")
        except Exception, e:
            logging.error("deleteTasks : exiting with error : %s", str(e))

    
    def deleteTaskLocal(self, pids):
        """
        pids : list of pids to be deleted.
        Terminates the processes associated with the PID. 
        This methods ignores the PID which are  not active.
        """
        logging.info("deleteTaskLocal : inside method with pids : %s", pids)
        for pid in pids:
            try:
                os.kill(pid, signal.SIGKILL)
            except Exception, e:
                logging.error("deleteTaskLocal : couldn't kill process. error: %s", str(e))
        logging.info("deleteTaskLocal : exiting method")        
    
    def startMachines(self, params):
        '''
        This method instantiates ec2 instances
        '''

        #this will basically start an instance in ec2
        # add call from the infrastructure manager here
        logging.info("startMachines : inside method with params : %s", str(params))
        try:
            i = InfrastructureManager(blocking=True)
            res = i.run_instances(params,params)
            return res
            logging.info("startMachines : exiting method with result : %s", str(res))
        except Exception, e:
            logging.error("startMachines : exiting method with error : %s", str(e))
            return None
        
    def stopMachines(self, params):
        '''
        This method would terminate all the  instances associated with the account
        It expects the following two fields in the  parameter argument
        params ={"infrastructure":"ec2",
             'credentials':{"EC2_ACCESS_KEY":"______________", 
              "EC2_SECRET_KEY":"__________"},
                  }
        '''
        try:
            i = InfrastructureManager(blocking=True)
            res = i.terminate_instances(params)
            print str(res)
            return True
        except Exception, e:
            logging.error("Terminate machine failed with error : %s", str(e))
            return False
    
    def describeMachines(self, params):
        '''
        This method gets the status of all the instances of ec2
        '''
        # add calls to the infrastructure manager for getting details of
        # machines
        logging.info("describeMachines : inside method with params : %s", str(params))
        try:
            i = InfrastructureManager()
            secret =[]
            res = i.describe_instances(params, secret)
            logging.info("describeMachines : exiting method with result : %s", str(res))
            return res
        except Exception, e:
            logging.error("describeMachines : exiting method with error : %s", str(e))
            return None
    
    
    def validateCredentials(self, params):
        '''
        This method verifies the validity of ec2 credentials
        '''
        logging.info("validateCredentials: inside method with params : %s", str(params))
        try:
            i = InfrastructureManager()
            logging.info("validateCredentials: exiting with result : %s", str(i))
            return i.validate_Credentials(params)
        except Exception, e:
            logging.error("validateCredentials: exiting with error : %s", str(e))
            return False
    
    
    def fetchOutput(self, taskid, outputurl):
        '''
        This method gets the output file from S3 and extracts it to the output 
        directory
        @param taskid: the taskid for which the output has to be fetched
        @return: True : if successful or False : if failed 
        '''
        try : 
            logging.info("fetchOutput: inside method with taskid : {0} and url {1}".format(taskid, outputurl))
            filename = "{0}.tar".format(taskid)
            #the output directory
            #logging.debug("fetchOutput : the name of file to be fetched : {0}".format(filename))
            #baseurl = "https://s3.amazonaws.com/stochkitoutput/output"
            #fileurl = "{0}/{1}".format(baseurl,filename)
            logging.debug("url to be fetched : {0}".format(taskid))
            fetchurlcmdstr = "curl --remote-name {0}".format(outputurl)
            logging.debug("fetchOutput : Fetching file using command : {0}".format(fetchurlcmdstr))
            os.system(fetchurlcmdstr)
            if not os.path.exists(filename):
                logging.error('unable to download file. Returning result as False')
                return False
            return True
        except Exception, e:
            logging.error("fetchOutput : exiting with error : %s", str(e))
            return False
        
if __name__ == "__main__":
    pass
    obj = backendservices()
    print "about to call executeRTaskLocal"
    res = obj.executeRTaskLocal({
        'model_file': '/Users/choruk/src/stochss/app/stochoptim/inst/extdata/birth_death_MAImodel.R',
        'model_data': '/Users/choruk/src/parameter_est/birth_death_MAdata.txt'
    })
    print "called executeRTaskLocal"
    print "checkTaskStatusLocal: " + str(obj.checkTaskStatusLocal([res['pid']]))
    while (obj.checkTaskStatusLocal([res['pid']])[res['pid']] == True):
        print "task not done"
        time.sleep(10)
    print "task done"
'''
    PARAM_CREDENTIALS = 'credentials'
    PARAM_GROUP = 'group'
    PARAM_IMAGE_ID = 'image_id'
    PARAM_INSTANCE_TYPE = 'instance_type'
    PARAM_KEYNAME = 'keyname'
    credentials = {"EC2_ACCESS_KEY":"KIAJWILGFLOFVDRDRCQ", "EC2_SECRET_KEY":"vnEvY4vFpmaPsPNTB80H8IsNqIkWGTMys/95VWaJ"}
    params ={"infrastructure":"ec2",
             "num_vms":1, 
             'group':'stochss19', 
             'image_id':'ami-11bad678', 
             'instance_type':'t1.micro',
             'keyname':'stochssnew32', 
             'email':['anand.bdk@gmail.com'],
             'credentials':{"EC2_ACCESS_KEY":"AKIAJWILGFLOFVDRDRCQ", "EC2_SECRET_KEY":"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"},
             #'credentials':{"EC2_ACCESS_KEY":"sadsdsad", "EC2_SECRET_KEY":"/95VWaJ"},
             'use_spot_instances':False}
'''
    #test  = obj.validateCredentials(params)
    #print test
    #print str(obj.startMachines(params))
#    print obj.stopMachines(params)
    #val = obj.describeMachines(params)
#    pids = [12680,12681,12682, 18526]
    #res  = obj.checkTaskStatusLocal(pids)
#    pids = [18511,18519,19200]
    #obj.deleteTaskLocal(pids)
    #print str(res)
    #obj.fetchOutput("2f3d86eb-9231-407d-bfd9-19010695e6a3","https://s3.amazonaws.com/78d7d1dc-0dfe-48e8-95ae-eec20d0ca346/output/2f3d86eb-9231-407d-bfd9-19010695e6a3.tar")
    #param = {'file':"/Users/RaceLab/StochKit2.0.6/models/examples/dimer_decay.xml",'paramstring':"--force -t 10 -r 1000"}
    #res = obj.executeTaskLocal(param)
    #print str(res)
    #obj.startMachines(params)
    #obj.describeMachines(params)
    
