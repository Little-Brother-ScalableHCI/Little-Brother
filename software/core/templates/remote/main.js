const socket = io.connect(window.location.origin, {
    path: "/Little-Brother/socket.io",
    cors: {
        origin: "*",
        methods: ["GET", "POST"]
    },
	agent: false,
	upgrade: false,
	rejectUnauthorized: false,
    transports: ["websocket"],
    query: "source=display"
});

socket.on('connect', () => {
    console.log('Connected to server');
});

socket.emit('cbs-home');
