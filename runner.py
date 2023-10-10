import argparse
import os
import subprocess
from datetime import datetime


def create_command(config):
    result = "autott"
    if "bi" in config.keys():
        result = result + " --build-id " + config["bi"]
    if "c" in config.keys():
        result = result + " --test-case \"" + config["tc"] + " : " + config["c"] + "\""
    if "n" in config.keys():
        result = result + " --node-type " + config["n"]
    if "r" in config.keys():
        result = result + " --resource " + config["r"]
    if "m" in config.keys():
        result = result + " --constraints \'[(((autoTT == \"1\" && node_pool == \"All teams\") && node_type == \"" + \
                 config["n"] + "\") && (model == \"" + config["m"] + "\"))]\'"
    if "e" in config.keys():
        result = result + " --epgcats-path \'" + config["e"] + "\'"
    if "d" in config.keys():
        result = result + " --dallas-path \'" + config["d"] + "\'"
    if "a" in config.keys():
        result = result + " --autott-path \'" + config["a"] + "\'"

    return result


def aggregate_data(config, arg):
    result = {}
    if arg.bi is not None:
        result["bi"] = arg.bi
    elif "build" in config.keys():
        result["bi"] = config["build"]

    if arg.c is not None:
        result["c"] = arg.c
        result["tc"] = arg.tc
    elif "command" in config.keys():
        result["c"] = config["command"]
        result["tc"] = config["tc"]

    if arg.n is not None:
        result["n"] = arg.n
    elif "build" in config.keys():
        result["n"] = config["node_type"]

    if arg.r is not None:
        result["r"] = arg.r
    elif "resource" in config.keys():
        result["r"] = config["resource"]

    if arg.m is not None:
        result["m"] = arg.m
    elif "model" in config.keys():
        result["m"] = config["model"]

    if arg.e is not None:
        result["e"] = arg.e
    elif "epg_path" in config.keys():
        result["e"] = config["epg_path"]

    if arg.d is not None:
        result["d"] = arg.d
    elif "dallas-path" in config.keys():
        result["d"] = config["dallas-path"]

    if arg.a is not None:
        result["a"] = arg.a
    elif "autott-path" in config.keys():
        result["a"] = config["autott-path"]

    return result


def write_out_file(id_list):
    name = datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "-result.txt"
    of = open(name, "w")
    for item in id_list:
        of.write("---------------------")
        of.write("Build-id: " + item["bi"])
        of.write("Test Case: " + item["tc"])
        of.write("Node Type: " + item["n"])
        of.write("https://epgweb.sero.wh.rnd.internal.ericsson.com/testviewer/job/" + str(item["ji"]))
        of.write("---------------------")
    of.close()
    print("report file generated: " + name)
    of = open(name, "r")
    for one_line in of:
        print(one_line)
    of.close()


if __name__ == "__main__":
    path = "configs"
    dir_list = os.listdir(path)
    conf = {}
    job_ids = []
    actual_conf = {}
    parser = argparse.ArgumentParser(
        description="use a .config file in the configs folder or the following switches. Required fileds (either in config or in parameter): build ID, TC+command, node type. The commandline parameter overrides the config file.")
    parser.add_argument('-bi', "--build-id", dest='bi',
                        help="specific build ID should be selected, not the config file's content. for example: --build-id EPG_28R190FE1_230823_155500",
                        required=False)
    parser.add_argument('-tc', "--test-case", dest='tc',
                        help="specific TC should be executed, but use this with --command switch. for example: --test-case TC37512.4.6.11.23",
                        required=False)
    parser.add_argument('-c', "--command", dest='c',
                        help="if the TC needs a specific running command, but use this with --test-case switch. for example: --command \"go --duration=16h\"",
                        required=False)
    parser.add_argument('-n', "--node-type", dest='n',
                        help="select the node pool. for example: --node-type cots_1_host_C14_U20vcpu_sriov",
                        required=False)
    parser.add_argument('-r', "--resource", dest='r',
                        help="if there is booked node. for example: --resource epg8-4",
                        required=False)
    parser.add_argument('-m', "--model", dest='m',
                        help="in the node constraints if model should be selected. for example: --model Dell640-18",
                        required=False)
    parser.add_argument('-e', "--epgcats-path", dest='e',
                        help="for advanced configuration, to run on private EPGCATS. for example: --epgcats-path \"/lab/epg_st_logs/<user>/paths\"",
                        required=False)
    parser.add_argument('-d', "--dallas-path", dest='d',
                        help="to run on specific dallas path",
                        required=False)
    parser.add_argument('-a', "--autott-path", dest='a',
                        help="to run on specific autott path.",
                        required=False)

    args = parser.parse_args()
    for file in dir_list:
        if file.endswith(".config"):
            conf.clear()
            actual_conf.clear()
            f = open(path + "/" + file, "r")
            for line in f.readlines():
                conf[line.split(": ")[0]] = line.split(": ")[1].rstrip("\n")
            actual_conf = aggregate_data(conf, args)
            print("executing: queue_run2.py " + create_command(actual_conf))
            output = subprocess.Popen(["queue_run2.py " + create_command(actual_conf)],
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            out, err = output.communicate()
            # print(out)
            out = out.replace("\"", "").replace("\'", "").replace("\n", " ")
            job_id = out.split("Enqueued job with id: ")[1].split(" and with split")[0]
            actual_conf["ji"] = job_id
            job_ids.append(actual_conf)

    write_out_file(job_ids)
