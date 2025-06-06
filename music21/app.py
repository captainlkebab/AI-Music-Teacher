import os
import streamlit as st
from pydub import AudioSegment
from basic_pitch.inference import predict_and_save
from music21 import converter, environment

# Pfade für MuseScore und Lilypond (anpassen!)
us = environment.UserSettings()
us['musicxmlPath'] = r"C:\Program Files\MuseScore 4\bin\MuseScore4.exe"
us['lilypondPath'] = r"C:\Program Files (x86)\LilyPond\usr\bin\lilypond.exe"

# Audio umwandeln
def convert_mp3_to_wav(mp3_path, wav_path):
    audio = AudioSegment.from_mp3(mp3_path)
    audio.export(wav_path, format="wav")

# MIDI erzeugen
def transcribe_audio_to_midi(wav_path, output_dir):
    predict_and_save([wav_path], output_dir, save_midi=True)

# MIDI lesen und als PNG speichern
def midi_to_png(midi_path, output_path):
    score = converter.parse(midi_path)
    png_path = score.write(fmt='lily.png', fp=output_path)
    return png_path

# Streamlit UI
st.title("🎵 MP3 to MIDI + Score Viewer")

uploaded_file = st.file_uploader("Upload an MP3 file", type=["mp3"])

if uploaded_file:
    with st.spinner("Processing..."):
        # Temporäre Dateien
        work_dir = "temp"
        os.makedirs(work_dir, exist_ok=True)

        mp3_path = os.path.join(work_dir, "input.mp3")
        wav_path = os.path.join(work_dir, "converted.wav")
        midi_path = os.path.join(work_dir, "converted_basic_pitch.mid")
        png_path = os.path.join(work_dir, "score.png")

        with open(mp3_path, "wb") as f:
            f.write(uploaded_file.read())

        convert_mp3_to_wav(mp3_path, wav_path)
        transcribe_audio_to_midi(wav_path, work_dir)

        if os.path.exists(midi_path):
            png = midi_to_png(midi_path, png_path)
            st.success("Done!")
            st.image(png, caption="Transcribed Score")
            with open(midi_path, "rb") as f:
                st.download_button("Download MIDI", f, file_name="transcribed.mid")
        else:
            st.error("MIDI konnte nicht erzeugt werden.")
