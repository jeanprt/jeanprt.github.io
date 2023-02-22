let oscillator1, isPlaying, pixelRatio, sizeOnScreen, segmentWidth, oscillator2, isDrawing;
const ac = new AudioContext();
isPlaying = false
isDrawing = true

analyser = new AnalyserNode(ac, {
  smoothingTimeConstant: 1,
  fftSize: 2048
}),

dataArray = new Uint8Array(analyser.frequencyBinCount);

function draw () {
  analyser.getByteTimeDomainData(dataArray);
  requestAnimationFrame(draw);
    if (isDrawing) {
    segmentWidth = canvas.width / analyser.frequencyBinCount;
    c.fillRect(0, 0, canvas.width, canvas.height);
    c.beginPath();
    c.moveTo(-100, canvas.height / 2);
    }
    if (isPlaying && isDrawing) {
      for (let i = 1; i < analyser.frequencyBinCount; i += 1) {
        let x = i * segmentWidth;
        let v = dataArray[i] / 128.0;
        let y = (v * canvas.height) / 2;
        c.lineTo(x, y);
  }
}
c.lineTo(canvas.width + 100, canvas.height / 2);
c.stroke();
};

osc1_gainNode = new GainNode(ac, {
    gain: 0.5
})

osc2_gainNode = new GainNode(ac, {
    gain: 0.5
})

master_gainNode = new GainNode(ac, {
    gain: 0.5
})

function get_canvas() {
const canvas = document.getElementById("canvas");
c = canvas.getContext('2d');
canvas.width = window.innerWidth;
canvas.height = window.innerHeight/2;
pixelRatio = window.devicePixelRatio;
sizeOnScreen = canvas.getBoundingClientRect();
canvas.width = sizeOnScreen.width * pixelRatio;
canvas.height = sizeOnScreen.height * pixelRatio;
canvas.style.width = canvas.width / pixelRatio + "px";
canvas.style.height = canvas.height / pixelRatio + "px";
c.fillStyle = "#181818";
c.fillRect(0, 0, canvas.width, canvas.height);
c.strokeStyle = "#33ee55";
c.beginPath();
c.moveTo(0, canvas.height / 2);
c.lineTo(canvas.width, canvas.height / 2);
c.stroke();
}


function on_off() {
let powerBtn = document.getElementById("on-off");
osc1Type = document.getElementById("osc1-type");
osc2Type = document.getElementById("osc2-type");
osc1FreqSlider = document.getElementById("osc1-frequency");
osc2FreqSlider = document.getElementById("osc2-frequency");
osc1GainSlider = document.getElementById("osc1-gain");
osc2GainSlider = document.getElementById("osc2-gain");
var mixedAudio = ac.createMediaStreamDestination();
var merger = ac.createChannelMerger(2);
var splitter = ac.createChannelSplitter(2);

var channel1 = [0, 1];
var channel2 = [1, 0];
    if (isPlaying) {
    oscillator1.stop();
    oscillator2.stop();
    powerBtn.innerHTML = "Turn On";
    document.getElementById("on-off").style.background = "red";
    } else {
      document.getElementById("on-off").style.background = "green";
      oscillator1 = new OscillatorNode(ac, {
        type: osc1Type.value,
        frequency: osc1FreqSlider.value
      });
      oscillator2 = new OscillatorNode( ac, {
      type: osc2Type.value,
      frequency: osc2FreqSlider.value});
      oscillator1.connect(osc1_gainNode);
      osc1_gainNode.connect(master_gainNode);
      oscillator2.connect(osc2_gainNode);
      osc2_gainNode.connect(master_gainNode);
      master_gainNode.connect(analyser)
      analyser.connect(ac.destination);
      oscillator1.start();
      oscillator2.start();
      draw();
      powerBtn.innerHTML = "Turn Off";
    }
    isPlaying = !isPlaying;
 };

function osc1_freq_update(value) {
      let freq = value;
  document.getElementById("osc1-frequencyValue").innerHTML = freq;
  if (oscillator1 && isPlaying) {
    oscillator1.frequency.value = freq;
  }
};

function osc2_freq_update(value) {
      let freq = value;
  document.getElementById("osc2-frequencyValue").innerHTML = freq;
  if (oscillator2 && isPlaying) {
    oscillator2.frequency.value = freq;
  }
};

function osc1_waveform_update(value) {
    if (oscillator1 && isPlaying) {
    oscillator1.type = value
    }
};


function osc2_waveform_update(value) {
    if (oscillator2 && isPlaying) {
    oscillator2.type = value
    }
};


function osc1_gain_update(value) {
    let gain = value
    document.getElementById("osc1-gainValue").innerHTML = gain
    if (oscillator1 && isPlaying) {
        osc1_gainNode.gain.value = gain
    }
};


function osc2_gain_update(value) {
    let gain = value
    document.getElementById("osc2-gainValue").innerHTML = gain
    if (oscillator2 && isPlaying) {
        osc2_gainNode.gain.value = gain
    }
};


function master_gain_update(value) {
    let gain = value
    document.getElementById("master-gainValue").innerHTML = gain
    if (oscillator1 && isPlaying) {
        master_gainNode.gain.value = gain
    }
};

function toggle_draw() {
    isDrawing = !isDrawing;
}

