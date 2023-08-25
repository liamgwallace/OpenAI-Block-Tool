
import chardet
import argparse
import json
import os
import glob
from dotenv import load_dotenv
import openai
from tkinter import filedialog, Tk

# Load .env file
load_dotenv()
# Set your OpenAI key
openai_api_key = os.getenv('OPENAI_API_KEY')

verbose = False
slow = False

class Block:
    def __init__(self, block_index=0, input_block=[], loop_block=None, ai_temp=0.9, prompt_system="", prompt_user="", prompt_files=[], data_files=[], output_file="", output_text="",is_processed=False):
        self.block_index = block_index
        self.input_block = input_block
        self.loop_block = loop_block
        self.ai_temp = ai_temp
        self.prompt_system = prompt_system
        self.prompt_user = prompt_user
        self.prompt_files = prompt_files
        self.data_files = data_files
        self.output_file = output_file
        self.output_text = output_text
        self.is_processed = is_processed
 
def print_verbose(*args):

    if verbose:
        print("##############################################################")
        for arg in args:
            if isinstance(arg, list):
                for item in arg:
                    print(item)
            else:
                print(arg)
        
        print("##############################################################")
    if slow:
        a = input("press enter con continue")
        
def Get_AI_output(system_prompt, user_prompt, ai_temp):
    openai.api_key = openai_api_key
    completion = openai.ChatCompletion.create(
      model="gpt-3.5-turbo-16k",
      temperature= ai_temp,
      messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
      ]
    )
    result = completion.choices[0].message.content
    return result

def write_to_file(filename, content):
    if not filename:
        return
    filename = "output_files/" + filename
    #print(f"filename: {filename}")
    directory = os.path.dirname(filename)
    # If the directory does not exist, create it
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(filename, 'w') as file:
        file.write(content)


def read_file(filename):
    if not filename:
        return "No file specified"
    filename = "input_files/" + filename
    try:
        with open(filename, 'rb') as file:
            content = file.read()
            encoding = chardet.detect(content)['encoding']
            if encoding:
                return content.decode(encoding)
            else:
                print(f"ERROR: Unable to detect encoding for file '{filename}'.")
                return ""
    except FileNotFoundError:
        print(f"ERROR: File '{filename}' not found.")
        return ""
        
def read_blocks(folder_path):
    blocks = []
    
    # Get all the json files in the folder
    json_files = glob.glob(os.path.join(folder_path, '*.json'))
    for json_file in json_files:
        with open(json_file, 'r') as file:
            print(f"reading file: {json_file}")
            data = json.load(file)
            # Create a Block object with default values
            temp_block = Block()

            # Iterate through the keys in the Block object and set their values from the JSON file
            for key in temp_block.__dict__.keys():
                setattr(temp_block, key, data.get(key, getattr(temp_block, key)))

            block_index = temp_block.block_index

            # Ensure the blocks list is long enough to accommodate the current block index
            while len(blocks) <= block_index:
                blocks.append(None)

            # Store the temp_block in the blocks list at the specified index
            blocks[block_index] = temp_block
    return blocks
    
def process_blocks(blocks):
    # Keep processing blocks until all have been processed
    iteration_count = 0
    while any(not block.is_processed for block in blocks):
        # Process each block in order
        for i, block in enumerate(blocks):
            if not block.is_processed:
                input_blocks_processed = all(blocks[index].is_processed for index in block.input_block)
                loop_block_processed = blocks[block.loop_block].is_processed if block.loop_block is not None else True
                
                if input_blocks_processed and loop_block_processed:
                    # Process the current block
                    block_output = block_process(blocks, i)
                
                iteration_count += 1
                if iteration_count > 200:
                    # Break the loop forcefully if it runs for too long
                    print("Breaking the loop forcefully to avoid infinite loop.")
                    break    
    #return the output for the last block processed
    return block_output

def block_process(blocks, block_index):
    # Code to process a block goes here
    print_verbose("")
    print("##############################################################")   
    print(f"Processing block at index {block_index}")
    print_verbose("")
    curr_block = blocks[block_index]
    # Get output_text from the block specified by loop_block
    output_text_string = blocks[curr_block.loop_block].output_text
    # Get output_text from blocks specified by input_block
    curr_inputs = [blocks[i].output_text for i in curr_block.input_block]  
    curr_inputs_str = "\n".join(curr_inputs)
    # Get system prompt and read into (curr_prompt_system)
    curr_prompt_system = curr_block.prompt_system
    # Get user prompt and read into (curr_prompt_user)
    curr_ai_temp = curr_block.ai_temp
    # Get user prompt and read into (curr_prompt_user)
    curr_prompt_user = curr_block.prompt_user
    # Get prompt file and read into (curr_prompt_files)
    curr_prompt_files = curr_block.prompt_files
    # get the file to write the block output to
    curr_block_output_file = curr_block.output_file
    # Get data files and read into (joined_data_files)
    curr_data_files = curr_block.data_files
    joined_data_files = ""
    for curr_data_file in curr_data_files:
        if curr_data_file:
            joined_data_files += "\n" + read_file(curr_data_file) + "\n"
    # Check if output_text_string is not empty
    if output_text_string:
        try:
            # Try to load the JSON string into a Python list
            curr_loop_elements = json.loads(output_text_string)
        except json.JSONDecodeError:
            # Handle the exception if the output_text_string is not a valid JSON
            print("The output text was not correctly formatted as a JSON string.")
            #print(output_text_string)
            curr_loop_elements = [""]  # Default to a list containing an empty string
    else:
        # If the output_text_string is empty, default to a list containing an empty string
        curr_loop_elements = [""]

    curr_block_output_text = ""
    # Loop through each element in curr_loop_elements
    for curr_loop_element in curr_loop_elements:
        # Loop through each element in curr_prompt_files
        for curr_prompt_file in curr_block.prompt_files if curr_prompt_files else [""]:
            #Read the prompt file
            curr_prompt_file_content = ""
            if curr_prompt_file:
                curr_prompt_file_content = read_file(curr_prompt_file)
            #setup the placeholders to go into the prompt
            placeholders = {
                "block_input": curr_inputs_str,
                "loop_input": curr_loop_element,
                "prompt_file": curr_prompt_file_content,                
                "data_file": joined_data_files
                
            }
            #create the user and system prompts with placeholder data and file data
            prompt_system = curr_prompt_system.format(**placeholders) 
            prompt_user = curr_prompt_user.format(**placeholders)  
            print_verbose(f"prompt_system:\n{prompt_system}")
            print_verbose(f"prompt_user:\n{prompt_user}")
            #print_verbose(f"curr_loop_element:\n{curr_loop_element}")
            #print_verbose(f"curr_prompt_file:\n{curr_prompt_file}")
            AI_output = Get_AI_output(prompt_system, prompt_user, curr_ai_temp)   
            print("##############################################################")   
            print(f"\nAI_result:\n{AI_output}")       
            curr_block_output_text += "\n" + AI_output
    #print_verbose(f"curr_block_output_text:\n{curr_block_output_text}")    
    blocks[block_index].output_text = curr_block_output_text
    # Write curr_block_output_text to blocks[block_index].output_file
    write_to_file(curr_block_output_file, curr_block_output_text)
    # Mark the current block as processed
    blocks[block_index].is_processed = True
    #a= input("ready for next block?")
    return AI_output
    
def main():
    # Get the absolute path to the directory containing the main.py script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Open the folder picker dialog with the script's path as the default
    root = Tk()
    root.withdraw()  # Hide the root Tk window
    blocks_folder_path = filedialog.askdirectory(initialdir=script_dir, title="Please select a directory")
    # If user didn't select any folder, use the default path
    if not blocks_folder_path:
        blocks_folder_path = os.path.join(script_dir, "blocks_folder")
    # Pass the folder path to the read_blocks function
    blocks = read_blocks(blocks_folder_path)
    result = process_blocks(blocks)
    print_verbose("")    
    print(f"####################################################################################")
    print(f"Final block Result:\n\n{result}")
    print(f"####################################################################################")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Open AI block linking tool")
    parser.add_argument('--verbose', dest='verbose', action='store_true', help='Enable verbose mode')
    parser.add_argument('--slow', dest='slow', action='store_true', help='Enable slow verbose mode')
    parser.set_defaults(verbose=False, slow=False)
    args = parser.parse_args()
    verbose = args.verbose
    slow = args.slow
    main()