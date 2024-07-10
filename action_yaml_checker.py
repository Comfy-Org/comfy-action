"""
This python script helps check if action yaml files have step names and the
windows actions are lining up with the unix actions.

e.g. > python action_yaml_checker.py action.yml

"""
import yaml
from tabulate import tabulate
import argparse
import textwrap

parser = argparse.ArgumentParser(description="Check if action yaml files have step names and if windows actions are aligned with unix actions.")
parser.add_argument("-c", "--complete", action="store_true", help="Include complete step information")
parser.add_argument(
    "-k", "--key", type=str, default="run", help="Include complete step information"
)
parser.add_argument(
    "--fallback-key", type=str, default="", help="Include complete step information"
)
parser.add_argument("yaml_file", help="Path to the YAML file")

def wrap_text(text, max_width=100):
    """
    Wraps the text to a specified max width for each line.

    Args:
    text (str): The input text to be wrapped.
    max_width (int): The maximum width of each line.

    Returns:
    str: The wrapped text.
    """
    # Split the text into lines
    lines = text.split('\n')

    # Wrap each line and join them with newline characters
    wrapped_lines = [textwrap.fill(line, max_width) for line in lines]
    wrapped_text = '\n'.join(wrapped_lines)

    return wrapped_text

def conditional_zip(x, y, step_name_extra_info_map, complete: bool = False):
    combined_list = []
    i = 0  # Pointer for x
    j = 0  # Pointer for y
    while i < len(x) or j < len(y):

        x_curr = x[i] if i < len(x) else ''
        y_curr = y[j] if j < len(y) else ''

        x_runs = step_name_extra_info_map[x_curr] if x_curr != "" else ""
        y_runs = step_name_extra_info_map[y_curr] if y_curr != "" else ""

        if '-Only]' in x_curr:
            if complete:
                x_curr = x_curr + '\n' + x_runs
            combined_list.append([x_curr, ''])
            i += 1
            continue
        if '-Only]' in y_curr:
            if complete:
                y_curr = y_curr + '\n' + y_runs
            combined_list.append(['', y_curr])
            j += 1
            continue
        if complete:
            x_curr = x_curr + '\n' + x_runs
            y_curr = y_curr + '\n' + y_runs
        combined_list.append([x_curr, y_curr])
        i += 1
        j += 1

    return combined_list


def get_step_names(
    yaml_file, complete: bool = False, step_key: str = "run", fallback_key: str = ""
):
    with open(yaml_file, 'r') as file:
        data = yaml.safe_load(file)

    steps = data['runs']['steps']

    for step in steps:
        if 'name' not in step:
            raise Exception("Step name not found in the action file: {}".format(step))

    step_name_extra_info_map = {}

    step_names = [step['name'] for step in steps if '[Universal]' not in step['name']]
    unix_step_names = []
    wins_step_names = []
    for step in steps:
        if '[Unix' in step['name']:
            unix_step_names.append(step['name'])

        if '[Win' in step['name']:
            wins_step_names.append(step['name'])
        step_name_extra_info_map[step["name"]] = wrap_text(
            step[step_key]
            if step_key in step
            else step.get(
                fallback_key if fallback_key != "" else "lalala", "[Not Info]"
            )
        )

    if len(unix_step_names) + len(wins_step_names) != len(step_names):
        uncategorized_steps = set(step_names) - set(unix_step_names + wins_step_names)
        raise Exception("There steps are not categorized: {}".format(uncategorized_steps))

    tabulated_list = conditional_zip(
        unix_step_names, wins_step_names, step_name_extra_info_map, complete=complete
    )

    print(tabulate(tabulated_list, headers=['Unix', 'Windows'], tablefmt='fancy_grid'))


if __name__ == "__main__":
    args = parser.parse_args()

    yaml_file = args.yaml_file
    get_step_names(
        yaml_file, args.complete, step_key=args.key, fallback_key=args.fallback_key
    )
