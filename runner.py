import os
import subprocess
import sys
from datetime import datetime

path = "configs"
dir_list = os.listdir(path)
conf = {}
job_ids = []


def create_command(param, args):
    result = "autott"
    if "build" in param.keys() or len(args) == 2:
        if len(args) == 2:
            result = result + " --build-id " + args[1]
        else:
            result = result + " --build-id " + param["build"]
    if "tc" in param.keys() and "command" in param.keys():
        result = result + " --test-case \"" + param["tc"] + " : " + param["command"] + "\""
    if "node_type" in param.keys():
        result = result + " --node-type " + param["node_type"]
    if "resource" in param.keys():
        result = result + " --resource " + param["resource"]
    if "model" in param.keys():
        result = result + " --constraints \'[(((autoTT == \"1\" && node_pool == \"All teams\") && node_type == \"" + \
                 param["node_type"] + "\") && (model == \"" + param["model"] + "\"))]\'"
    if "epg_path" in param.keys():
        result = result + " --epgcats-path \'" + param["epg_path"] + "\'"
    if "dallas-path" in param.keys():
        result = result + " --dallas-path \'" + param["dallas-path"] + "\'"
    if "autott-path" in param.keys():
        result = result + " --autott-path \'" + param["autott-path"] + "\'"

    return result


def write_out_file(id_list):
    name = datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "-result.txt"
    of = open(name, "w")
    for item in id_list:
        of.write("https://epgweb.sero.wh.rnd.internal.ericsson.com/testviewer/job/" + str(item) + "\n")
    of.close()
    print("report file generated: " + name)


for file in dir_list:
    if file.endswith(".config"):
        conf.clear()
        f = open(path + "/" + file, "r")
        for line in f.readlines():
            conf[line.split(": ")[0]] = line.split(": ")[1].rstrip("\n")
        print("executing: queue_run2.py " + create_command(conf, sys.argv))
        output = subprocess.Popen(["queue_run2.py " + create_command(conf, sys.argv)],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, err = output.communicate()
        # print(out)
        out = out.replace("\"", "").replace("\'", "").replace("\n", " ")
        job_id = out.split("Enqueued job with id: ")[1].split(" and with split")[0]
        job_ids.append(job_id)

write_out_file(job_ids)
