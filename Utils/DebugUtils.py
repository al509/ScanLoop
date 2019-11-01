DEBUG = 0


def print_dictionary(dictionary):
    if not DEBUG:
        return

    print("{:<16} {:<16}".format('Key', 'Value'))
    for k, v in dictionary.items():
        print("{:<16} {:<16}".format(k, v))


def print_func_info(name, args_dict):
    if not DEBUG:
        return

    print("####################")
    print(name)
    try:
        print_dictionary(args_dict)
    except TypeError:
        print(args_dict)
    print("####################")


def print_method_info(name, args_dict):
    print_func_info(name, {key: args_dict[key] for key in args_dict if key != "DebugUtils" and key != "self"})


if __name__ == "__main__":
    d = {"asd": 1, "aaaa": 2}
    print_dictionary(d)
