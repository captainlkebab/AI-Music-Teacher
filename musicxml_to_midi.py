import os
import logging
from music21 import converter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("conversion.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("musicxml_converter")

def convert_musicxml_to_midi(musicxml_path, output_dir=None):
    """
    Convert a MusicXML file to MIDI format
    
    Parameters:
    musicxml_path (str): Path to the MusicXML file
    output_dir (str, optional): Directory to save the MIDI file. If None, saves in the same directory as the input file.
    
    Returns:
    str: Path to the generated MIDI file
    """
    try:
        logger.info(f"Starting conversion of MusicXML file: {musicxml_path}")
        
        # Determine output directory
        if output_dir is None:
            output_dir = os.path.dirname(musicxml_path)
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate output filename
        base_name = os.path.splitext(os.path.basename(musicxml_path))[0]
        midi_path = os.path.join(output_dir, f"{base_name}.mid")
        
        # Parse the MusicXML file with music21
        logger.info("Parsing MusicXML with music21")
        score = converter.parse(musicxml_path)
        
        # Write the score as MIDI
        logger.info(f"Writing MIDI file to {midi_path}")
        score.write('midi', fp=midi_path)
        
        logger.info("Conversion completed successfully")
        return midi_path
        
    except Exception as e:
        logger.error(f"Error converting MusicXML to MIDI: {str(e)}")
        raise

# Example usage
if __name__ == "__main__":
    # Example: convert the Test1.musicxml file
    musicxml_file = "c:\\Users\\samil\\Documents\\PythonScripts\\AIMusicTeacher\\Oemer\\Test1.musicxml"
    midi_file = convert_musicxml_to_midi(musicxml_file)
    print(f"Converted MusicXML to MIDI: {midi_file}")