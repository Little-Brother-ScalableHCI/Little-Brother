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
}, 33);

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
