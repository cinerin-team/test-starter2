import os
import subprocess

path = "configs"
dir_list = os.listdir(path)
conf = {}


def create_command(param):
    result = "autott"
    if "build" in param.keys():
        result = result + " --build-id " + param["build"]
    if "tc" in param.keys() and "constraints" in param.keys():
        result = result + " --test-case \"" + param["tc"] + " : " + param["constraints"] + "\""
    if "node_type" in param.keys():
        result = result + " --node-type " + param["node_type"]

    return result


for file in dir_list:
    conf.clear()
    f = open(path + "/" + file, "r")
    for line in f.readlines():
        conf[line.split(": ")[0]] = line.split(": ")[1].rstrip("\n")

    output = subprocess.Popen(["queue_run2.py", create_command(conf)],
                              stdout=subprocess.PIPE)
    out, err = output.communicate()
    print(out)
    print(err)
