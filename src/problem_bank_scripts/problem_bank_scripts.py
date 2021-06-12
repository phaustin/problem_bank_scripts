# Author: Firas Moosvi and Graham Bovett
# Date: 2021-05-09
# This file contains many helper functions that will be used across the question bank project.

from docopt import docopt

# Imports
## Loading and Saving files & others
import uuid
import json
from . import prairielearn as pl
import pathlib
import sys
import numpy as np
import os
from collections import defaultdict
from shutil import copy2
import re

## Parse Markdown
from markdown_it import MarkdownIt # pip install markdown-it-py 
from mdformat.renderer import MDRenderer # pip install mdformat

## Dealing with YAML
import yaml

# Start of reading/parsing functions

def defdict_to_dict(defdict, finaldict):
    """Convert a defaultdict (nested) to a regular dictionary.
        - Answer copied from: https://stackoverflow.com/a/61133504/2217577
    Args:
        defdict (dict): defaultdict
        finaldict (dict): regular dictionary

    Returns:
        dict: Convert to regular dictionary
    """
    # pass in an empty dict for finaldict
    for k, v in defdict.items():
        if isinstance(v, defaultdict):
            # new level created and that is the new value
            finaldict[k] = defdict_to_dict(v, {})
        else:
            finaldict[k] = v
    return finaldict

def split_body_parts(num_parts,body_parts):
    """Parses individual question parts and splits out titles, and content

    Args:
        num_parts (int): An integer corresponding to the number of question parts (from `read_md_problem()`).
        body_parts (dict): A dictionary from `read_md_problem()`.

    Returns:
        body_parts_dict (dict): returns a nested dictionary with title,content,answer keys .
    """
    mdit = MarkdownIt()
    env = {}
    nested_dict = lambda: defaultdict(nested_dict)

    parts_dict = nested_dict()

    for pnum in range(1,num_parts+1):

        part = 'part'+f'{pnum}'
        # Set up tokens by parsing the md file
        tokens = mdit.parse(body_parts[part], env)

        ptt = [i for i,j in enumerate(tokens) if j.tag=='h2']
        parts_dict[part]['title'] = MDRenderer().render(tokens[ptt[0]+1:ptt[1]], mdit.options, env).strip('\n')

        pa = [i for i,j in enumerate(tokens) if j.tag=='h3']

        try:
            parts_dict[part]['answer']['title'] = MDRenderer().render(tokens[pa[0]+1:pa[1]], mdit.options, env)
        except IndexError:
            print("Check the heading levels, is there one that doesn't belong? Or is the heading level incorrect? For e.g., it should be ### Answer Section (this is not necessarily where the issue is).")
            raise

        parts_dict[part]['content'] = MDRenderer().render(tokens[ptt[1]+1:pa[0]], mdit.options, env)
        parts_dict[part]['answer']['content'] = MDRenderer().render(tokens[pa[1]+1:], mdit.options, env)

        # Remove parts from body_parts
        body_parts.pop(part)

    # Deal with other headings: pl-submission-panel and pl-answer-panel

    for key in body_parts.keys():
        if key in ['pl-submission-panel','pl-answer-panel']:
            # Set up tokens by parsing the md file
            tokens = mdit.parse(body_parts[key], env)

            ptt = [i for i,j in enumerate(tokens) if j.tag=='h2']
            parts_dict[key] = MDRenderer().render(tokens[ptt[-1]+1:], mdit.options, env)  

    return defdict_to_dict(parts_dict,{})

def read_md_problem(filepath):
    """Reads a MystMarkdown problem file and returns a dictionary of the header and body

    Args:
        filepath (str): Path of file to read.

    Returns:
        dict: In this dictionary there are three keys containing useful portions of the parsed md file: 
            - `header` - Header of the problem file (nested dictionary).
            - `body_parts` - Body text of the problem file (nested dictionary).
            - `num_parts` - Number of parts in the problem (integer).
    """

    mdtext = pathlib.Path(filepath).read_text()

    # Deal with YAML header
    header_text = mdtext.rsplit('---\n')[1]
    header = yaml.safe_load('---\n' + header_text)

    # Deal with Markdown Body
    body = mdtext.rsplit('---\n')[2]
    
    # Set up the markdown parser
    # to be honest, not fully sure what's going on here, see this issue: https://github.com/executablebooks/markdown-it-py/issues/164

    mdit = MarkdownIt()
    env = {}

    # Set up tokens by parsing the md file
    tokens = mdit.parse(body, env)

    blocks = {}

    block_count = 0

    num_titles = 0

    for x,t in enumerate(tokens):

        if t.tag == 'h1' and t.nesting == 1: # title
            # oh boy. this is going to break and it will be your fault firas.
            blocks['title'] = [x,x+3]
            num_titles += 1

        elif t.tag == 'h2' and t.nesting == 1:
            block_count += 1

            if block_count == 1:
                blocks['block{0}'.format(block_count)] = [x,]
            else:
                blocks['block{0}'.format(block_count-1)].append(x)
                blocks['block{0}'.format(block_count)] = [x,]

    # Add -1 to the end of the last block
    blocks['block{0}'.format(block_count)].append(len(tokens))

    # Assert statements (turn into tests!)
    assert num_titles == 1, "I see {0} Level 1 Headers (#) in this file, there should only be one!".format(num_titles)
    assert block_count >= 1, "I see {0} Level 2 Headers (##) in this file, there should be at least 1".format(block_count -1)

    # Add the end of the title block; # small hack
    #blocks['title'].append(blocks['block1'][0])

    # Get the preamble before the parts start
    blocks['preamble'] = [blocks['title'][1],blocks['block1'][0]]

    ## Process the blocks into markdown

    body_parts = {}

    part_counter = 0

    for k,v in blocks.items():

        rendered_part = MDRenderer().render(tokens[v[0]:v[1]], mdit.options, env)

        if k == 'title':
            body_parts['title'] = rendered_part
        
        elif k == 'preamble':
            body_parts['preamble'] = rendered_part

        elif 'Rubric' in rendered_part:
            body_parts['Rubric'] = rendered_part

        elif 'Solution' in rendered_part:
            body_parts['Solution'] = rendered_part

        elif 'Comments' in rendered_part:
            body_parts['Comments'] = rendered_part

        elif 'pl-submission-panel' in rendered_part:
            body_parts['pl-submission-panel'] = rendered_part

        elif 'pl-answer-panel' in rendered_part:
            body_parts['pl-answer-panel'] = rendered_part

        else:
            part_counter +=1
            body_parts['part{0}'.format(part_counter)] = rendered_part
    
    return defdict_to_dict({'header': header,
            'body_parts': body_parts,
            'num_parts': part_counter,
            'body_parts_split': split_body_parts(part_counter,body_parts) },{})

def dict_to_md(md_dict, remove_keys = [None,]):
    """ Takes a nested dictionary (e.g. output of read_md_problem()) and returns a multi-line string  that can be written to a file (after removing specified keys).   
    Args:
        md_dict (dict): A nested dictionary, for e.g. the output of `read_md_problem()`
        remove_keys (list, optional): Any keys to remove from the dictionary, for instance solutions. Defaults to [None,].

    Returns:
        str: A multi-line string that can be written to a file.
    """

    md_string = ""

    md_dict = defdict_to_dict(md_dict,{})

    for k,v in md_dict.items():
        if k in remove_keys:
            continue
        else:
            md_string += md_dict[k]

    return md_string

## Functions from md-to-pl

def write_info_json(output_path, parsed_question):
    """
    Args:
        output_path (Path): [description]
        parsed_question (dict]): [description]
    """

    pathlib.Path(output_path / 'info.json').write_text("""{
            "uuid": \"""" + str(uuid.uuid4()) + """\",
            "title": \"""" + parsed_question['header']['title'] + """",
            "topic": \"""" + parsed_question['header']['topic'] + """",
            "tags":  """ + json.dumps(parsed_question['header']['tags']) + """,
            "type": "v3"
        }""")

def write_server_py(output_path,parsed_question):
    """
    Args:
        output_path ([type]): [description]
        parsed_question ([type]): [description]
    """
    
    server_dict = parsed_question['header']['server']
    
    server_file = f""""""
    
    server_file += server_dict.pop('imports',None) + '\n'
    
    try:
        for function, code in server_dict.items():
            indented_code = code.replace('\n','\n    ')
            if code:
                server_file += f"def {function}(data):\n    {indented_code}\n"
    except:
        raise

    # Deal with path differences when using PL
    server_file = server_file.replace('read_csv("','read_csv(data["options"]["client_files_course_path"]+"/')

    # Write server.py
    (output_path / "server.py").write_text(server_file)

def process_multiple_choice(part_name,parsed_question, data_dict):
    """Processes markdown format multiple-choice questions and returns PL HTML
    Args:
        output_path (Path): [description]
        parsed_question (dict): [description]
        data_dict (dict)
    
    Returns:
        str: Multiple choice question is returned as a string with PL-compliant syntax.
    """

    html = f"""<pl-question-panel>\n<markdown>{parsed_question['body_parts_split'][part_name]['content']}</markdown>\n</pl-question-panel>\n\n"""
    
    pl_customizations = " ".join([f'{k} = "{v}"' for k,v in parsed_question['header'][part_name]['pl-customizations'].items()]) # PL-customizations
    html += f"""<pl-multiple-choice answers-name="{part_name}_ans" {pl_customizations} >\n"""

    if data_dict['params'][f'vars']['units']:
        units = f"|@ params.vars.units @|"
    else:
        units = ''

    for a in data_dict['params'][f'{part_name}'].keys():
        if 'ans' in a:
            html += f"\t<pl-answer correct= |@ params.{part_name}.{a}.correct @| > |@ params.{part_name}.{a}.value @| {units} </pl-answer>\n"

    html += '</pl-multiple-choice>\n' 

    return replace_tags(html)

def process_dropdown(part_name,parsed_question, data_dict):
    """Processes markdown format dropdown questions and returns PL HTML

    Args:
        part_name (string): Name of the question part being processed (e.g., part1, part2, etc...)
        parsed_question (dict): Dictionary of the MD-parsed question (output of `read_md_problem`)
        data_dict (dict): Dictionary of the `data` dict created after running server.py using `exec()`

    Returns:
        html: A string of HTML that is part of the final PL question.html file.
    """
    html = process_multiple_choice(part_name,parsed_question, data_dict).replace('-multiple-choice','-dropdown')
    return html
    
def process_number_input(part_name,parsed_question, data_dict):
    """Processes markdown format number-input questions and returns PL HTML

    Args:
        part_name (string): Name of the question part being processed (e.g., part1, part2, etc...)
        parsed_question (dict): Dictionary of the MD-parsed question (output of `read_md_problem`)
        data_dict (dict): Dictionary of the `data` dict created after running server.py using `exec()`

    Returns:
        html: A string of HTML that is part of the final PL question.html file.
    """

    html = f"""<pl-question-panel>\n\t<markdown>{parsed_question['body_parts_split'][part_name]['content']}\t</markdown>\n</pl-question-panel>\n\n"""
    
    pl_customizations = " ".join([f'{k} = "{v}"' for k,v in parsed_question['header'][part_name]['pl-customizations'].items()]) # PL-customizations
    html += f"""<pl-number-input answers-name="{part_name}_ans" {pl_customizations} ></pl-number-input>\n"""

    return replace_tags(html)

def process_checkbox(part_name,parsed_question, data_dict):
    """Processes markdown format checkbox (select all that apply) questions and returns PL HTML

    Args:
        part_name (string): Name of the question part being processed (e.g., part1, part2, etc...)
        parsed_question (dict): Dictionary of the MD-parsed question (output of `read_md_problem`)
        data_dict (dict): Dictionary of the `data` dict created after running server.py using `exec()`

    Returns:
        html: A string of HTML that is part of the final PL question.html file.
    """
    # start with the MCQ version and then...change things for checkbox questions
    html = process_multiple_choice(part_name,parsed_question, data_dict).replace('-multiple-choice','-checkbox')
    return html

def process_symbolic_input(part_name,parsed_question, data_dict):
    """Processes markdown format symbolic questions and returns PL HTML

    Args:
        part_name (string): Name of the question part being processed (e.g., part1, part2, etc...)
        parsed_question (dict): Dictionary of the MD-parsed question (output of `read_md_problem`)
        data_dict (dict): Dictionary of the `data` dict created after running server.py using `exec()`

    Returns:
        html: A string of HTML that is part of the final PL question.html file.
    """

    html = f"""<pl-question-panel>\n\t<markdown>{parsed_question['body_parts_split'][part_name]['content']}\t</markdown>\n</pl-question-panel>\n\n"""
    
    pl_customizations = " ".join([f'{k} = "{v}"' for k,v in parsed_question['header'][part_name]['pl-customizations'].items()]) # PL-customizations
    html += f"""<pl-symbolic-input answers-name="{part_name}_ans" {pl_customizations} ></pl-symbolic-input>\n"""

    return replace_tags(html).replace('\\\\','\\')

def replace_tags(string):
    """Takes in a string with tags: |@ and @| and returns {{ and }} respectively. This is because Python strings can't have double curly braces.

    Args:
        string (str): String to be processed, can be multi-line.

    Returns:
        string (str): returns string with tags replaced with curly braces.
    """
    return string.replace('|@','{{').replace('@|','}}')

def remove_correct_answers(data2_dict):
    """Magical recursive function that removes particular keys from a nested dictionary: https://stackoverflow.com/a/29652561/2217577

    Args:
        data2_dict (dict): Dictionary (nested) from which to remove key:value

    Returns:
        data2_dict (dict): Dictionary with the offending keys removed
    """

    # This was adapted from this SO: https://stackoverflow.com/a/29652561/2217577
    def gen_dict_extract(key_to_remove, dict_object):
        if hasattr(dict_object,'items'):
            for k, v in list(dict_object.items()):
                if key_to_remove in k:
                    dict_object.pop(k,None)
                if isinstance(v, dict):
                    for result in gen_dict_extract(key_to_remove, v):
                        yield result
                elif isinstance(v, list):
                    for d in v:
                        for result in gen_dict_extract(key_to_remove, d):
                            yield result

    list(gen_dict_extract('correct',data2_dict))

    return data2_dict

def process_attribution(source):
    """Takes in a string and returns the HTML for the attribution

    Args:
        source (string): One of a set of pre-defined values corresponding to a particular attribution.

    Returns:
        string (str): returns the html of the attribution
    """
    try:
        if 'openstax-physics-vol1' in source:
            attribution_text = "![Image representing the Creative Commons 4.0 BY license.](https://raw.githubusercontent.com/firasm/bits/master/by.png) Problem is from the [OpenStax University Physics Volume 1](https://openstax.org/details/books/university-physics-volume-1) textbook, licensed under the [CC-BY 4.0 license](https://creativecommons.org/licenses/by/4.0/)."

        elif 'openstax-physics-vol2' in source:
            attribution_text = "![Image representing the Creative Commons 4.0 BY license.](https://raw.githubusercontent.com/firasm/bits/master/by.png) Problem is from the [OpenStax University Physics Volume 2](https://openstax.org/details/books/university-physics-volume-2) textbook, licensed under the [CC-BY 4.0 license](https://creativecommons.org/licenses/by/4.0/)."

        elif 'ubc-mech2' in source:
            raise NotImplementedError

        elif 'standard' in source:
            attribution_text = "![The Creative Commons 4.0 license requiring attribution (BY), non-commercial (NC), and share-alike (SA) license.](https://raw.githubusercontent.com/firasm/bits/master/by-nc-sa.png) Problem is licensed under the [CC-BY-NC-SA 4.0 license](https://creativecommons.org/licenses/by-nc-sa/4.0/)."
    
        return attribution_text
    
    except TypeError:
        print("You probably need to update the template, the 'attribution' key seems to be missing.")
        
def process_question_md(source_filepath, output_path = None, instructor = False):
    
    try:
        pathlib.Path(source_filepath)
    except:
        print(f"{source_filepath} - File does not exist.")
        raise
        
    if output_path is None:
        if instructor: 
            # Set the output path (hard-coded)
            output_path = pathlib.Path(source_filepath.replace('source','output/instructor'))
        else:
            # Set the output path (hard-coded)
            output_path = pathlib.Path(source_filepath.replace('source','output/public'))
    else:
        ## TODO: Make this a bit more robust
        output_path = pathlib.Path(output_path)
        print(f"Warning: This feature (specifying your own directory {output_path}) is not tested!")
    
    # deal with multi-line strings in YAML Dump
    ## Code copied from here: https://stackoverflow.com/a/33300001/2217577

    def str_presenter(dumper, data2):
        if len(data2.splitlines()) > 1:  # check for multiline string
            return dumper.represent_scalar('tag:yaml.org,2002:str', data2, style='|')
        return dumper.represent_scalar('tag:yaml.org,2002:str', data2)

    yaml.add_representer(str, str_presenter)

    parsed_q = read_md_problem(source_filepath)

    header = parsed_q['header']
    body_parts = parsed_q['body_parts']
    
    # Run the python code
    ## TODO: Is there a better way to do this?
    exec(parsed_q['header']['server']['imports'].replace('import prairielearn as pl','from . import prairielearn as pl'),globals() )
    exec(parsed_q['header']['server']['generate'].split('# Update the data object with a new dict')[0],globals() )     

    # Remove the solutions from the server section
    if instructor is True:
        header.pop('server',None)

        # Remove python solution from the public view
        header.pop('server',None)

        # Remove correct answers from the data2 dict 
        data2_sanitized = defdict_to_dict(data2,{})
        data2_sanitized = remove_correct_answers(data2_sanitized)

        # Update the YAML header to add substitutions 
        header.update({'substitutions': data2_sanitized})

        # Update the YAML header to add substitutions, unsort it, and process for file
        header_yml = yaml.dump(header,sort_keys=False,default_flow_style=False)
        
        # Write the YAML to a file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text('---\n' + header_yml + '---\n' + dict_to_md(body_parts,remove_keys=['pl-submission-panel','pl-answer-panel']) +
                        '\n## Attribution\n\n' + process_attribution(header.get('attribution')) )
        
    else:
        # Update the YAML header to add substitutions 
        header.update({'substitutions': defdict_to_dict(data2,{})})

        # Update the YAML header to add substitutions, unsort it, and process for file
        header_yml = yaml.dump(header,sort_keys=False,default_flow_style=False)

        # Write the YAML to a file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text('---\n' + header_yml + '---\n' + dict_to_md(body_parts,remove_keys=['Rubric','Solution','Comments','pl-submission-panel','pl-answer-panel']) +
                        '\n## Attribution\n\n' + process_attribution(header.get('attribution')) )

    # Move image assets
    files_to_copy = header.get('assets')
    if files_to_copy:
        [copy2(pathlib.Path(source_filepath).parent / fl, output_path.parent) for fl in files_to_copy]

def process_question_pl(source_filepath, output_path = None):

    try:
        pathlib.Path(source_filepath)
    except:
        print(f"{source_filepath} - File does not exist.")
        raise

    if output_path is None:
        output_path = pathlib.Path(source_filepath.replace('source','output/prairielearn')).parent
    else:
        output_path = pathlib.Path(output_path).parent

        ## TODO: Make this a bit more robust
        print(f"Warning: This feature (specifying your own directory {output_path}) is not tested!")

    # Parse the MD file
    parsed_q = read_md_problem(source_filepath)

    # Create output dir if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)

    ############### Start Sketchiest Part
    # Run the python code
    try:
        exec(parsed_q['header']['server']['imports'],globals() )
        exec(parsed_q['header']['server']['generate'].split('# Update the data object with a new dict')[0],globals() )
    except ModuleNotFoundError:
        # AWFUL AWFUL hack because of the prairielearn.py file
        exec(parsed_q['header']['server']['imports'].replace('import prairielearn as pl','from . import prairielearn as pl'),globals() )
        exec(parsed_q['header']['server']['generate'].split('# Update the data object with a new dict')[0],globals() )     
    ############### End Sketchiest Part

    # Write info.json file
    write_info_json(output_path, parsed_q)

    # Question Preamble
    if parsed_q['body_parts']['preamble']:
        question_html = f"{parsed_q['body_parts']['preamble']}\n\n"
    else:
        question_html = f""

    ## Single part questions
    if parsed_q['num_parts'] == 1:
        q_type = parsed_q['header']['part1']['type']
        if 'multiple-choice' in q_type:
            question_html += process_multiple_choice('part1',parsed_q,data2)
        elif 'number-input' in q_type:
            question_html += process_number_input('part1',parsed_q,data2)
        elif 'checkbox' in q_type:
            question_html += process_checkbox('part1',parsed_q,data2)
        elif 'symbolic-input' in q_type:
            question_html += process_symbolic_input('part1',parsed_q,data2)
        elif 'dropdown' in q_type:
            question_html += process_dropdown('part1',parsed_q,data2)
        else:
            raise NotImplementedError(f"This question type ({q_type}) is not yet implemented.")

    ##### Multi part
    else:
        for pnum in range(1, parsed_q['num_parts'] + 1):
            part = 'part'+f'{pnum}'
            q_type = parsed_q['header'][part]['type']

            question_html += f"""<div class="card my-2">
<div class="card-header">{parsed_q['body_parts_split'][part]['title']}</div>\n
<div class="card-body">\n\n"""

            if 'multiple-choice' in q_type:                
                question_html += f"{process_multiple_choice(part,parsed_q,data2)}"  
            elif 'number-input' in q_type:
                question_html += f"{process_number_input(part,parsed_q,data2)}"
            elif 'checkbox' in q_type:
                question_html += process_checkbox(part,parsed_q,data2)
            elif 'symbolic-input' in q_type:
                question_html += process_symbolic_input(part,parsed_q,data2)
            elif 'dropdown' in q_type:
                question_html += process_dropdown(part,parsed_q,data2)
            else:
                raise NotImplementedError(f"This question type ({q_type}) is not yet implemented.")

            question_html += "</div>\n</div>\n\n\n"

    # Add pl-submission-panel and pl-answer-panel

    if parsed_q['body_parts_split']['pl-submission-panel']:
        question_html += f"<pl-submission-panel>{ parsed_q['body_parts_split']['pl-submission-panel'] } </pl-submission-panel>\n"

    if parsed_q['body_parts_split']['pl-answer-panel']:
        question_html += f"<pl-answer-panel>{ parsed_q['body_parts_split']['pl-answer-panel'] } </pl-answer-panel>\n"

    # Add Attribution
    question_html += f"\n<markdown>---\n{process_attribution(parsed_q['header'].get('attribution'))}\n</markdown>"

    # Final pre-processing
    question_html = pl_image_path(question_html)

    # Write question.html file
    (output_path / "question.html").write_text(question_html) #,encoding='raw_unicode_escape')

    ### TODO solve the issue with the latex escape sequences, this is a workaround
    # with open((output_path / "question.html"), "w") as qfile:
    #     print(f"{question_html}", file=qfile)

    # Write server.py file
    write_server_py(output_path,parsed_q)

    # Move image assets
    files_to_copy = parsed_q['header'].get('assets')
    if files_to_copy:
        pl_path =  output_path / "clientFilesQuestion"
        pl_path.mkdir(parents=True, exist_ok=True)
        [copy2(pathlib.Path(source_filepath).parent / fl, pl_path / fl) for fl in files_to_copy]

def pl_image_path(html):

    """Adds `clientFilesQuestion` directory before the path automatically
    """

    # If image files are included as markdown format, add clientFilesQuestion
    res = re.subn("\((.*\.png)\)",'(clientFilesQuestion/\\1)',html)

    # If image files are included as html format, add clientFilesQuestion
    res = re.subn(r"src=\"(?!http)(.*\.png)",
              "src=\"clientFilesQuestion/\\1",res[0]) # works


    return res[0]