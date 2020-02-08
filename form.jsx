<!DOCTYPE html>
<html>
<script src="https://unpkg.com/react@16/umd/react.production.min.js"></script>
<script src="https://unpkg.com/react-dom@16/umd/react-dom.production.min.js"></script>
<script src="https://unpkg.com/babel-standalone@6.15.0/babel.min.js"></script>
<body>

<div id="mydiv"></div>

<script type="text/babel">
class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = { username: '' };
  }
  mySubmitHandler = (event) => {
    event.preventDefault();
    alert("You are submitting " + this.state.username);
  }
  myChangeHandler = (event) => {
    this.setState({username: event.target.value});
  }
  myClickHandler = (event) => {
    this.setState({username: event.target.value});
    alert("Setted");
    alert(this.state.username);
  }

  render() {
    return (
      <form onSubmit={this.mySubmitHandler}>
      <h1>Hello {this.state.username}</h1>
      <p>Enter your name, and submit:</p>
      <input
        type='text'
        onChange={this.myChangeHandler}
      />
      <input
        type='button'
        onClick={this.myClickHandler}
      />
      <input
        type='submit'
      />
      </form>
    );
}

}
ReactDOM.render(<App />, document.getElementById('mydiv'))
</script>

</body>
</html>



