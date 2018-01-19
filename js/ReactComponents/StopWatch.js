import React, { Component } from 'react';

export default class StopWatch extends Component {
  state = {
    value: 0,
    on: false,
    padding: {padding: '10px'},
    margin: {margin: '10px'},
    watchStyle: {
      border: '1px solid grey',
      width: '500px',
      maxWidth: '95%',
      display: 'block',
      margin: 'auto',
      boxShadow: '0px 1px 3px rgba(0, 0, 0, 0.2)',
      marginBottom: '10px'
    }
  }

  hms(num) {
    var sec_num = num;
    var hours   = Math.floor(sec_num / 3600);
    var minutes = Math.floor((sec_num - (hours * 3600)) / 60);
    var seconds = sec_num - (hours * 3600) - (minutes * 60);

    if (hours   < 10) {hours   = "0"+hours;}
    if (minutes < 10) {minutes = "0"+minutes;}
    if (seconds < 10) {seconds = "0"+seconds;}

    return hours+':'+minutes+':'+seconds;
  }

  startResume() {
    if(this.state.on === true) { return; }
    this.clock = setInterval(() => {
      this.setState(prev =>  ({ on: true, value: prev.value + 1 }));
    }, 1000)
  }

  stop() {
    if(this.state.on === false) { return; }
    window.clearInterval(this.clock);
    this.setState({ on: false });
  }

  reset() {
    window.clearInterval(this.clock);
    this.setState({ value: 0, on: false });
  }

  render() {
    let { value, on } = this.state;
    let text = value > 0 ? 'Resume' : 'Start';
    let status = on === true ? 'On' : 'Off';
    let color = on === true ? 'green' : 'red';
    return (
      <div style={this.state.watchStyle}>
        <span>{this.hms(this.state.value)} <em><span style={{ color }}>{status}</span></em></span> |
        <button style={this.state.margin} onClick={() => { this.startResume() }}>{text}</button>
        <button style={this.state.margin} onClick={() => { this.stop() }}>Stop</button>
        <button style={this.state.margin} onClick={() => { this.reset() }}>Reset</button>
      </div>
    );
  }
}
