from functions import process_collected_commands_from_files_or_commandline, collect_commands

if __name__ == "__main__":
    path = "configs"
    command_list = collect_commands(path)

    process_collected_commands_from_files_or_commandline(command_list)
