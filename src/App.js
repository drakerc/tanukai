import React, { Component } from "react";
import { BrowserRouter as Router } from "react-router-dom";
import { connect } from "react-redux";

import "semantic-ui-css/semantic.min.css";

import Routes from "./routes";

import ScrollToTop from "./utils/ScrollToTop"

import * as actions from "./store/actions/auth";
import { logout } from "./store/actions/auth";

import Nav from "./components/Nav";
import Footer from "./components/Footer";

import './styles/styles.scss'

require('dotenv').config()

class App extends Component {
  componentDidMount() {
    this.props.onTryAutoSignup();
  }

  render() {
    const { isAuthenticated, logout } = this.props;
    return (
      <Router>
        <ScrollToTop>
          <Nav isAuthenticated={isAuthenticated} />
          <Routes isAuthenticated={isAuthenticated} />
          <Footer />
        </ScrollToTop>
      </Router>
    );
  }
}

const mapStateToProps = state => {
  return {
    isAuthenticated: state.auth.token !== null
  };
};

const mapDispatchToProps = dispatch => {
  return {
    onTryAutoSignup: () => dispatch(actions.authCheckState()),
    logout: () => dispatch(logout())
  };
};

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(App);
