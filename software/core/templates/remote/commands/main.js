const commandInput = document.getElementById('command-input');
const commandOutput = document.getElementById('messages');
const sendButton = document.getElementById('send-button');

sendButton.addEventListener('click', () => {
    const command = commandInput.value;
    commandInput.value = '';
    socket.emit('send-command', command);
});

socket.on('commands', (commands) => {
    commandOutput.innerHTML = '';
    commands.forEach(command => {
        commandOutput.innerHTML += `<p>${command['intent']}: ${command['object']}</p>`;
    });
});

socket.emit('get-commands');
setInterval(() => {
    socket.emit('get-commands');
}, 1000);
