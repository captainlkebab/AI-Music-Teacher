from music21 import converter, note, chord, stream
import json

def mxl_to_json(path):
    score = converter.parse(path)
    result = []

    for part in score.parts:
        part_data = {"partName": part.partName, "measures": []}
        for m in part.getElementsByClass(stream.Measure):
            measure_data = {"number": m.number, "notes": []}
            for element in m.notesAndRests:
                if isinstance(element, note.Note):
                    measure_data["notes"].append({
                        "type": "note",
                        "pitch": element.nameWithOctave,
                        "duration": element.quarterLength
                    })
                elif isinstance(element, chord.Chord):
                    measure_data["notes"].append({
                        "type": "chord",
                        "pitches": [n.nameWithOctave for n in element.notes],
                        "duration": element.quarterLength
                    })
                elif element.isRest:
                    measure_data["notes"].append({
                        "type": "rest",
                        "duration": element.quarterLength
                    })
            part_data["measures"].append(measure_data)
        result.append(part_data)
    
    return json.dumps(result, indent=2)


json_data = mxl_to_json("test1.mxl")

# in Datei schreiben (optional)
with open("output.json", "w") as f:
    f.write(json_data)