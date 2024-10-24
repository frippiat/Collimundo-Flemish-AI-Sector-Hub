import json

def parse_file(input_file):
    """! Function used to parse the input file

    @param input_file: The input file
    @return: The training data
    """

    training_data = []
    with open(input_file, 'r') as file:
        for line in file:
            if line.strip():
                user_query, assistant_response = line.strip().split('$')
                training_data.append({
                    "messages": [
                        {"role": "user", "content": user_query},
                        {"role": "assistant", "content": assistant_response}
                    ]
                })
    return training_data

def save_json(training_data, output_file):
    """! Function used to save the training data to a json file
    
    @param training_data: The training data
    @param output_file: The output file
    """

    with open(output_file, 'w') as file:
        for data in training_data:
            json.dump(data, file)
            file.write('\n')

if __name__ == "__main__":
    input_file = "trainingsdata.txt"
    output_file = "trainings_data_v1.jsonl"
    training_data = parse_file(input_file)
    save_json(training_data, output_file)
