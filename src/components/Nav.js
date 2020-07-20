import React from "react";
import {
  Container,
  Menu,
} from "semantic-ui-react";
import { Link } from "react-router-dom";

class Nav extends React.Component {
  render() {
    const { isAuthenticated, logout } = this.props;
    return (
      <Menu fixed="top" size='huge' secondary>
        <Container>
          <Link to="/">
            <Menu.Item header title="Homepage" className="logo">Tanuk<span className="logo--accent">ai</span></Menu.Item>
          </Link>
          <Menu.Menu position='right'>
            {isAuthenticated ? (
              <Menu.Item header onClick={logout}>
                Logout
              </Menu.Item>
            ) : (
                <React.Fragment>
                  <Link to="/login">
                    <Menu.Item header>Login</Menu.Item>
                  </Link>
                  <Link to="/signup">
                    <Menu.Item header>Signup</Menu.Item>
                  </Link>
                </React.Fragment>
              )}
          </Menu.Menu>
        </Container>
      </Menu>
    );
  }
}

export default Nav
