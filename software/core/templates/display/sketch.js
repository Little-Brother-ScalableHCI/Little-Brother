var w = window.innerWidth;
var h = window.innerHeight;

var itemFound;
var spotlight;
var arrow;

var orange;
var blue;

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
  constructor(x, y, minDiameter, maxDiameter, maxStrokeWeight, speed = 4, state = 0) {
    this.x = x;
    this.y = y;
    this.minDiameter = minDiameter;
    this.maxDiameter = maxDiameter;
    this.diameter = minDiameter + (maxDiameter - minDiameter) * state;
    this.maxStrokeWeight = maxStrokeWeight;
    this.strokeWeight = maxStrokeWeight;
    this.speed = speed;
    this.state = state;
    this.blur = 3;
  }

  display() {
    drawingContext.filter = `blur(${this.blur}px)`;
    noFill();
    stroke(orange);
    strokeWeight(this.strokeWeight);
    circle(this.x, this.y, this.diameter);
    // reset the filter
    drawingContext.filter = 'none';
  }

  animate() {
    if (this.diameter >= this.maxDiameter) {
      this.diameter = this.minDiameter;
      this.strokeWeight = this.maxStrokeWeight;
      this.blur = 3;
    }
    this.strokeWeight = this.maxStrokeWeight * (1 - (this.diameter - this.minDiameter) / (this.maxDiameter - this.minDiameter));
    this.diameter += this.speed;
    this.blur += 0.15;
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

class MovingArrow {
  constructor(angle, speed = 22) {
    this.angle = angle;
    this.speed = speed;
    this.x = w / 2;
    this.y = h / 2;
    this.size = h / 4;
    this.maxBlur = 40; // Maximum blur at the edges
    this.minBlur = 0; // Minimum blur at the center
    this.nextAngle = null;
  }

  display() {
    // Calculate blur based on distance from the center
    let distFromCenter = dist(this.x, this.y, w/2, h/2);
    let maxDist = dist(0, 0, w/2, h/2);
    // Map distance to blur value
    this.blur = map(distFromCenter, 0, maxDist, this.minBlur, this.maxBlur);
    drawingContext.filter = `blur(${this.blur}px)`;
    stroke(255);
    strokeWeight(50);
    translate(this.x, this.y);
    rotate(45 + this.angle);
    line(0, 0, 0, this.size);
    line(0, 0, this.size, 0);
    // reset filter
    drawingContext.filter = 'none';
  }

  animate() {
    // Wrap around the screen - reorient if nextAngle is set
    if (this.x - this.size > w || this.x + this.size < 0 || this.y - this.size > h || this.y + this.size < 0) {
      this.x = w - this.x;
      this.y = h - this.y;
      if (this.nextAngle) {
        this.x = w / 2;
        this.y = h / 2;
        this.angle = this.nextAngle;
        this.nextAngle = null;
      }
    }
    // Increment the position of the arrow
    this.x += this.speed * sin(this.angle);
    this.y -= this.speed * cos(this.angle);
    
  }

  update(angle) {
    this.nextAngle = angle;
  }
}


function setup() {
  createCanvas(w, h);
  frameRate(30);
  angleMode(DEGREES);
  orange = color("#fca103");
  blue = color("#2e45ed");

  spotlight = new SearchingItem(h * 0.95);
  itemFound = new ItemFound(w/2, h/2, h/3, h/1.5, 10);
  arrow = new MovingArrow(0);
}

function draw() {
  background(0);
  // itemFound.display();
  // itemFound.animate();
  // spotlight.display();
  arrow.display()
  arrow.animate();
}

window.onresize = function() {
  w = window.innerWidth;
  h = window.innerHeight;
  resizeCanvas(w, h);
};
