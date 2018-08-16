/*

  Usage
  ---

  let watch = new StopWatch();

  // starts the watch timer
  watch.startTimer(function(){
    // you can even run a callback for each interval, like updating the DOM!
  });

  watch.stopTimer();              // stops the watch timer
  watch.resetTimer();             // resets the watch timer
  watch.getTimeString();          // returns the time as a string like so ---> "00:01:17"
  watch.getTimeObj();             // returns an object like this ---> { hours: 0, minutes: 4, seconds: 27 }
  watch.getTimeObjFormatted();    // returns an object like this ---> { hours: '00', minutes: '04', seconds: '27' }

*/

const StopWatch = function StopWatch() {
  const self = this;

  let hours = 0;
  let minutes = 0;
  let seconds = 0;

  let timer;
  let on = false;

  self.startTimer = function(callback) {
    if(on === true) { console.log('timer is already on.'); return; }
    on = true;
    timer = setInterval(function(){
      seconds++;
      if(seconds === 60) {
        seconds = 0;
        minutes++;
        if(minutes === 60) {
          minutes = 0;
          hours++;
        }
      }
      if(callback && callback.constructor === Function) {
        callback();
      }
    }, 1000);
    console.log('timer started');
  }

  self.stopTimer = function() {
    clearInterval(timer);
    on = false;
    console.log('timer ended: ', self.getTimeString());
  }

  self.resetTimer = function() {
    self.stopTimer();
    hours = 0;
    minutes = 0;
    seconds = 0;
  }

  self.getTimeString = function() {
    let hour = hours > 9 ? String(hours) : '0' + String(hours);
    let minute = minutes > 9 ? String(minutes) : '0' + String(minutes);
    let second = seconds > 9 ? String(seconds) : '0' + String(seconds);
    let timeString = hour + ':' + minute + ':' + second;
    return timeString;
  }

  self.getTimeObj = function() {
    return {
      hours: hours,
      minutes: minutes,
      seconds: seconds
    };
  }
  
  self.getTimeObjFormatted = function() {
    return {
      hours: hours > 9 ? String(hours) : '0' + String(hours),
      minutes: minutes > 9 ? String(minutes) : '0' + String(minutes),
      seconds: seconds > 9 ? String(seconds) : '0' + String(seconds)
    };
  }
  
  self.getHours = function() {
    return hours;
  }

  self.getMinutes = function() {
    return minutes;
  }

  self.getSeconds = function() {
    return seconds;
  }
}
