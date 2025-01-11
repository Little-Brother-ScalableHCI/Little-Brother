var w = window.innerWidth;
var h = window.innerHeight;

var objectFound;

// Makes a circle grow from minDiameter to maxDiameter, while decreasing strokeWeight from maxStrokeWeight to 0
class GrowingCircle {
  constructor(x, y, minDiameter, maxDiameter, maxStrokeWeight, speed = 2, state = 0) {
    this.x = x;
    this.y = y;
    this.minDiameter = minDiameter;
    this.maxDiameter = maxDiameter;
    this.diameter = minDiameter + (maxDiameter - minDiameter) * state;
    this.maxStrokeWeight = maxStrokeWeight;
    this.strokeWeight = maxStrokeWeight;
    this.speed = speed;
    this.state = state;
  }

  show() {
    drawingContext.filter = 'blur(8px)';
    noFill();
    stroke(255);
    strokeWeight(this.strokeWeight);
    circle(this.x, this.y, this.diameter);
    // reset the filter
    drawingContext.filter = 'none';
  }

  animate() {
    if (this.diameter >= this.maxDiameter) {
      this.diameter = this.minDiameter;
      this.strokeWeight = this.maxStrokeWeight;
    }
    this.strokeWeight = this.maxStrokeWeight * (1 - (this.diameter - this.minDiameter) / (this.maxDiameter - this.minDiameter));
    this.diameter += this.speed;
  }
}

// Creates 3 centered GrowingCircles with an offset
class ObjectFound {
  constructor(x, y, minDiameter, maxDiameter, maxStrokeWeight) {
    this.circles = [];
    let offsets = [0, 1 / 3, 2 / 3]; // Offsets
    for (let offset of offsets) {
      this.circles.push(new GrowingCircle(x, y, minDiameter, maxDiameter, maxStrokeWeight, 2, offset));
    }
  }

  show() {
    for (let circle of this.circles) {
      circle.show();
    }
  }

  animate() {
    for (let circle of this.circles) {
      circle.animate();
    }
  }
}

function setup() {
  createCanvas(w, h);
  frameRate(60);
  objectFound = new ObjectFound(w / 2, h / 2, h / 3, h / 1.5, 10);
}

function draw() {
  background(0);
  objectFound.show();
  objectFound.animate();
}

window.onresize = function() {
  w = window.innerWidth;
  h = window.innerHeight;
  resizeCanvas(w, h);
};
