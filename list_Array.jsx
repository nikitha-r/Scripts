import React from 'react';
import ReactDOM from 'react-dom';
import axios from 'axios';
import logo from './logo.svg';
import './App.css';

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
        shop: [
            {id: 35, name: 'jumper', color: 'red', price: 20},
            {id: 42, name: 'shirt', color: 'blue', price: 15},
            {id: 56, name: 'pants', color: 'green', price: 25},
            {id: 71, name: 'socks', color: 'black', price: 5},
            {id: 72, name: 'socks', color: 'white', price: 5},
        ]
    };
  }
  render() {
   const items = this.state.shop.map((item, key) =>
        <li key={item.id}>{item.name}</li>
);

    return (
      <div>
      {items}
      </div>
    );
  }
}

export default App;
