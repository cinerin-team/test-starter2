import argparse
import os
import subprocess
import sys
from datetime import datetime


def create_command(param, arg):
    result = "autott"
    if "build" in param.keys() or arg.bi != "":
        if arg.bi != "":
            result = result + " --build-id " + arg.bi
        else:
            result = result + " --build-id " + param["build"]
    if ("tc" in param.keys() and "command" in param.keys()) or (arg.tc != "" and arg.c != ""):
        if arg.tc != "":
            result = result + " --test-case \"" + arg.tc + " : " + arg.c + "\""
        else:
            result = result + " --test-case \"" + param["tc"] + " : " + param["command"] + "\""
    if "node_type" in param.keys() or arg.n != "":
        if arg.n != "":
            result = result + " --node-type " + arg.n
        else:
            result = result + " --node-type " + param["node_type"]
    if "resource" in param.keys() or arg.r != "":
        if arg.r != "":
            result = result + " --resource " + arg.r
        else:
            result = result + " --resource " + param["resource"]
    if "model" in param.keys() or arg.m != "":
        if arg.m != "":
            result = result + " --constraints \'[(((autoTT == \"1\" && node_pool == \"All teams\") && node_type == \"" + \
                     arg.n + "\") && (model == \"" + arg.m + "\"))]\'"
        else:
            result = result + " --constraints \'[(((autoTT == \"1\" && node_pool == \"All teams\") && node_type == \"" + \
                     param["node_type"] + "\") && (model == \"" + param["model"] + "\"))]\'"
    if "epg_path" in param.keys() or arg.e != "":
        if arg.e != "":
            result = result + " --epgcats-path \'" + arg.e + "\'"
        else:
            result = result + " --epgcats-path \'" + param["epg_path"] + "\'"
    if "dallas-path" in param.keys() or arg.d != "":
        if arg.d != "":
            result = result + " --dallas-path \'" + arg.d + "\'"
        else:
            result = result + " --dallas-path \'" + param["dallas-path"] + "\'"
    if "autott-path" in param.keys() or arg.a:
        if arg.a != "":
            result = result + " --autott-path \'" + arg.a + "\'"
        else:
            result = result + " --autott-path \'" + param["autott-path"] + "\'"

    return result


def write_out_file(id_list):
    name = datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "-result.txt"
    of = open(name, "w")
    for item in id_list:
        of.write("https://epgweb.sero.wh.rnd.internal.ericsson.com/testviewer/job/" + str(item) + "\n")
    of.close()
    print("report file generated: " + name)


if __name__ == "__main__":
    path = "configs"
    dir_list = os.listdir(path)
    conf = {}
    job_ids = []
    parser = argparse.ArgumentParser(
        description="use a .config file in the configs folder or the following switches. Required fileds (either in config or in parameter): build ID, TC+command, node type. The stronger is the commandline parameter to the config file.")
    parser.add_argument('-bi', "--build-id",
                        help="specific build ID should be selected, not the config file's content. for example: --build-id EPG_28R190FE1_230823_155500",
                        required=False)
    parser.add_argument('-tc', "--test-case",
                        help="specific TC should be executed, but use this with --command switch. for example: --test-case TC37512.4.6.11.23",
                        required=False)
    parser.add_argument('-c', "--command",
                        help="if the TC needs a specific running command, but use this with --test-case switch. for example: --command \"go --duration=16h\"",
                        required=False)
    parser.add_argument('-n', "--node-type",
                        help="select the node pool. for example: --node-type cots_1_host_C14_U20vcpu_sriov",
                        required=False)
    parser.add_argument('-r', "--resource",
                        help="if there is booked node. for example: --resource epg8-4",
                        required=False)
    parser.add_argument('-m', "--model",
                        help="in the node constraints if model should be selected. for example: --model Dell640-18",
                        required=False)
    parser.add_argument('-e', "--epgcats-path",
                        help="for advanced configuration, to run on private EPGCATS. for example: --epgcats-path \"/lab/epg_st_logs/<user>/paths\"",
                        required=False)
    parser.add_argument('-d', "--dallas-path",
                        help="to run on specific dallas path",
                        required=False)
    parser.add_argument('-a', "--autott-path",
                        help="to run on specific autott path.",
                        required=False)

    args = parser.parse_args()
    for file in dir_list:
        if file.endswith(".config"):
            conf.clear()
            f = open(path + "/" + file, "r")
            for line in f.readlines():
                conf[line.split(": ")[0]] = line.split(": ")[1].rstrip("\n")
            print("executing: queue_run2.py " + create_command(conf, args))
            output = subprocess.Popen(["queue_run2.py " + create_command(conf, args)],
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            out, err = output.communicate()
            # print(out)
            out = out.replace("\"", "").replace("\'", "").replace("\n", " ")
            job_id = out.split("Enqueued job with id: ")[1].split(" and with split")[0]
            job_ids.append(job_id)

    write_out_file(job_ids)
