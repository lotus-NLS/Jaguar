from src.lotusEngine.l3_lotus_core import Flag
# ----------------------------------------------------


seperator = '|'

def get_parsed_input(the_input : str) -> (str, list[Flag]):
    if not seperator in the_input:
        msg, flags_present = the_input, []

    else:
        msg, flag_str = the_input.split(seperator)
        flags_present = []
        for flag_type in Flag.get_all_flagtypes():
            if flag_type in flag_str:
                flags_present.append(flag_type)

    return msg, flags_present

