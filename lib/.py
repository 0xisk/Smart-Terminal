from warnings import catch_warnings , simplefilter;
from sklearn.externals.joblib import load;
from dill import load as cload;
from subprocess import Popen , PIPE;
from warnings import catch_warnings , simplefilter;
from normalize import normalizeQuery;
from os import system;
from sys import path;
from tempfile import NamedTemporaryFile;
from monitor.analysis import Collect;


classes=['amixer -D pulse sset Master 50%+', 'amixer -D pulse sset Master 50%-', 'cal', 'cal -y', 'date', 'hostname -i', 'mkdir','mkdir -m 777', 'pkill', 'poweroff', 'reboot', 'systemctl suspend','uname -a', 'uptime -p', 'whoami', 'eject', 'rm', 'rm -r','uptime -p']


with catch_warnings(record=True)  :
	simplefilter("always")
	model   = load("../models/model.bin");
	feature = load("../models/feature.bin");
	correction = cload(open("../models/correction.bin" , "rb"));


class Run :

	@staticmethod
	def _run(command , password=None) :
		if password != None :
			command = command.replace("sudo","echo {0} | sudo -S ".format(password), 1)#first occurance
		result = Popen(command , shell = True,stdout=PIPE,stderr=PIPE,stdin=PIPE)
		output , err = result.communicate()	
		if result.returncode != 0 : raise ValueError("the query <{0}> can't work correctly".format(command))
		return output.decode("utf-8")

	def _predict(self, query) :
		(query , quotedwords) = normalizeQuery(query , 0.55 , correction);
		query = [" ".join(query)];
		t_data  = feature.transform(query).toarray()
		result  = model.predict(t_data)
		result  = result[0]
		cmd = classes[result];
		
		return (cmd  , " ".join(quotedwords));


	def exec(self, query) :
		command = self._predict(query);
		try :
			output = self._run(command[0] + " " + command[1])
		except : 
			return "sorry your command can't be executed correctly";
		else :
			if command[0] in ['cal', 'cal -y', 'date', 'hostname -i','uname -a', 'uptime -p', 'whoami','uptime -p'] :
				return (output.strip() , command[0]);
			elif command[0] == 'amixer -D pulse sset Master 50%+' : return ("the sound has raised 50%" , command[0])
			elif command[0] == 'amixer -D pulse sset Master 50%-' : return ("the sound has lowed 50%" , command[0])
			elif command[0] == 'eject' : return ("your cd-rom has opened" , command[0])
			elif command[0] in ['mkdir','mkdir -m 777'] : return ("a new folder is created with name {0}".format(command[1]) , command[0])
			elif command[0] == "pkill" : return ("the process {0} is closed".format(command[1]) , command[0])
			elif command[0] == "poweroff" : return ("the computer is turing off now" , command[0])
			elif command[0] == "reboot" : return ("your computer will restart shortly" , command[0])
			elif command[0] == "systemctl suspend" : return ("your machine will sleep now" , command[0])
			elif command[0] in ["rm" , "rm -r"] : return ("{0} has deleted".format(command[1]) , command[0])


	def showTrackingData(self , days=7) :
		data = Collect(days).calculate();
		tempFile = NamedTemporaryFile(mode="w" , suffix=".dat");
		if data == {} : 
			tempFile.write(" ");
			tempFile.close();
			return;
		for label in data :
			tempFile.write("{0} {1}\n".format(label , data[label])); 
		tempFile.flush();
		system("termgraph {0}".format(tempFile.name));
		tempFile.close();




if __name__ == "__main__" : 
	# print(Run().exec('show my '))
	pass;