import os

from functions import local_argument_parser, aggregate_data, execute_commands

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
