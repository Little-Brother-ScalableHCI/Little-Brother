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
const updatePositionButton = document.getElementById('update-position');

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

// Send G0 command when "Update Cable Lengths" is clicked
updateCablesButton.addEventListener('click', () => {
    const command = `G0 X${cable1Slider.value} Y${cable2Slider.value} Z${cable3Slider.value}`;
    socket.emit('send-serial-command', command);
});

// Send position update when "Update Position" is clicked
updatePositionButton.addEventListener('click', () => {
    const x = parseFloat(xCoordInput.value);
    const y = parseFloat(yCoordInput.value);
    socket.emit('update-position', { x, y });
});
