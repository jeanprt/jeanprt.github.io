let oscillator1, isPlaying, pixelRatio, sizeOnScreen, segmentWidth, oscillator2, isDrawing;// setting up variables

const ac = new AudioContext();

isPlaying = false
isDrawing = true

analyser = new AnalyserNode(ac, { //creates the Webaudio analyser node that will be used to analyze signal and draw it
  smoothingTimeConstant: 1,
  fftSize: 2048
}),

dataArray = new Uint8Array(analyser.frequencyBinCount);

function draw () { //draws a frame on the canvas
  analyser.getByteTimeDomainData(dataArray);
  requestAnimationFrame(draw);
    if (isDrawing) {
    segmentWidth = canvas.width / analyser.frequencyBinCount;
    c.clearRect(0, 0, canvas.width, canvas.height);
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

osc1_gainNode = new GainNode(ac, { //this is a webaudio gainNode used to manage Osc1 volume
  gain: 0.5
})

osc2_gainNode = new GainNode(ac, { //this is a webaudio gainNode used to manage Osc2 volume
  gain: 0.5
})

master_gainNode = new GainNode(ac, { //this is a webaudio gainNode used to manage master volume
  gain: 0.5
})

function get_canvas() { // this initializes the canvas
  const canvas = document.getElementById("canvas"); 
  c = canvas.getContext('2d'); //sets canvas to 2 dimensions
  canvas.width = window.innerWidth; //sets canvas to fill the whole window width
  canvas.height = window.innerHeight/2; //sets canvas to use half window height
  pixelRatio = window.devicePixelRatio; //sets pixel ratio
  sizeOnScreen = canvas.getBoundingClientRect();
  canvas.width = sizeOnScreen.width * pixelRatio; 
  canvas.height = sizeOnScreen.height * pixelRatio; //sets canvas dimensions
  canvas.style.width = canvas.width / pixelRatio + "px";
  canvas.style.height = canvas.height / pixelRatio + "px";
  c.beginPath();
  c.moveTo(0, canvas.height / 2);
  c.lineTo(canvas.width, canvas.height / 2);
  c.strokeStyle = "rgb(168, 201, 219)";//change line color here
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
var splitter = ac.createChannelSplitter(2); // gets elements from DOM

    if (isPlaying) { //if it is already playing, stop.
    oscillator1.stop();
    oscillator2.stop();
    powerBtn.innerHTML = "Turn On";
    document.getElementById("on-off").style.background = "rgb(168, 201, 219)";
    document.getElementById("on-off").style.color = "rgb(24, 41, 49)";
    } else {
      document.getElementById("on-off").style.background = "rgb(24, 41, 49)";
      document.getElementById("on-off").style.color = "rgb(168, 201, 219)";
      oscillator1 = new OscillatorNode(ac, {// create Oscillato1 node
        type: osc1Type.value,
        frequency: osc1FreqSlider.value
      });
      oscillator2 = new OscillatorNode( ac, {//create oscillator2 node
        type: osc2Type.value,
        frequency: osc2FreqSlider.value});
      oscillator1.connect(osc1_gainNode);
      osc1_gainNode.connect(analyser);
      oscillator2.connect(osc2_gainNode);
      osc2_gainNode.connect(analyser);
      analyser.connect(master_gainNode)
      master_gainNode.connect(ac.destination);// sets up node connections
      oscillator1.start();
      oscillator2.start();//start the oscillatorw
      draw();//begin drawing
      powerBtn.innerHTML = "Turn Off";//change the DOM button state
    }
    isPlaying = !isPlaying;
 };

function osc1_freq_update(value) {//Updates the frequency of osc1 given a value (triggered from DOM)
      let freq = value;
  document.getElementById("osc1-frequencyValue").innerHTML = freq;
  if (oscillator1 && isPlaying) {
    oscillator1.frequency.value = freq;
  }
};

function osc2_freq_update(value) {//Updates the frequency of osc1 given a value (triggered from DOM)
      let freq = value;
  document.getElementById("osc2-frequencyValue").innerHTML = freq;
  if (oscillator2 && isPlaying) {
    oscillator2.frequency.value = freq;
  }
};

function osc1_waveform_update(value) {//updates osc1's waveform given a str (triggered from DOM)
    if (oscillator1 && isPlaying) {
    oscillator1.type = value
    }
};


function osc2_waveform_update(value) {//updates osc1's waveform given a str (triggered from DOM)
    if (oscillator2 && isPlaying) {
    oscillator2.type = value
    }
};


function osc1_gain_update(value) {//updates the gain applied to osc1 by its gain node (triggered from DOM)
    let gain = value
    document.getElementById("osc1-gainValue").innerHTML = gain
    if (oscillator1 && isPlaying) {
        osc1_gainNode.gain.value = gain
    }
};


function osc2_gain_update(value) {//updates the gain applied to osc2 by its gain node (triggered from DOM)
    let gain = value
    document.getElementById("osc2-gainValue").innerHTML = gain
    if (oscillator2 && isPlaying) {
        osc2_gainNode.gain.value = gain
    }
};


function master_gain_update(value) {//updates the gain applied to master gain node (triggered from DOM)
    let gain = value
    document.getElementById("master-gainValue").innerHTML = gain
    if (oscillator1 && isPlaying) {
        master_gainNode.gain.value = gain
    }
};

function toggle_draw() {//toggles wether or not the canvas draws current waveform or stays still
    isDrawing = !isDrawing;
}

