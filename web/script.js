// Global variables for control and animation IDs.
let audioCtx = null;
let lowFreqAnimationId = null;
let heatmapAnimationId = null;

const fileInput = document.getElementById('audio-upload');

// Retrieve canvases and contexts for low-frequency visualization.
const lowFreqCanvasData = document.getElementById('lowFreqCanvasData');
const lowCtx = lowFreqCanvasData.getContext('2d');
const lowFreqCanvasGuides = document.getElementById('lowFreqCanvasGuides');
const lowGuideCtx = lowFreqCanvasGuides.getContext('2d');

// Retrieve canvases and contexts for the full-range heatmap.
const heatmapCanvasData = document.getElementById('heatmapCanvasData');
const heatmapCtx = heatmapCanvasData.getContext('2d');
const heatmapCanvasGuides = document.getElementById('heatmapCanvasGuides');
const heatmapGuideCtx = heatmapCanvasGuides.getContext('2d');

// Initialize the data canvases with a black background.
lowCtx.fillStyle = 'black';
lowCtx.fillRect(0, 0, lowFreqCanvasData.width, lowFreqCanvasData.height);
heatmapCtx.fillStyle = 'black';
heatmapCtx.fillRect(0, 0, heatmapCanvasData.width, heatmapCanvasData.height);

// Draw static guides for the low-frequency graph.
function drawLowFreqGuides() {
  lowGuideCtx.clearRect(0, 0, lowFreqCanvasGuides.width, lowFreqCanvasGuides.height);
  lowGuideCtx.strokeStyle = 'white';
  lowGuideCtx.lineWidth = 1;
  lowGuideCtx.beginPath();
  // Horizontal guide lines at the top and bottom.
  lowGuideCtx.moveTo(0, 0);
  lowGuideCtx.lineTo(lowFreqCanvasGuides.width, 0);
  lowGuideCtx.moveTo(0, lowFreqCanvasGuides.height);
  lowGuideCtx.lineTo(lowFreqCanvasGuides.width, lowFreqCanvasGuides.height);
  lowGuideCtx.stroke();
  // Labels.
  lowGuideCtx.fillStyle = 'white';
  lowGuideCtx.font = '12px sans-serif';
  lowGuideCtx.fillText('255 (max amplitude)', 2, 12);
  lowGuideCtx.fillText('0 (min amplitude)', 2, lowFreqCanvasGuides.height - 2);
}

// Draw static guides for the full-range heatmap.
function drawHeatmapGuides(maxFrequency) {
  heatmapGuideCtx.clearRect(0, 0, heatmapCanvasGuides.width, heatmapCanvasGuides.height);
  heatmapGuideCtx.strokeStyle = 'white';
  heatmapGuideCtx.lineWidth = 1;
  heatmapGuideCtx.beginPath();
  // Horizontal guide lines at the top and bottom.
  heatmapGuideCtx.moveTo(0, 0);
  heatmapGuideCtx.lineTo(heatmapCanvasGuides.width, 0);
  heatmapGuideCtx.moveTo(0, heatmapCanvasGuides.height);
  heatmapGuideCtx.lineTo(heatmapCanvasGuides.width, heatmapCanvasGuides.height);
  heatmapGuideCtx.stroke();
  // Labels.
  heatmapGuideCtx.fillStyle = 'white';
  heatmapGuideCtx.font = '12px sans-serif';
  heatmapGuideCtx.fillText(`${maxFrequency.toFixed(0)} Hz (max)`, 2, 12);
  heatmapGuideCtx.fillText(`0 Hz (min)`, 2, heatmapCanvasGuides.height - 2);
}

fileInput.addEventListener('change', function() {
  const file = this.files[0];
  if (!file) return;
  
  const reader = new FileReader();
  reader.onload = function(e) {
    const arrayBuffer = e.target.result;
    // Create a new AudioContext.
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    
    audioCtx.decodeAudioData(arrayBuffer, function(audioBuffer) {
      // Create an audio source.
      const source = audioCtx.createBufferSource();
      source.buffer = audioBuffer;
      
      // Create two AnalyserNodes.
      const analyserLow = audioCtx.createAnalyser();
      const analyserHeat = audioCtx.createAnalyser();
      analyserLow.fftSize = 2048;
      analyserHeat.fftSize = 2048;
      const bufferLengthLow = analyserLow.frequencyBinCount;
      const frequencyDataLow = new Uint8Array(bufferLengthLow);
      const bufferLengthHeat = analyserHeat.frequencyBinCount;
      const frequencyDataHeat = new Uint8Array(bufferLengthHeat);
      
      // Connect the source to both analysers.
      source.connect(analyserLow);
      source.connect(analyserHeat);
      // Connect one analyser to the destination to hear the audio.
      analyserLow.connect(audioCtx.destination);
      
      // Low-frequency analysis: 20–150 Hz.
      const sampleRate = audioCtx.sampleRate;
      const freqResolution = sampleRate / analyserLow.fftSize;
      const lowIndex = Math.floor(20 / freqResolution);
      const highIndex = Math.ceil(150 / freqResolution);
      
      // For full-range heatmap, the max frequency is sampleRate/2.
      const maxFrequency = sampleRate / 2;
      
      // Draw the static guides.
      drawLowFreqGuides();
      drawHeatmapGuides(maxFrequency);
      
      // Start audio playback.
      source.start();
      
      // Animation loop for the low-frequency scrolling line graph.
      function drawLowFreq() {
        analyserLow.getByteFrequencyData(frequencyDataLow);
        let sum = 0, count = 0;
        for (let i = lowIndex; i < highIndex; i++) {
          sum += frequencyDataLow[i];
          count++;
        }
        const currentEnergy = count ? sum / count : 0;
        // Scroll the data canvas by 1 pixel to the left.
        const imageData = lowCtx.getImageData(1, 0, lowFreqCanvasData.width - 1, lowFreqCanvasData.height);
        lowCtx.putImageData(imageData, 0, 0);
        // Clear the rightmost column.
        lowCtx.fillStyle = 'black';
        lowCtx.fillRect(lowFreqCanvasData.width - 1, 0, 1, lowFreqCanvasData.height);
        // Map currentEnergy (0–255) to a vertical position.
        const y = lowFreqCanvasData.height - Math.floor((currentEnergy / 255) * lowFreqCanvasData.height);
        lowCtx.fillStyle = 'lime';
        lowCtx.fillRect(lowFreqCanvasData.width - 1, y, 1, 1);

        // Schedule the next frame if the audio is still playing.
        if (audioCtx.currentTime < audioBuffer.duration) {
          lowFreqAnimationId = requestAnimationFrame(drawLowFreq);
        }
      }

      // Animation loop for the full-range heatmap spectrogram.
      function drawHeatmap() {
        analyserHeat.getByteFrequencyData(frequencyDataHeat);
        // Scroll the data canvas by 1 pixel to the left.
        const imageData = heatmapCtx.getImageData(1, 0, heatmapCanvasData.width - 1, heatmapCanvasData.height);
        heatmapCtx.putImageData(imageData, 0, 0);
        // Clear the rightmost column.
        heatmapCtx.fillStyle = 'black';
        heatmapCtx.fillRect(heatmapCanvasData.width - 1, 0, 1, heatmapCanvasData.height);
        // Calculate vertical scale: flip so that lower frequencies appear at the bottom.
        const scaleY = heatmapCanvasData.height / bufferLengthHeat;
        for (let i = 0; i < bufferLengthHeat; i++) {
          const value = frequencyDataHeat[i];
          // Map the amplitude to a color hue (0 = red for high amplitude, 240 = blue for low amplitude).
          const hue = (1 - (value / 255)) * 240;
          heatmapCtx.fillStyle = `hsl(${hue}, 100%, 50%)`;
          const yPos = heatmapCanvasData.height - ((i + 1) * scaleY);
          heatmapCtx.fillRect(heatmapCanvasData.width - 1, yPos, 1, Math.ceil(scaleY));
        }

        // Schedule the next frame if the audio is still playing.
        if (audioCtx.currentTime < audioBuffer.duration) {
          heatmapAnimationId = requestAnimationFrame(drawHeatmap);
        }
      }

      // Start the animation loops.
      lowFreqAnimationId = requestAnimationFrame(drawLowFreq);
      heatmapAnimationId = requestAnimationFrame(drawHeatmap);
    }, function(error) {
      console.error("Error decoding audio data:", error);
    });
  };
  reader.readAsArrayBuffer(file);
});
