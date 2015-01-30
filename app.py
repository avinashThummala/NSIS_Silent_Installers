#!/usr/bin/python

import os, time, subprocess, shutil
from flask import Flask, render_template, jsonify, request, send_from_directory

class MyServer(Flask):

    def __init__(self, *args, **kwargs):

        super(MyServer, self).__init__(*args, **kwargs)    

app = MyServer(__name__)
app.config.from_object(__name__)

app.config['PROBE_INSTALLER_CONFIG_FILE_PATH'] = 'ProbeInstaller/config.properties'
app.config['AGENT_INSTALLER_CONFIG_FILE_PATH'] = 'AgentInstaller/config.properties'

app.config['CallbackFinishedUrl']='http://192.168.0.105:5000/installFinished'
app.config['CallbackUnFinishedUrl']='http://192.168.0.105:5000/installIncomplete'

app.config['PROBE_INSTALLER_DIR_PATH'] = 'ProbeInstaller'
app.config['AGENT_INSTALLER_DIR_PATH'] = 'AgentInstaller'

app.config['PROBE_INSTALLER_NSI_FILE_PATH'] = 'WProbe.nsi'
app.config['AGENT_INSTALLER_NSI_FILE_PATH'] = 'WAgent.nsi'

app.config['PROBE_INSTALLER_EXE_PATH'] = 'ProbeInstaller/ProbeInstaller.exe'
app.config['AGENT_INSTALLER_EXE_PATH'] = 'AgentInstaller/AgentInstaller.exe'

@app.route("/")
def index():
    return render_template("wprobe.html")

@app.route("/wprobe")
def wprobe():
    return render_template("wprobe.html")    

@app.route("/wagent")
def wagent():
    return render_template("wagent.html")    

@app.route("/<path:filename>")
def getFile(filename):
    return send_from_directory(app.root_path + '/', filename)

@app.route('/installFinished', methods=['POST'])
def installFinished():

    if request.method == 'POST':  

        fName=request.form['param']+".exe"

        print "End user:"+request.form['param']+" wrapped up the setup"        

        if os.path.isfile(app.config['PROBE_INSTALLER_DIR_PATH']+"_"+fName):
            os.remove(app.config['PROBE_INSTALLER_DIR_PATH']+"_"+fName)

        elif os.path.isfile(app.config['AGENT_INSTALLER_DIR_PATH']+"_"+fName):
            os.remove(app.config['AGENT_INSTALLER_DIR_PATH']+"_"+fName)

        return jsonify({"success":True}) 

    return jsonify({"success":False})    

@app.route('/installIncomplete', methods=['POST'])
def installIncomplete():

    if request.method == 'POST':  

        fName=request.form['param']+".exe"    	

        print "End user:"+request.form['param']+" couldn't get the installation to work"

        if os.path.isfile(app.config['PROBE_INSTALLER_DIR_PATH']+"_"+fName):
            os.remove(app.config['PROBE_INSTALLER_DIR_PATH']+"_"+fName)

        elif os.path.isfile(app.config['AGENT_INSTALLER_DIR_PATH']+"_"+fName):
            os.remove(app.config['AGENT_INSTALLER_DIR_PATH']+"_"+fName)       

        return jsonify({"success":True}) 

    return jsonify({"success":False})             

@app.route('/probeUploadInfo', methods=['POST'])
def probeUploadInfo():

    if request.method == 'POST':

        try:

            command="/s /v /qn "  

            for key, value in request.form.items():
                command+=(key+"="+value+" ")

            param=str(int(time.time()))
            fName="ProbeInstaller_"+param+".exe"

            with open(app.config['PROBE_INSTALLER_CONFIG_FILE_PATH'], 'w') as cFile:

                cFile.write("Command="+command+"\n")

                cFile.write("CallbackFinishedUrl="+app.config['CallbackFinishedUrl']+"\n")
                cFile.write("CallbackUnFinishedUrl="+app.config['CallbackUnFinishedUrl']+"\n")

                cFile.write("Param="+param+"\n") 

            with open(os.devnull, "w") as fnull:

                os.chdir(app.config['PROBE_INSTALLER_DIR_PATH'])                    

                proc = subprocess.Popen(["makensis", app.config['PROBE_INSTALLER_NSI_FILE_PATH']], stdout = fnull, stderr = fnull)
                proc.communicate()

                if proc.returncode!=0:
                    return jsonify({"fName":"-1"})   

                else:
                    os.chdir("..")
                    shutil.move( app.config['PROBE_INSTALLER_EXE_PATH'], fName)                                                                      

            return jsonify({"fName":"/"+fName})            

        except:
            return jsonify({"fName":"-1"})                                            

    return jsonify({"success":False})    

@app.route('/agentUploadInfo', methods=['POST'])
def agentUploadInfo():

    if request.method == 'POST':

        try:
            command="/s /v /qn "  

            for key, value in request.form.items():
                command+=(key+"="+value+" ")
                
            param=str(int(time.time()))
            fName="AgentInstaller_"+param+".exe"

            with open(app.config['AGENT_INSTALLER_CONFIG_FILE_PATH'], 'w') as cFile:

                cFile.write("Command="+command+"\n")

                cFile.write("CallbackFinishedUrl="+app.config['CallbackFinishedUrl']+"\n")
                cFile.write("CallbackUnFinishedUrl="+app.config['CallbackUnFinishedUrl']+"\n")

                cFile.write("Param="+param+"\n") 

            with open(os.devnull, "w") as fnull:

                os.chdir(app.config['AGENT_INSTALLER_DIR_PATH'])

                proc = subprocess.Popen(["makensis", app.config['AGENT_INSTALLER_NSI_FILE_PATH']], stdout = fnull, stderr = fnull)
                proc.communicate()
                            
                if proc.returncode!=0:                        
                    return jsonify({"fName":"-1"})                                    

                else:           
                    os.chdir("..")
                    shutil.move( app.config['AGENT_INSTALLER_EXE_PATH'], fName)                                                                     

            return jsonify({"fName":"/"+fName})            

        except:                    
            return jsonify({"fName":"-1"})                                

    return jsonify({"success":False})     

if __name__ == "__main__":
	
	port = int(os.environ.get('PORT', 5000)) 
	app.run(host='0.0.0.0', port=port)	
