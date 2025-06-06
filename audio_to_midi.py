import os
import tempfile
import librosa
import numpy as np
import pretty_midi
import traceback
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("audio_conversion.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("audio_converter")

# Force Numba to compile the onset detection function at startup
def _precompile_librosa_functions():
    dummy_audio = np.zeros(1000)
    # Use the exact same parameters as in your convert_audio_to_midi function
    librosa.onset.onset_detect(
        y=dummy_audio, 
        sr=22050,
        wait=0.1,
        pre_avg=0.5,
        post_avg=0.5,
        pre_max=0.5,
        post_max=0.5,
        delta=0.07,
        backtrack=True
    )
    
    # Also pre-compile other librosa functions you're using
    librosa.piptrack(y=dummy_audio, sr=22050)

# Run the precompilation
_precompile_librosa_functions()

def convert_audio_to_midi(audio_file):
    """
    Convert an audio file to MIDI using librosa for note detection
    
    Parameters:
    audio_file (str): Path to the audio file to convert
    
    Returns:
    str: Path to the generated MIDI file
    """
    try:
        logger.info(f"Starting conversion of audio file: {audio_file}")
        
        # Use static/midi directory instead of a temporary directory
        static_midi_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "midi")
        os.makedirs(static_midi_dir, exist_ok=True)
        logger.info(f"Using MIDI directory: {static_midi_dir}")
        
        # Generate a filename based on the original audio filename with timestamp
        original_filename = os.path.basename(audio_file)
        base_name = os.path.splitext(original_filename)[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        midi_filename = f"{base_name}_{timestamp}.mid"
        midi_path = os.path.join(static_midi_dir, midi_filename)
        
        logger.info(f"Will save MIDI file to: {midi_path}")
        
        # Load the audio file
        logger.info("Loading audio file with librosa")
        y, sr = librosa.load(audio_file, sr=None)
        logger.info(f"Audio loaded successfully. Sample rate: {sr}, Length: {len(y)}")
        
        # Extract pitch and onset information
        logger.info("Detecting onsets")
        # Improved onset detection with custom parameters
        onset_frames = librosa.onset.onset_detect(
            y=y, 
            sr=sr,
            wait=0.05,          # Increased from 0.03 but still less than original 0.1
            pre_avg=0.4,        # Increased from 0.3 but still less than original 0.5
            post_avg=0.4,       # Increased from 0.3 but still less than original 0.5
            pre_max=0.4,        # Increased from 0.3 but still less than original 0.5
            post_max=0.4,       # Increased from 0.3 but still less than original 0.5
            delta=0.03,         # Decreased from 0.04 to be more sensitive
            backtrack=True      # Keep backtracking
        )
        
        onset_times = librosa.frames_to_time(onset_frames, sr=sr)
        logger.info(f"Detected {len(onset_times)} onsets")
        
        if len(onset_times) == 0:
            logger.warning("No onsets detected in the audio. The file might be silent or not contain clear note onsets.")
            raise ValueError("No musical notes detected in the audio file. Please try a different recording.")
        
        # Use librosa to estimate pitches
        logger.info("Estimating pitches")
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        logger.info("Pitch estimation complete")
        
        # Create a MIDI file
        logger.info("Creating MIDI file")
        pm = pretty_midi.PrettyMIDI()
        piano_program = pretty_midi.instrument_name_to_program('Acoustic Grand Piano')
        piano = pretty_midi.Instrument(program=piano_program)
        
        # Add notes to the MIDI file
        notes_added = 0
        logger.info("Adding notes to MIDI file")
        for i, onset in enumerate(onset_times):
            if i < len(onset_times) - 1:
                duration = min(onset_times[i + 1] - onset, 1.0)  # Cap duration at 1 second
                analysis_duration = min(duration, 0.2)  # Analyze up to 200ms for pitch
            else:
                duration = 0.5  # Default duration for the last note
                analysis_duration = 0.2
            
            # Use the new function
            pitch = estimate_pitch_for_segment(y, sr, onset, analysis_duration)
            
            # Convert frequency to MIDI note number
            if pitch > 0:
                midi_note = int(round(librosa.hz_to_midi(pitch)))
                note = pretty_midi.Note(
                    velocity=100,
                    pitch=midi_note,
                    start=onset,
                    end=onset + duration
                )
                piano.notes.append(note)
                notes_added += 1
        
        logger.info(f"Added {notes_added} notes to the MIDI file")
        
        if notes_added == 0:
            logger.warning("No notes were added to the MIDI file. Check if pitch detection is working correctly.")
            raise ValueError("Failed to detect any musical notes in the audio. Please try a different recording.")
        
        pm.instruments.append(piano)
        pm.write(midi_path)
        logger.info(f"MIDI file written successfully to {midi_path}")
        
        return midi_path
    
    except Exception as e:
        logger.error(f"Error in convert_audio_to_midi: {str(e)}")
        logger.error(traceback.format_exc())
        raise


# For each onset, analyze a small segment after the onset
def estimate_pitch_for_segment(y, sr, start_time, duration):
    # Convert time to samples
    start_sample = int(start_time * sr)
    duration_samples = int(duration * sr)
    end_sample = min(start_sample + duration_samples, len(y))
    
    # Extract the segment
    segment = y[start_sample:end_sample]
    
    if len(segment) < 512:  # Need minimum length for FFT
        segment = np.pad(segment, (0, 512 - len(segment)))
    
    # Use more robust pitch estimation
    pitches, magnitudes = librosa.piptrack(y=segment, sr=sr)
    
    # Take the average of the top 3 pitch candidates
    pitch_candidates = []
    for frame in range(pitches.shape[1]):
        frame_pitches = pitches[:, frame]
        frame_magnitudes = magnitudes[:, frame]
        
        # Get indices of top 3 magnitudes
        top_indices = np.argsort(frame_magnitudes)[-3:]
        
        # Get corresponding pitches
        for idx in top_indices:
            if frame_magnitudes[idx] > 0 and frame_pitches[idx] > 0:
                pitch_candidates.append(frame_pitches[idx])
    
    if pitch_candidates:
        return np.median(pitch_candidates)  # Use median to avoid outliers
    return 0