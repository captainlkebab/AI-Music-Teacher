import os
from pydub import AudioSegment
from basic_pitch.inference import predict_and_save
from music21 import converter, environment

# Set up logging
def setup_logging(log_file="music_transcription.log", level=logging.INFO):
    """Configure logging to output to both file and console"""
    # Create logger
    logger = logging.getLogger("music_transcription")
    logger.setLevel(level)
    
    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # Create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Initialize logger
logger = setup_logging()

# Optional: set up MuseScore for music21 (for showing the score)
us = environment.UserSettings()
us['musicxmlPath'] = r"C:\Program Files\MuseScore 4\bin\MuseScore4.exe"  # adjust path as needed

# Step 1: Convert MP3 to WAV
def convert_mp3_to_wav(mp3_path, wav_path):
    logger.info("Converting MP3 to WAV...")
    try:
        audio = AudioSegment.from_mp3(mp3_path)
        audio.export(wav_path, format="wav")
        logger.info(f"Successfully converted {mp3_path} to {wav_path}")
    except Exception as e:
        logger.error(f"Error converting MP3 to WAV: {str(e)}")
        raise

# Step 2: Transcribe WAV to MIDI using BasicPitch
def transcribe_audio_to_midi(wav_path, output_dir):
    logger.info("Transcribing audio to MIDI...")
    try:
        predict_and_save([wav_path], output_dir, save_midi=True, save_model_outputs=False)
        logger.info(f"Successfully transcribed {wav_path} to MIDI")
    except Exception as e:
        logger.error(f"Error transcribing audio to MIDI: {str(e)}")
        raise

# Step 3: Load and show MIDI with music21
def read_and_show_midi(midi_path):
    logger.info(f"Reading MIDI with music21: {midi_path}")
    try:
        score = converter.parse(midi_path)
        logger.info("Opening score in viewer...")
        score.show()  # Opens in MuseScore or default musicXML viewer
        return score
    except Exception as e:
        logger.error(f"Error reading or showing MIDI: {str(e)}")
        raise

# Full pipeline
def mp3_to_music21(mp3_path, working_dir="output"):
    logger.info(f"Starting full transcription pipeline for {mp3_path}")
    
    try:
        os.makedirs(working_dir, exist_ok=True)
        logger.debug(f"Created or verified working directory: {working_dir}")
        
        wav_path = os.path.join(working_dir, "converted.wav")
        logger.debug(f"WAV output path: {wav_path}")

    convert_mp3_to_wav(mp3_path, wav_path)
    transcribe_audio_to_midi(wav_path, working_dir)

    midi_path = os.path.join(working_dir, "converted_basic_pitch.mid")
    if os.path.exists(midi_path):
        score = read_and_show_midi(midi_path)
        return score
    else:
        raise FileNotFoundError("MIDI file not found after transcription.")

# Example usage
if __name__ == "__main__":
    mp3_file = "fur_elise.mp3"  # Provide your input file
    mp3_to_music21(mp3_file)
