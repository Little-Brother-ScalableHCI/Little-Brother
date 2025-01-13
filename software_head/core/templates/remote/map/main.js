let liveFeed;
let items = [];
let currentAspect = 1;
const parent = document.getElementById('p5-canvas');

function setup() {
    const w = parent.offsetWidth;
    const h = parent.offsetHeight;
    const canvas = createCanvas(w, h);
    canvas.parent('p5-canvas');
    currentAspect = w / h;
}

function windowResized() {
    const w = parent.offsetWidth;
    const h = parent.offsetHeight;
    resizeCanvas(w, h);
}

function draw() {
    background(0);

    if (liveFeed) {
        let aspectCanvas = width / height;
        let aspectFeed = liveFeed.width / liveFeed.height;
        let ratio = aspectCanvas / aspectFeed;

        // console.log(aspectFeed, currentAspect);

        if (aspectCanvas != currentAspect) {
            currentAspect = aspectFeed;
            resizeCanvas(parent.offsetWidth, parent.offsetWidth / aspectFeed);
            console.log(parent.offsetWidth, parent.offsetWidth / aspectFeed);
        }

        if (aspectFeed < aspectCanvas) {
            scale(height / liveFeed.height);
        } else {
            scale(width / liveFeed.width);
        }
        image(liveFeed, 0, 0, liveFeed.width, liveFeed.height);
        // if

        // let s = width / liveFeed.width;

        items.forEach((item) => {
            push();
            translate(width / 2, height / 2);
            scale(100);
            stroke(255);
            strokeWeight(0.1);
            circle(item.world[0], item.world[1], 0.1);
            pop();
            push();
            stroke(255);
            strokeWeight(2);
            noFill();
            translate(item.coords[0], item.coords[1]);
            rectMode(CENTER);
            rect(0, 0, item.size[0], item.size[1]);
            textSize(16);
            fill(255);
            text(item.lbl, -item.size[0]/2, -item.size[1]/2);
            pop();
        });
    }
};


setInterval(() => {
    socket.emit("get-camera-feed");
}, 200);

socket.on("camera-feed", (data) => {
    let blob = new Blob([data], { type: 'image/png' });
    let url = URL.createObjectURL(blob);

    loadImage(url, (img) => {
        liveFeed = img;
        URL.revokeObjectURL(url);
    }, (event) => {
        console.error("Error loading image:", event);
    });
});

setInterval(() => {
    socket.emit("get-items");
}, 33);

socket.on("items", (itms) => {
    items = eval(itms);
    console.log(itms);
});


let findCellPhoneButton = document.getElementById('find-cell-phone');
findCellPhoneButton.addEventListener('click', () => {
    socket.emit('send-command', "Where is my cell phone");
});
let findScrewdriverButton = document.getElementById('find-screwdriver');
findScrewdriverButton.addEventListener('click', () => {
    socket.emit('send-command', "Where is the screwdriver");
});
let findPliersButton = document.getElementById('find-pliers');
findPliersButton.addEventListener('click', () => {
    socket.emit('send-command', "Where are the pliers");
});
let findHammerButton = document.getElementById('find-hammer');
findHammerButton.addEventListener('click', () => {
    socket.emit('send-command', "Where is the hammer");
});
let findWrenchButton = document.getElementById('find-wrench');
findWrenchButton.addEventListener('click', () => {
    socket.emit('send-command', "Where is the wrench");
});
let findScissorsButton = document.getElementById('find-scissors');
findScissorsButton.addEventListener('click', () => {
    socket.emit('send-command', "Where are the scissors");
});
let findMouseButton = document.getElementById('find-mouse');
findMouseButton.addEventListener('click', () => {
    socket.emit('send-command', "Where is the mouse");
});
