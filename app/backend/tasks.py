import sys,os,logging
sys.path.append(os.path.join(os.path.dirname(__file__), '../lib/celery'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../lib/kombu'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../lib/amqp'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../lib/billiard'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../lib/anyjson'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../lib/pytz'))
print str(sys.path)
from celery import Celery, group
import celeryconfig
import os, subprocess, shlex
import uuid,traceback
THOME = '/home/ubuntu'
STOCHKIT_DIR = '/home/ubuntu/StochKit'
ODE_DIR = '/home/ubuntu/ode'
MCEM2_DIR = '/home/ubuntu/stochoptim'

import logging, subprocess
import boto.dynamodb
from datetime import datetime
from multiprocessing import Process
import tempfile, time

class CelerySingleton(object):
    """
    Singleton class by Duncan Booth.
    Multiple object variables refer to the same object.
    http://web.archive.org/web/20090619190842/http://www.suttoncourtenay.org.uk/duncan/accu/pythonpatterns.html#singleton-and-the-borg
    """
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls)
            cls._instance.app = Celery('tasks')
        return cls._instance
    
    def configure(self):
        reload(celeryconfig)
        self.app.config_from_object('celeryconfig')

celery_config = CelerySingleton()
celery_config.configure()
celery = celery_config.app

def poll_commands(queue_name):
    '''
    '''
    print "Polling process: just started..."
    package_root = "StochOptim"
    commands_file = os.path.abspath("commands.txt")
    done_token = "done"
    # slave_tasks = []
    all_slave_params = []
    while True:
        # Do this in a loop forever until the master_task terminates this process
        # Check for commands file
        print "Polling process: checking for commands file..."
        while not os.path.exists(commands_file):
            time.sleep(5)
        print "Polling process: found commands file..."
        # Ok it exists, now check the last line
        all_commands = []
        last_line = ""
        print "Polling process: checking for done token..."
        with open(commands_file, 'r') as commands:
            all_commands = [c.strip() for c in commands.readlines()]
            last_line = all_commands[-1]
        # We need to wait until all commmands are there
        while last_line != done_token:
            time.sleep(5)
            with open(commands_file, 'r') as commands:
                all_commands = [c.strip() for c in commands.readlines()]
                last_line = all_commands[-1]
        print "Polling process: found done token, re-constructing commands..."
        # Ok we have all the commands now.
        all_commands.remove(done_token)
        # slave_tasks = []
        all_slave_params = []
        for command in all_commands:
            # We need to reconstruct the command for the remote worker.
            # We are going to reconstruct it in place and then just join
            # the segments of the array to create the final string.
            command_segments = command.split(' ')
            # We actually don't need to worry about the full path to the executable being
            # wrong because all instances on the same infrastructure have the exact same
            # directory structure.
            slave_params = {}
            # We do need to worry about all of the input/output files.
            for index, segment in enumerate(command_segments):
                # For input files, we will pass the contents of the file as a key,value pair
                # to the slave in the input parameters map, where the key is just the file name
                # in the command string and the value is the file contents.
                # We need to re-write the contents to file on the slave before calling.
                if segment == "--model":
                    file_name = command_segments[index+1]
                    with open(file_name, 'r') as file_content:
                        slave_params[file_name] = file_content.read()
                elif segment == "--initial":
                    file_name = command_segments[index+1]
                    with open(file_name, 'r') as file_content:
                        slave_params[file_name] = file_content.read()
                elif segment == "--final":
                    file_name = command_segments[index+1]
                    with open(file_name, 'r') as file_content:
                        slave_params[file_name] = file_content.read()
                # For output files, we don't need to do anything really because the slave will deal with
                # making sure they exist on the master after the slave is finished.
                elif segment == "--output":
                    pass
                elif segment == "--stats":
                    pass
            # Now command_segments is the correct execution string (other than the business with the
            # input files), just need to join it.
            execution_string = " ".join(command_segments)
            print "Polling process: command =", execution_string
            slave_params['exec_str'] = execution_string
            # celery_result = slave_task.delay(slave_params, queue=queue_name)
            # slave_tasks.append(celery_result)
            all_slave_params.append(slave_params)
        # Part of Celery's task calling API, calls all tasks at the same time,
        # can retrieve all the results together.
        slave_group = group(
            slave_task.s(slave_params).set(queue=queue_name) for slave_params in all_slave_params
        )()
        print "Poll process: waiting on results from slaves", queue_name
        # all_results will be a list of dictionaries, each with one or two
        # (file name, file content) key-value pairs
        all_results = slave_group.get()
        # Now remove the commands file and wait until all slave_tasks are done
        os.system("rm -rf {0}".format(commands_file))
        # Need to write them all to files now
        for result in all_results:
            for key in result:
                with open(key, 'w') as file_handle:
                    file_handle.write(result[key])
        # Now we loop back to the start since the actual master executable just polls the
        # file-system and should have all the files it needs now.
        print "Poll process: done writing output files"

def update_s3_bucket(task_id, bucket_name, output_dir):
    print "S3 update process just started..."
    # Wait 30 seconds initially for some output to build up
    time.sleep(30)
    while True:
        tar_output_str = "tar -zcf {0}.tar {0}".format(output_dir)
        print "S3 update", tar_output_str
        os.system(tar_output_str)
        copy_to_s3_str = "python {0}/sccpy.py {1}.tar {2}".format(THOME, output_dir, bucket_name)
        print "S3 update", copy_to_s3_str
        os.system(copy_to_s3_str)
        data = {
            'uuid': task_id,
            'status': 'active',
            'message': 'Executing in the cloud.',
            'output': "https://s3.amazonaws.com/{0}/{1}.tar".format(bucket_name, output_dir)
        }
        updateEntry(task_id, data, "stochss")
        # Update the output in S3 every 30 seconds...
        time.sleep(30)

@celery.task(name='tasks.master_task')
def master_task(task_id, params):
    '''
    This task encapsulates the logic behind the new R program.
    '''
    global MCEM2_DIR
    try:
        print "Master task starting execution..."
        data = {
            'status': 'active',
            'message': 'Task Executing in cloud'
        }
        updateEntry(task_id, data, "stochss")
        result = {
            'uuid': task_id
        }
        paramstr =  params['paramstring']
        output_dir = "output/{0}".format(task_id)
        create_dir_str = "mkdir -p {0}".format(output_dir) #output_dir+"/result"
        print create_dir_str
        os.system(create_dir_str)
        # Write files
        model_file_name = "{0}/model-{1}.R".format(output_dir, task_id)
        f = open(model_file_name, 'w')
        f.write(params['model_file'])
        f.close()
        model_data_file_name = "{0}/model-data-{1}.txt".format(output_dir, task_id)
        f = open(model_data_file_name, 'w')
        f.write(params['model_data'])
        f.close()
        # Start up a new process to poll commands.txt
        poll_process = Process(
            target=poll_commands,
            args=(params["queue"],)
        )
        # Need to start up another process to periodically update stdout
        # and stderr in S3 bucket.
        bucket_name = params["bucketname"]
        update_process = Process(
            target=update_s3_bucket,
            args=(task_id, bucket_name, output_dir)
        )
        # Construct execution string and call it
        exec_str = "{0}/{1} --model {2} --data {3}".format(
            MCEM2_DIR,
            params["paramstring"],
            model_file_name,
            model_data_file_name
        )
        stdout = "{0}/stdout".format(output_dir)
        stderr = "{0}/stderr".format(output_dir)
        print "Master: about to call {0}".format(exec_str)
        with open(stdout, 'w') as stdout_fh:
            with open(stderr, 'w') as stderr_fh:
                p = subprocess.Popen(
                    shlex.split(exec_str),
                    stdout=stdout_fh,
                    stderr=stderr_fh
                )
                poll_process.start()
                update_process.start()
                p.communicate()
        # Done
        poll_process.terminate()
        update_process.terminate()
        # Just send final output to S3
        tar_output_str = "tar -zcf {0}.tar {0}".format(output_dir)
        print tar_output_str
        os.system(tar_output_str)
        copy_to_s3_str = "python {0}/sccpy.py {1}.tar {2}".format(THOME, output_dir, bucket_name)
        print copy_to_s3_str
        os.system(copy_to_s3_str)
        data = {
            'status': 'finished',
            'uuid': task_id,
            'output': "https://s3.amazonaws.com/{0}/{1}.tar".format(bucket_name, output_dir)
        }
        updateEntry(task_id, data, "stochss")
    except Exception, e:
        data = {
            'status':'failed',
            'message': str(e),
            'traceback': traceback.format_exc()
        }
        updateEntry(task_id, data, "stochss")

@celery.task(name='tasks.slave_task')
def slave_task(params):
    '''
    The worker tasks for the R program, only to be called from the master_task.
    '''
    command = params["exec_str"]
    # First, we need to reconstruct the execution string with the
    # input files. We are going to reconstruct it in place and then
    # just join the segments of the array to create the final string.
    command_segments = command.split(' ')
    input_files = []
    output_files = {}
    # First, we need to worry about all of the input/output files.
    for index, segment in enumerate(command_segments):
        # For input files, the value passed is the key to use to retrieve the
        # proper file contents from the input params dictionary. We need to
        # re-write the contents to file and replace file name in command
        # string before calling executable.
        if segment == "--model":
            for file_handle in with_temp_file(input_files):
                file_handle.write(params[command_segments[index+1]])
            command_segments[index+1] = input_files[-1]
        elif segment == "--initial":
            for file_handle in with_temp_file(input_files):
                file_handle.write(params[command_segments[index+1]])
            command_segments[index+1] = input_files[-1]
        elif segment == "--final":
            for file_handle in with_temp_file(input_files):
                file_handle.write(params[command_segments[index+1]])
            command_segments[index+1] = input_files[-1]
        # For output files, we need to store the name that the master is expecting and
        # then replace it with a new temp file name
        elif segment == "--output":
            output_files["output"] = [command_segments[index+1]]
            fileint, file_name = tempfile.mkstemp(suffix=".RData")
            command_segments[index+1] = file_name
            output_files["output"].append(file_name)
        elif segment == "--stats":
            output_files["stats"] = [command_segments[index+1]]
            fileint, file_name = tempfile.mkstemp(suffix=".RData")
            command_segments[index+1] = file_name
            output_files["stats"].append(file_name)
    # Now command_segments is the correct execution string, just need to join it.
    execution_string = " ".join(command_segments)
    print execution_string
    p = subprocess.Popen(
        shlex.split(execution_string),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = p.communicate()
    # Need to send the output files back to the master now, so send them back
    # in a dictionary, where the key is the absolute file path that the master
    # is expecting and the value is the contents of the file.
    result = {}
    if "stats" in output_files:
        master_output_file = output_files["output"][0]
        slave_output_file = output_files["output"][1]
        with open(slave_output_file, 'r') as file_handle:
            result[master_output_file] = file_handle.read()
        master_stats_file = output_files["stats"][0]
        slave_stats_file = output_files["stats"][1]
        with open(slave_stats_file, 'r') as file_handle:
            result[master_stats_file] = file_handle.read()
    else:
        master_output_file = output_files["output"][0]
        slave_output_file = output_files["output"][1]
        with open(slave_output_file, 'r') as file_handle:
            result[master_output_file] = file_handle.read()
    return result

def with_temp_file(file_names):
    fileint, file_name = tempfile.mkstemp(suffix=".RData")
    file_names.append(file_name)
    with open(file_name, 'w') as file_handle:
        yield file_handle

@celery.task(name='stochss')
def task(taskid,params):
  ''' This is the actual work done by a task worker '''
  try:
        
      global THOME
      global STOCHKIT_DIR
      global ODE_DIR

      print 'task to be executed at remote location'
      print 'inside celery task method'
      data = {'status':'active','message':'Task Executing in cloud'}
      updateEntry(taskid, data, "stochss")
      res = {}
      paramstr =  params['paramstring']
      uuidstr = taskid
      res['uuid'] = uuidstr
      create_dir_str = "mkdir -p output/%s/result " % uuidstr
      os.system(create_dir_str)
      filename = "output/{0}/{0}.xml".format(uuidstr)
      f = open(filename,'w')
      f.write(params['document'])
      f.close()
      xmlfilepath = filename
      stdout = "output/%s/stdout.log" % uuidstr
      stderr = "output/%s/stderr.log" % uuidstr

      job_type = params['job_type']
      exec_str = ''
      if job_type == 'stochkit':
          # The following executiong string is of the form : stochkit_exec_str = "~/StochKit/ssa -m ~/output/%s/dimer_decay.xml -t 20 -i 10 -r 1000" % (uuidstr)
          exec_str = "{0}/{1} -m {2} --force --out-dir output/{3}/result 2>{4} > {5}".format(STOCHKIT_DIR, paramstr, xmlfilepath, uuidstr, stderr, stdout)
      elif job_type == 'stochkit_ode' or job_type == 'sensitivity':
          exec_str = "{0}/{1} -m {2} --force --out-dir output/{3}/result 2>{4} > {5}".format(ODE_DIR, paramstr, xmlfilepath, uuidstr, stderr, stdout)
      
      print "======================="
      print " Command to be executed : "
      print exec_str
      print "======================="
      print "To test if the command string was correct. Copy the above line and execute in terminal."
      timestarted = datetime.now()
      os.system(exec_str)
      timeended = datetime.now()
      
      results = os.listdir("output/{0}/result".format(uuidstr))
      if 'stats' in results and os.listdir("output/{0}/result/stats".format(uuidstr)) == ['.parallel']:
          raise Exception("The compute node can not handle a job of this size.")
      
      res['pid'] = taskid
      filepath = "output/%s//" % (uuidstr)
      absolute_file_path = os.path.abspath(filepath)
      print 'generating tar file'
      create_tar_output_str = "tar -zcvf output/{0}.tar output/{0}".format(uuidstr)
      print create_tar_output_str
      logging.debug("followig cmd to be executed %s" % (create_tar_output_str))
      bucketname = params['bucketname']
      copy_to_s3_str = "python {2}/sccpy.py output/{0}.tar {1}".format(uuidstr,bucketname,THOME)
      data = {'status':'active','message':'Task finished. Generating output.'}
      updateEntry(taskid, data, "stochss")
      os.system(create_tar_output_str)
      print 'copying file to s3 : {0}'.format(copy_to_s3_str)
      os.system(copy_to_s3_str)
      print 'removing xml file'
      removefilestr = "rm {0}".format(xmlfilepath)
      os.system(removefilestr)
      removetarstr = "rm output/{0}.tar".format(uuidstr)
      os.system(removetarstr)
      removeoutputdirstr = "rm -r output/{0}".format(uuidstr)
      os.system(removeoutputdirstr)
      res['output'] = "https://s3.amazonaws.com/{1}/output/{0}.tar".format(taskid,bucketname)
      res['status'] = "finished"
      diff = timeended - timestarted
      res['time_taken'] = "{0} seconds and {1} microseconds ".format(diff.seconds, diff.microseconds)
      updateEntry(taskid, res, "stochss")
  except Exception,e:
      expected_output_dir = "output/%s" % uuidstr
      # First check for existence of output directory
      if os.path.isdir(expected_output_dir):
          # Then we should store this in S3 for debugging purposes
          create_tar_output_str = "tar -zcvf {0}.tar {0}".format(expected_output_dir)
          os.system(create_tar_output_str)
          bucketname = params['bucketname']
          copy_to_s3_str = "python {0}/sccpy.py {1}.tar {2}".format(THOME, expected_output_dir, bucketname)
          os.system(copy_to_s3_str)
          # Now clean up
          remove_output_str = "rm {0}.tar {0}".format(expected_output_dir)
          os.system(remove_output_str)
          # Update the DB entry
          res['output'] = "https://s3.amazonaws.com/{0}/{1}.tar".format(bucketname, expected_output_dir)
          res['status'] = 'failed'
          res['message'] = str(e)
          updateEntry(taskid, res, "stochss")
      else:
          # Nothing to do here besides send the exception
          data = {'status':'failed', 'message':str(e)}
          updateEntry(taskid, data, "stochss")
      raise e
  return res


def checkStatus(task_id):
    '''
    Method takes task_id as input and returns the result of the celery task
    '''
    logging.info("checkStatus inside method with params %s", str(task_id))
    result = {}
    try:
        from celery.result import AsyncResult
        res = AsyncResult(task_id)
        logging.debug("checkStatus: result returned for the taskid = {0} is {1}".format(task_id, str(res)))
        result = res.result
        result['state'] = res.status
        if res.status == "PROGRESS":
            print 'Task in progress'
            print 'Current %d' % result['current']
            print 'Total %d' % result['total']
            result['result'] = None
        elif res.status == "SUCCESS":
            result['result'] = res.result
        elif res.status == "FAILURE":
            result['result'] = res.result 
        
    except Exception, e:
        logging.debug("checkStatus error : %s", str(e))
        result['state'] = "FAILURE"
        result['result'] = str(e)
    logging.debug("checkStatus : Exiting with result %s", str(res))
    return result


def removeTask(task_id):
    '''
    this method revokes scheduled tasks as well as the tasks in progress
    '''
    try:
        print "removeTask: with task_id: {0}".format(task_id)
        from celery.task.control import revoke
        # Celery can't use remote control (which includes revoking tasks) with SQS
        # http://docs.celeryproject.org/en/latest/getting-started/brokers/sqs.html
        revoke(task_id)#, terminate=True, signal="SIGTERM")
    except Exception,e:
        print "task {0} cannot be removed/deleted. Error : {1}".format(task_id, str(e))
        
#def describeTask():
#    i = celery.control.inspect()
#    print type(i)
#    print dir(i)
#    print str(i.active_queues())
#    print str(i.registered_tasks())
#    print str(i.stats())
#    #print str(i.registered())
#    #print str(i.active())
#    #print str(i.scheduled())

"""
All DynamoBD related methods follow next. TODO: move it to a different file
"""

def describetask(taskids,tablename):
    res = {}
    try:
        print 'inside describetask method with taskids = {0} and tablename {1}'.format(str(taskids), tablename)
        dynamo=boto.connect_dynamodb()
        if not tableexists(dynamo, tablename): return res
        table = dynamo.get_table(tablename)
        for taskid in taskids:
            try:
                item = table.get_item(hash_key=taskid)
                res[taskid] = item
            except Exception,e:
                res[taskid] = None
        return res
    except Exception,e:
        print "exiting describetask  with error : {0}".format(str(e))
        print str(e)
        return res

def removetask(tablename,taskid):
    print 'inside removetask method with tablename = {0} and taskid = {1}'.format(tablename, taskid)
    try:
        dynamo=boto.connect_dynamodb()
        if tableexists(dynamo, tablename):
            table = dynamo.get_table(tablename)
            item = table.get_item(hash_key=taskid)
            item.delete()
            return True
        else:
            print 'exiting removetask with error : table doesn\'t exists'
            return False
        
    except Exception,e:
        print 'exiting removetask with error {0}'.format(str(e))
        return False
    
def createtable(tablename=str()):
    print 'inside create table method with tablename :: {0}'.format(tablename)
    if tablename == None:
        tablename = "stochss"
        print 'default table name picked as stochss'
    try:
        print 'connecting to dynamodb'
        dynamo=boto.connect_dynamodb()
        #check if table already exisits
        print 'checking if table {0} exists'.format(tablename)
        if not tableexists(dynamo,tablename):
            print 'creating table schema'
            myschema=dynamo.create_schema(hash_key_name='taskid',hash_key_proto_value=str)
            table=dynamo.create_table(name=tablename, schema=myschema, read_units=6, write_units=4)
        else:
            print "table already exists"
        return True  
    except Exception,e:
        print str(e)
        return False

def tableexists(dynamo, tablename):
    try:
        table = dynamo.get_table(tablename)
        if table == None:
            print "table doesn't exist"
            return False
        else:
            return True
    except Exception,e:
        print str(e)
        return False

def updateEntry(taskid=str(), data=dict(), tablename=str()):
    '''
     check if entry exists
     create a entry if not or
     update the status
    '''
    try:
        print 'inside update entry method with taskid = {0} and data = {1}'.format(taskid, str(data))
        dynamo=boto.connect_dynamodb()
        if not tableexists(dynamo, tablename):
            print "invalid table name specified"
            return False
        table = dynamo.get_table(tablename)
        item = table.new_item(hash_key=str(taskid),attrs=data)
        item.put()
        return True
    except Exception,e:
        print 'exiting updatedata with error : {0}'.format(str(e))
        return False
    
if __name__ == "__main__":

    '''
    NOTE: these must be set in your environment:
    export AWS_SECRET_ACCESS_KEY=XXX
    export AWS_ACCESS_KEY_ID=YYY
    '''
    global THOME
    global STOCHKIT_DIR
    os.environ["AWS_ACCESS_KEY_ID"] = os.environ['EC2_ACCESS_KEY']
    os.environ["AWS_SECRET_ACCESS_KEY"] = os.environ['EC2_SECRET_KEY']

    print createtable('stochss')
    val = {'status':"running", 'message':'done'}
    updateEntry('1234', val, 'stochss')
    print describetask(['1234', '1234'], 'stochss')
    
    #this executes a task locally
    #NOTE: dimer_decay.xml must be in this local dir
    xmlfile = open('dimer_decay.xml','r')
    doc = xmlfile.read()
    xmlfile.close()
    taskargs = {}
    taskargs['paramstring'] = 'ssa -t 100 -i 1000 -r 100 --keep-trajectories --seed 706370 --label'
    taskargs['document'] = doc
    taskargs['bucketname'] = 'cjk1234'

    THOME=os.getcwd()
    STOCHKIT_DIR='{0}/../../StochKit'.format(THOME)
    task('1234',taskargs)
    print describetask(['1234', '1234'], 'stochss')
 
    print 'BE SURE TO GO TO YOUR AWS ADMIN CONSOLE AND DELETE DYNAMODB TABLES AND S3 BUCKETS'
    

