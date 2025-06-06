import os
from music21 import converter, environment
from datetime import datetime

def generate_sheet_music(midi_path):
    """
    Convert MIDI to sheet music and return the paths to the MusicXML and PNG files
    
    Parameters:
    midi_path (str): Path to the MIDI file
    
    Returns:
    tuple: (xml_path, png_path) - Paths to the generated MusicXML and PNG files
    """
    # Create static directories if they don't exist
    base_dir = os.path.dirname(os.path.abspath(__file__))
    static_xml_dir = os.path.join(base_dir, "static", "xml")
    static_png_dir = os.path.join(base_dir, "static", "png")
    
    os.makedirs(static_xml_dir, exist_ok=True)
    os.makedirs(static_png_dir, exist_ok=True)
    
    # Generate filenames with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    midi_basename = os.path.basename(midi_path)
    base_name = os.path.splitext(midi_basename)[0]
    
    # Convert MIDI to music21 score
    score = converter.parse(midi_path)
    
    # Save the score as MusicXML for display
    xml_filename = f"{base_name}_{timestamp}.xml"
    xml_path = os.path.join(static_xml_dir, xml_filename)
    score.write('musicxml', fp=xml_path)
    
    # Skip PNG generation since we're using Verovio in the browser
    # This avoids the MuseScore dependency
    png_path = None
    
    return xml_path, png_path