import React, { Component } from 'react';

export default class DateTime extends Component {
  componentWillMount() {
    this.state = {
      datetime: ""
    }
    setInterval(() => {
      this.setState({
        datetime: String(new Date())
      });
    }, 1000);
  }

  render() {
    return (
      <p><strong>Date Time</strong>: {this.state.datetime}</p>
    );
  }
}
