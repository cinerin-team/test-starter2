import argparse
import os
import subprocess
import sys
import time
from datetime import datetime

import paramiko
from cryptography.fernet import Fernet


def encrypt_password(password, key):
    f = Fernet(key)
    encrypted_password = f.encrypt(password.encode())
    return encrypted_password


def decrypt_password(encrypted_password, key):
    f = Fernet(key)
    decrypted_password = f.decrypt(encrypted_password).decode()
    return decrypted_password


def passwd_mgmnt():
    password_and_repo_path = 'configs/pass_and_repo.ini'

    # if password file is not exist, then create
    if not os.path.exists(password_and_repo_path):
        with open(password_and_repo_path, 'w') as configfile:
            configfile.write("repo: \n")
            configfile.write("username: \n")
            configfile.write("password: \n")
            configfile.write("key: " + Fernet.generate_key().decode() + "\n")
        print(
            "The config.ini is created. Please enter your username, password and epg directory in it. Do not worry! This will be encrypted on the second run.")
        sys.exit(0)

    # Configuration reading
    with open(password_and_repo_path, 'r') as configfile:
        lines = configfile.readlines()
        for i in lines:
            if i.startswith("repo"):
                repo = i.split("repo:")[1].strip()
            if i.startswith("username"):
                user = i.split("username:")[1].strip()
            if i.startswith("password"):
                password = i.split("password:")[1].strip()
            if i.startswith("key"):
                key = i.split("key:")[1].strip().encode()

    # Check if it is encrypted
    # TODO use the encrypted pass in code and decrypt when it is used
    if password.startswith('encrypted:'):
        # if yes then decrypt
        encrypted_password = password.encode()[len('encrypted:'):]
        decrypted_password = decrypt_password(encrypted_password, key)
        return {"user": user, "pass": decrypted_password, "repo": repo}
    else:
        # in not then encrypt
        encrypted_password = encrypt_password(password, key)
        password = 'encrypted:' + encrypted_password.decode()

        with open(password_and_repo_path, 'w') as configfile:
            configfile.write("repo: " + repo + "\n")
            configfile.write("username: " + user + "\n")
            configfile.write("password: " + password + "\n")
            configfile.write("key: " + key.decode('ascii') + "\n")
        decrypted_password = decrypt_password(encrypted_password, key)
        return {"user": user, "pass": decrypted_password, "repo": repo}


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
        description="use a .config file in the configs folder or the following switches. Required fields (either in config or in parameter): build ID, TC+command, node type. The command line parameter overrides the config file. For example: python runner.py -bi EPG_28R202EE1_231020_122336 -tc TC37512.4.6.11.23 -c \"go --duration=16h\" -n COTS_1_HOST_C14_U20VCPU_SRIOV -r vepg332-2 -m Dell640-18 -e \"/proj/epg_st_sandbox/ethnyz/PCEPGST-2587/epgcats240202/paths\" -d /lab/testtools/dallas/testRelease/eyuhkua/3R203B03_eyuhkua -a /lab/epg_st_utils/testtools/autott/LSV/R5A418")
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


def wait_for_prompt(channel, timeout=10):
    start_time = time.time()
    while time.time() - start_time < timeout:
        if channel.recv_ready():
            return True
        time.sleep(1)
    return False


def local_env(conf):
    output = subprocess.Popen(["queue_run2.py " + create_command(conf)],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, err = output.communicate()
    # print(out)
    out = out.replace("\"", "").replace("\'", "").replace("\n", " ")

    return out


def remote_env(conf):
    credentials = passwd_mgmnt()
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("10.63.192.69", 22, credentials["user"], credentials["pass"])

    shell = client.invoke_shell()

    # setup_workspace
    shell.send("cd " + credentials["repo"] + " && setup_workspace" + '\n')

    # wait for the prompt
    output = ''
    if wait_for_prompt(shell):
        while shell.recv_ready():
            output += shell.recv(65535).decode('utf-8')
        shell.send("queue_run2.py " + create_command(conf) + '\n')

        # wait for the results
        # TODO finetune the waiting time (10 was too short)
        time.sleep(20)
        while shell.recv_ready():
            output += shell.recv(65535).decode('utf-8')

    else:
        print("Cannot wait for the prompt.")

    shell.close()
    client.close()

    return output


def communication_and_getting_job_id(conf):
    print("executing: queue_run2.py " + create_command(conf))
    host = os.getenv('COMPUTERNAME')
    if host.startswith("seroiuts"):
        output = local_env(conf)
    else:
        output = remote_env(conf)

    output = output.replace("\"", "").replace("\'", "").replace("\n", " ")

    return output.split("Enqueued job with id: ")[1].split(" and with split")[0]


def execute_commands(command_list_loc, configs):
    for comm in command_list_loc:
        job_id = communication_and_getting_job_id(comm)
        comm["jobid"] = job_id
        configs.append(
            comm.copy())  # copy is needed because without it when we clear the actual_conf, the array item will be cleared as well

    write_out_file(configs)
