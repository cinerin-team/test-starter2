import os
import subprocess
from datetime import datetime

path = "configs"
dir_list = os.listdir(path)
conf = {}
job_ids = []


def create_command(param):
    result = "autott"
    if "build" in param.keys():
        result = result + " --build-id " + param["build"]
    if "tc" in param.keys() and "command" in param.keys():
        result = result + " --test-case \"" + param["tc"] + " : " + param["command"] + "\""
    if "node_type" in param.keys():
        result = result + " --node-type " + param["node_type"]
    if "resource" in param.keys():
        result = result + " --resource " + param["resource"]
    if "model" in param.keys():
        result = result + " --constraints \'[(model == \"" + param["model"] + "\")]\'"

    return result


def write_out_file(id_list):
    of = open(datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "-result.txt", "w")
    for item in id_list:
        of.write(str(item) + ", ")
    of.close()


for file in dir_list:
    if file.endswith(".config"):
        conf.clear()
        f = open(path + "/" + file, "r")
        for line in f.readlines():
            conf[line.split(": ")[0]] = line.split(": ")[1].rstrip("\n")

        output = subprocess.Popen(["queue_run2.py " + create_command(conf)],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, err = output.communicate()
        print(str(out))
        # mo = re.match(r'\w+Enqueued job with id: (\w{8}) \w+', str(out))
        # if mo:
        #     job_ids.append(mo.group(1))

write_out_file(job_ids)
