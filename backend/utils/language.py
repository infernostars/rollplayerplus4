def list_format(input_list):
    """
    Formats a list for English.
    """
    if len(input_list) == 0:
        return "nothing"
    if len(input_list) == 1:
        return str(input_list[0])
    if len(input_list) == 2:
        return f"{input_list[0]} and {input_list[1]}"
    else:
        return ", ".join(input_list[:-1])+f", and {input_list[-1]}"