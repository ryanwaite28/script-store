function randomValue(){
  return Math.random().toString(36).substr(2, 34);
}

function randomValueLong(){
  return Math.random().toString(36).substr(2, 34) + Math.random().toString(36).substr(2, 34);
}

function uniqueValue() {
    return String(Date.now()) +
	    Math.random().toString(36).substr(2, 34) +
	    Math.random().toString(36).substr(2, 34) +
	    Math.random().toString(36).substr(2, 34)
}
