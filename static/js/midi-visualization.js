document.addEventListener('DOMContentLoaded', function() {
    // Form submission handler
    document.getElementById('uploadForm').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const fileInput = document.getElementById('audioFile');
        const file = fileInput.files[0];
        
        if (!file) {
            alert('Please select a file');
            return;
        }
        
        const formData = new FormData();
        formData.append('file', file);
        
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Error: ' + data.error);
                return;
            }
            
            // Show the result section
            document.getElementById('resultSection').classList.remove('d-none');
            
            // Set the original audio
            const audioPlayer = document.getElementById('originalAudio');
            audioPlayer.src = URL.createObjectURL(file);
            
            // Set the MIDI file for the player
            const midiPlayer = document.getElementById('midiPlayer');
            midiPlayer.src = data.midi_path;
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred during upload');
        });
    });

    // Visualization type radio buttons event listeners
    document.querySelectorAll('input[name="visualizationType"]').forEach(function(radio) {
        radio.addEventListener('change', function() {
            const visualizer = document.getElementById('midiVisualizer');
            visualizer.type = this.value;
            
            // Apply specific configurations based on visualization type
            if (this.value === 'waterfall') {
                visualizer.config = {
                    noteHeight: 6,
                    pixelsPerTimeStep: 60,
                    minPitch: 21,
                    maxPitch: 108
                };
            } else if (this.value === 'staff') {
                visualizer.config = {
                    noteHeight: 4,
                    noteSpacing: 1,
                    pixelsPerTimeStep: 30
                };
            } else {
                // Default piano-roll settings
                visualizer.config = {
                    noteHeight: 3,
                    pixelsPerTimeStep: 50
                };
            }
        });
    });

    // Range sliders for advanced settings
    const noteHeightSlider = document.getElementById('noteHeight');
    const noteHeightValue = document.getElementById('noteHeightValue');
    const noteSpeedSlider = document.getElementById('noteSpeed');
    const noteSpeedValue = document.getElementById('noteSpeedValue');

    if (noteHeightSlider && noteHeightValue) {
        noteHeightSlider.addEventListener('input', function() {
            noteHeightValue.textContent = this.value;
            updateVisualizerConfig();
        });
    }

    if (noteSpeedSlider && noteSpeedValue) {
        noteSpeedSlider.addEventListener('input', function() {
            noteSpeedValue.textContent = this.value;
            updateVisualizerConfig();
        });
    }

    function updateVisualizerConfig() {
        const visualizer = document.getElementById('midiVisualizer');
        const visualizationType = document.querySelector('input[name="visualizationType"]:checked').value;
        const noteHeight = parseInt(noteHeightSlider.value);
        const pixelsPerTimeStep = parseInt(noteSpeedSlider.value);

        let config = {
            noteHeight: noteHeight,
            pixelsPerTimeStep: pixelsPerTimeStep
        };

        // Add type-specific configurations
        if (visualizationType === 'waterfall') {
            config.minPitch = 21;
            config.maxPitch = 108;
        } else if (visualizationType === 'staff') {
            config.noteSpacing = 1;
        }

        visualizer.config = config;
    }
});