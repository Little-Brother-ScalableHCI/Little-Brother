var w = window.innerWidth;
var h = window.innerHeight;

var itemFound;
var spotlight;
var arrow;

// Simple spotlight effect
class SearchingItem {
  constructor(diameter) {
    this.diameter = diameter;
  }
  display() {
    drawingContext.filter = 'blur(22px)';
    noStroke();
    fill(255);
    circle(w/2, h/2, this.diameter);
  }
}

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

  display() {
    drawingContext.filter = 'blur(6px)';
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
class ItemFound {
  constructor(x, y, minDiameter, maxDiameter, maxStrokeWeight) {
    this.circles = [];
    let offsets = [0, 1 / 3, 2 / 3]; // Offsets
    for (let offset of offsets) {
      this.circles.push(new GrowingCircle(x, y, minDiameter, maxDiameter, maxStrokeWeight, 2, offset));
    }
  }

  display() {
    for (let circle of this.circles) {
      circle.display();
    }
  }

  animate() {
    for (let circle of this.circles) {
      circle.animate();
    }
  }

  update(x, y, minDiameter, maxDiameter, maxStrokeWeight) {
    for (let circle of this.circles) {
      circle.x = x;
      circle.y = y;
      circle.minDiameter = minDiameter;
      circle.maxDiameter = maxDiameter;
      circle.maxStrokeWeight = maxStrokeWeight;
    }
  }
}

class FollowMe {
  constructor(angle) {
    this.angle = angle
  }

  display() {
    stroke(255);
    strokeWeight(50);
    translate(w/2, h/2);
    rotate(45 + this.angle);
    line(0, 0, 0, h/4);
    line(0, 0, h/4, 0);
  }

  update(angle) {
    this.angle = angle;
  }
}

function setup() {
  createCanvas(w, h);
  frameRate(60);
  angleMode(DEGREES);
  // spotlight = new SearchingItem(h * 0.95);
  itemFound = new ItemFound(w/2, h/2, h/3, h/1.5, 10);
  // arrow = new FollowMe(0);
}

function draw() {
  background(0);
  itemFound.display();
  itemFound.animate();
  // spotlight.display();
  // arrow.display();
  // arrow.update(frameCount % 360);
}

window.onresize = function() {
  w = window.innerWidth;
  h = window.innerHeight;
  resizeCanvas(w, h);
};
