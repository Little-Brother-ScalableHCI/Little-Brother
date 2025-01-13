// Get references to the sliders, input fields, and buttons
const cable1Slider = document.getElementById('cable1');
const cable2Slider = document.getElementById('cable2');
const cable3Slider = document.getElementById('cable3');
const cable1Value = document.getElementById('cable1-value');
const cable2Value = document.getElementById('cable2-value');
const cable3Value = document.getElementById('cable3-value');
const updateCablesButton = document.getElementById('update-cables');

const xCoordInput = document.getElementById('x-coord');
const yCoordInput = document.getElementById('y-coord');
const zCoordInput = document.getElementById('z-coord');
const xCoordValue = document.getElementById('x-coord-value');
const yCoordValue = document.getElementById('y-coord-value');
const zCoordValue = document.getElementById('z-coord-value');
const updatePositionButton = document.getElementById('update-position');
const homeButton = document.getElementById('home');

// Update slider value displays
cable1Slider.addEventListener('input', () => {
    cable1Value.textContent = cable1Slider.value;
});
cable2Slider.addEventListener('input', () => {
    cable2Value.textContent = cable2Slider.value;
});
cable3Slider.addEventListener('input', () => {
    cable3Value.textContent = cable3Slider.value;
});


// Update slider value displays
xCoordInput.addEventListener('input', () => {
    xCoordValue.textContent = xCoordInput.value;
});
yCoordInput.addEventListener('input', () => {
    yCoordValue.textContent = yCoordInput.value;
});
zCoordInput.addEventListener('input', () => {
    zCoordValue.textContent = zCoordInput.value;
});


// Send G0 command when "Update Cable Lengths" is clicked
updateCablesButton.addEventListener('click', () => {
    const command = `G0 X${cable1Slider.value} Y${cable2Slider.value} Z${cable3Slider.value}`;
    socket.emit('send-serial-command', command);
    getCableLengths();
});

// Send position update when "Update Position" is clicked
updatePositionButton.addEventListener('click', () => {
    const x = parseFloat(xCoordInput.value);
    const y = parseFloat(yCoordInput.value);
    const z = parseFloat(zCoordInput.value);
    socket.emit('update-position', { x, y, z });

    xCoordInput.value = 0;
    yCoordInput.value = 0;
    zCoordInput.value = 0;

    xCoordValue.textContent = x;
    yCoordValue.textContent = y;
    zCoordValue.textContent = z;
    getCableLengths();
});

homeButton.addEventListener('click', () => {
    socket.emit('home');
});

// Function to get current cable lengths from the server
function getCableLengths() {
    socket.emit('get-cable-lengths');
}

// Handle the 'cable-lengths' event from the server
socket.on('cable-lengths', (data) => {
    console.log(data);
    cable1Slider.value = data.x;
    cable2Slider.value = data.y;
    cable3Slider.value = data.z;

    // Update the displayed values
    cable1Value.textContent = data.x;
    cable2Value.textContent = data.y;
    cable3Value.textContent = data.z;
});

socket.on('connect', () => {
    console.log('Connected to server');
    getCableLengths();
});
