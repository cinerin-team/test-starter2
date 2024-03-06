import argparse
import os
import subprocess
from datetime import datetime


def create_command(config):
    result = "autott"
    if "buildid" in config.keys():
        result = result + " --build-id " + config["buildid"]
    if "testcase" in config.keys():
        result = result + " --test-case \"" + config["testcase"] + " : " + config["command"] + "\""
    if "node_type" in config.keys():
        result = result + " --node-type " + config["node_type"]
    if "resource" in config.keys():
        result = result + " --resource " + config["resource"]
    if "model" in config.keys():
        result = result + " --constraints \'[(((autoTT == \"1\" && node_pool == \"All teams\") && node_type == \"" + \
                 config["node_type"] + "\") && (model == \"" + config["model"] + "\"))]\'"
    if "epgpath" in config.keys():
        result = result + " --epgcats-path \'" + config["epgpath"] + "\'"
    if "dallaspath" in config.keys():
        result = result + " --dallas-path \'" + config["dallaspath"] + "\'"
    if "autottpath" in config.keys():
        result = result + " --autott-path \'" + config["autottpath"] + "\'"

    return result


def aggregate_data(config, arg):
    result = {}
    if arg.bi is not None:
        result["buildid"] = arg.bi
    elif "build" in config.keys():
        result["buildid"] = config["build"]

    if arg.c is not None:
        result["command"] = arg.c
        result["testcase"] = arg.tc
    elif "command" in config.keys():
        result["command"] = config["command"]
        result["testcase"] = config["tc"]

    if arg.n is not None:
        result["node_type"] = arg.n
    elif "build" in config.keys():
        result["node_type"] = config["node_type"]

    if arg.r is not None:
        result["resource"] = arg.r
    elif "resource" in config.keys():
        result["resource"] = config["resource"]

    if arg.m is not None:
        result["model"] = arg.m
    elif "model" in config.keys():
        result["model"] = config["model"]

    if arg.e is not None:
        result["epgpath"] = arg.e
    elif "epg_path" in config.keys():
        result["epgpath"] = config["epgpath"]

    if arg.d is not None:
        result["dallaspath"] = arg.d
    elif "dallas-path" in config.keys():
        result["dallaspath"] = config["dallaspath"]

    if arg.a is not None:
        result["autottpath"] = arg.a
    elif "autott-path" in config.keys():
        result["autottpath"] = config["autottpath"]

    return result


def write_out_file(config_list):
    name = datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "-result.txt"
    of = open(name, "w")
    for item in config_list:
        of.write("---------------------\n")
        of.write("Build-id: " + item["buildid"] + "\n")
        of.write("Test Case: " + item["testcase"] + "\n")
        of.write("Node Type: " + item["node_type"] + "\n")
        of.write("https://epgweb.sero.wh.rnd.internal.ericsson.com/testviewer/job/" + str(item["jobid"]) + "\n")
        of.write("---------------------\n")
    of.close()
    print("report file generated: " + name)
    of = open(name, "r")
    for one_line in of:
        print(one_line)
    of.close()


def local_argument_parser():
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
                        help="to run on specific dallas path, for example: --dallas-path /lab/testtools/dallas/testRelease/eyuhkua/3R203B03_eyuhkua",
                        required=False)
    parser.add_argument('-a', "--autott-path", dest='a',
                        help="to run on specific autott path.",
                        required=False)

    return parser.parse_args()


def communication_and_getting_job_id(conf):
    print("executing: queue_run2.py " + create_command(conf))
    output = subprocess.Popen(["queue_run2.py " + create_command(conf)],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, err = output.communicate()
    # print(out)
    out = out.replace("\"", "").replace("\'", "").replace("\n", " ")

    return out.split("Enqueued job with id: ")[1].split(" and with split")[0]


def execute_commands(command_list_loc, configs):
    for comm in command_list_loc:
        job_id = communication_and_getting_job_id(comm)
        comm["jobid"] = job_id
        configs.append(
            comm.copy())  # copy is needed because without it when we clear the actual_conf, the array item will be cleared as well

    write_out_file(configs)


if __name__ == "__main__":
    path = "configs"
    dir_list = os.listdir(path)
    conf_file_content = {}
    configs = []
    actual_conf = {}
    command_list = []

    argument_line_content = local_argument_parser()
    file_counter = 0
    for file in dir_list:
        if file.endswith(".config"):
            conf_file_content.clear()
            actual_conf.clear()
            f = open(path + "/" + file, "r")
            for line in f.readlines():
                conf_file_content[line.split(": ")[0]] = line.split(": ")[1].rstrip("\n")
        actual_conf = aggregate_data(conf_file_content, argument_line_content)
        command_list.append(actual_conf.copy())
        file_counter += 1

    if file_counter == 0:
        actual_conf = aggregate_data(conf_file_content, argument_line_content)
        command_list.append(actual_conf)

    execute_commands(command_list, configs)
