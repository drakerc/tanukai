import React from "react";
import {NavLink, Redirect} from "react-router-dom";
import {connect} from "react-redux";

import {authLogin} from "../store/actions/auth";

import {
  Button,
  Form,
  Grid,
  Header,
  Message,
  Container,
  Divider,
} from "semantic-ui-react";

class LoginForm extends React.Component {
  state = {
    username: "",
    password: ""
  };

  handleChange = e => {
    this.setState({[e.target.name]: e.target.value});
  };

  handleSubmit = e => {
    e.preventDefault();
    const {username, password} = this.state;
    this.props.login(username, password);
  };

  render() {
    const {error, loading, isAuthenticated} = this.props;
    const {username, password} = this.state;
    if (isAuthenticated) {
      return <Redirect to="/"/>;
    }
    return (
      <Container>
        <Grid
          textAlign="center"
          verticalAlign="middle"
          relaxed
          columns={2}
          className="fullHeight"
        >
          <Grid.Column className="form--column">
            <Header as="h2" textAlign="center">
              Login to your account
            </Header>
            <Divider/>
            {error && <p>Error: Could not log in</p>}
            {(error && error.response.data.non_field_errors) && <p>{error.response.data.non_field_errors}</p>}
            <React.Fragment>
              <Form size="large" onSubmit={this.handleSubmit} className="form">
                <Form.Input
                  onChange={this.handleChange}
                  value={username}
                  name="username"
                  fluid
                  icon="user"
                  iconPosition="left"
                  placeholder="Username"
                  error={(error && error.response.data.username) ?
                    {
                      content: error.response.data.username,
                      pointing: 'below',
                    } : false
                  }
                />
                <Form.Input
                  onChange={this.handleChange}
                  fluid
                  value={password}
                  name="password"
                  icon="lock"
                  iconPosition="left"
                  placeholder="Password"
                  type="password"
                  error={(error && error.response.data.password) ?
                    {
                      content: error.response.data.password,
                      pointing: 'below',
                    } : false
                  }
                />
                <Button
                  fluid
                  size="large"
                  loading={loading}
                  disabled={loading}
                >
                  Login
                </Button>
              </Form>
              <Message>
                New to Tanukai? <NavLink to="/signup">Sign Up</NavLink>
              </Message>
            </React.Fragment>
          </Grid.Column>
        </Grid>
      </Container>
    );
  }
}

const mapStateToProps = state => {
  return {
    loading: state.auth.loading,
    error: state.auth.error,
    isAuthenticated: state.auth.token
  };
};

const mapDispatchToProps = dispatch => {
  return {
    login: (username, password) => dispatch(authLogin(username, password))
  };
};

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(LoginForm);
