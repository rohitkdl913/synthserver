import whisper
import numpy as np
from pydub import AudioSegment, silence
import argparse
import torch


# Load Whisper AI Model
model = whisper.load_model("/home/saugat/Projects/Major Project/translation-server/whisper-model.pt")  # Change model size if needed


# Audio processing parameters
MIN_SILENCE_LEN = 700  # Min silence duration (ms) to split audio
SILENCE_THRESH = -40  # Silence threshold in dBFS
SAMPLE_RATE = 16000  # Whisper expects 16kHz audio


def transcribe_audio(file_path):
    """Process the audio file and transcribe it in real-time chunks."""
    print(f"Processing: {file_path}")

    # Load audio file and convert it to 16kHz mono
    audio = AudioSegment.from_file(file_path).set_frame_rate(SAMPLE_RATE).set_channels(1)

    # Split based on silence
    chunks = silence.split_on_silence(audio, min_silence_len=MIN_SILENCE_LEN, silence_thresh=SILENCE_THRESH)

    for i, chunk in enumerate(chunks):
        # Ensure the chunk is at least 1 second long for Whisper to work properly
        if len(chunk) < 1000:
            chunk = chunk + AudioSegment.silent(duration=1000 - len(chunk))

        # Convert chunk to numpy array compatible with Whisper
        samples = np.array(chunk.get_array_of_samples())
        
        # Normalize to float32 in [-1, 1] range
        samples = samples.astype(np.float32) / (2 ** (8 * chunk.sample_width - 1))

        # Use Whisper's built-in transcribe function
        result = model.transcribe(samples, fp16=False)
        text = result["text"].strip()

        if text:
            print(f"Chunk {i+1}: {text}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcribe an audio file using Whisper AI with real-time-like output.")
    parser.add_argument("file", type=str, help="Path to the audio file")
    args = parser.parse_args()

    # transcribe_audio(args.file)
    result = model.transcribe(args.file, fp16=False)
    text = result["text"]
    print(f"result {result}")
