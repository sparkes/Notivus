from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Verify API key is set
if not client.api_key:
    raise ValueError("No OpenAI API key found. Please set OPENAI_API_KEY in .env file.")

# Define input file and output directory
input_file = "input_words.txt"  # Path to your file with one word per line
output_dir = "output_audio"  # Directory to save the audio files
os.makedirs(output_dir, exist_ok=True)

# Function to generate audio for a given word
def generate_audio(word):
    try:
        # Generate the audio response
        response = client.audio.speech.create(
            model="tts-1-hd",
            voice="nova",
            input=word
        )
        
        # Construct the output filename
        filename = f"sample_{word}.wav"
        output_path = os.path.join(output_dir, filename)
        
        # Save the audio to the file
        response.stream_to_file(output_path)
        
        print(f"Audio file saved: {output_path}")
    except Exception as e:
        print(f"Error generating audio for '{word}': {e}")

# Process the input file
def process_file(file_path):
    try:
        with open(file_path, "r") as file:
            lines = file.readlines()
        
        # Iterate over each line in the file
        for line in lines:
            word = line.strip()  # Remove any extra whitespace or newline characters
            if not word:  # Skip empty lines
                continue
            
            # Generate and save audio for the word
            generate_audio(word)
    
    except Exception as e:
        print(f"Error processing file '{file_path}': {e}")

if __name__ == "__main__":
    process_file(input_file)