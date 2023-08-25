
# OpenAI-Block-Tool

`OpenAI-Block-Tool` is a Python utility designed to streamline the process of chaining together multiple prompts and API calls to OpenAI's language models, particularly GPT-3.5-turbo-16k. By using "block" files, users can instruct the tool to read, process, and execute a series of prompts in a predefined order.

## Prerequisites

- An API key from OpenAI. Ensure you set it in a `.env` file as `OPENAI_API_KEY=YOUR_KEY_HERE`.

## Installation

1. Clone this repository:

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/OpenAI-Block-Tool.git
cd OpenAI-Block-Tool
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Prepare your block files and store them together in a single folder. Refer to the "Block File Structure" section below for details on how to format these files.
2. Run the main script:

```bash
python main.py
```

3. When prompted, select the directory containing your block files. The tool will then read and process these blocks in order.

## Block File Structure

Each block file is a JSON file that instructs the tool on how to interact with the OpenAI API. A block can contain:

- **block_index**: The order in which the block should be processed.
- **input_block**: An array of indices specifying which blocks' outputs should be taken as input for the current block.
- **loop_block**: An optional index specifying which block's output should be used as loop elements for the current block. The output of this block should be a JSON formatted string, representing a list of elements: `["element1", "element2", "etc."]`.
- **ai_temp**: The AI's temperature setting, affecting the randomness of its output.
- **prompt_system**: The system-level prompt for the AI.
- **prompt_user**: The user-level prompt for the AI.
- **prompt_files**: An array of filenames which will be read and included in the prompt.
- **data_files**: An array of filenames which will be read and included as data in the prompt.
- **output_file**: The filename where the AI's response should be saved.
- **output_text**: Reserved for internal use by the tool to store the AI's response.
- **is_processed**: Reserved for internal use by the tool to track which blocks have been processed.

### Placeholders

The tool supports dynamic inputs using placeholders in the prompts:

- `{block_input}`: This will be replaced by the combined outputs of the blocks specified in `input_block`.
- `{loop_input}`: When using a `loop_block`, this will be replaced by the current element of the loop.
- `{prompt_file}`: This will be replaced by the content of the current file from `prompt_files`.
- `{data_file}`: This will be replaced by the combined contents of all files specified in `data_files`.

### Example Blocks

**Basic Information Block**

```json
{
  "block_index": 1,
  "input_block": [],
  "ai_temp": 0.7,
  "prompt_system": "You are an informative bot...",
  "prompt_user": "Tell me about the history of AI...",
  "prompt_files": [],
  "data_files": [],
  "output_file": "output1.txt",
  "output_text": "",
  "is_processed": false
}
```

**Summarization Block**

```json
{
  "block_index": 5,
  "input_block": [1],
  "loop_block": 0,
  "ai_temp": 0.9,
  "prompt_system": "You are a summarization bot...",
  "prompt_user": "Based on the following article: 
{block_input} 

 Select from the following information the top 8 list of keywords that would fit
Keyword data
{data_file}",
  "prompt_files": [],
  "data_files": ["data1.txt", "data2.txt"],
  "output_file": "output5.txt",
  "output_text": "",
  "is_processed": false
}
```

**Creative Writing Block**

```json
{
  "block_index": 3,
  "input_block": [1],
  "loop_block": 4,
  "ai_temp": 0.5,
  "prompt_system": "You are a creative writer bot...",
  "prompt_user": "Write a short chapter on [{loop_input}] for a short blogpost. Keep it to 1 paragraph. 
Start the chapter with 
[chapter number] - [chapter title]
Here is the blogpost outline: 
 {block_input}",
  "prompt_files": [],
  "data_files": [],
  "output_file": "output3.txt",
  "output_text": "",
  "is_processed": false
}
```

## How It Works

The tool processes blocks by:

1. Reading each block file from the selected directory.
2. Processing blocks based on their `block_index`.
3. Sending prompts to the OpenAI API and obtaining responses.
4. Writing the AI's response to the specified `output_file`.
5. Looping through and processing each block until all blocks have been processed.

## Contributions

Feel free to contribute to this project by raising issues or submitting pull requests.

