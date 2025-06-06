from basic_pitch import ICASSP2022Model
from basic_pitch.inference import predict_and_save
import os

# Eingabedatei
input_file = "input.mp3"
output_folder = "output"

# Model laden & Konvertieren
model = ICASSP2022Model()
os.makedirs(output_folder, exist_ok=True)
predict_and_save([input_file], model, output_directory=output_folder)

print(f"✅ MIDI gespeichert in: {output_folder}")
