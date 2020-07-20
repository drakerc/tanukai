import React from "react";
import {connect} from "react-redux";
import {NavLink, Redirect} from "react-router-dom";
import {authSignup} from "../store/actions/auth";

import {
  Button,
  Form,
  Grid,
  Header,
  Message,
  Container,
  Divider
} from "semantic-ui-react";

class RegistrationForm extends React.Component {
  state = {
    username: "",
    email: "",
    password1: "",
    password2: ""
  };

  handleSubmit = e => {
    e.preventDefault();
    const {username, email, password1, password2} = this.state;
    this.props.signup(username, email, password1, password2);
  };

  handleChange = e => {
    this.setState({[e.target.name]: e.target.value});
  };

  render() {
    const {username, email, password1, password2} = this.state;
    const {error, loading, isAuthenticated} = this.props;
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
              Welcome to Tanukai
            </Header>
            <p textAlign="center">
              Create an account and start searching
            </p>
            <Divider/>
            <p textAlign="center">
              Registered users can save search settings (safety, websites) and in the future, black/whitelisted tags,
              favorite images, etc.
            </p>
            <Divider/>
            {error && <p>Error: Could not create a new account</p>}
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
                value={email}
                name="email"
                fluid
                icon="mail"
                iconPosition="left"
                placeholder="E-mail address"
                error={(error && error.response.data.email) ?
                  {
                    content: error.response.data.email,
                    pointing: 'below',
                  } : false
                }
              />
              <Form.Input
                onChange={this.handleChange}
                fluid
                value={password1}
                name="password1"
                icon="lock"
                iconPosition="left"
                placeholder="Password"
                type="password"
                error={(error && error.response.data.password1) ?
                  {
                    content: error.response.data.password1,
                    pointing: 'below',
                  } : false
                }
              />
              <Form.Input
                onChange={this.handleChange}
                fluid
                value={password2}
                name="password2"
                icon="lock"
                iconPosition="left"
                placeholder="Confirm password"
                type="password"
                error={(error && error.response.data.password12) ?
                  {
                    content: error.response.data.password2,
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
                Signup
              </Button>
            </Form>
            <Message>
              Already have an account? <NavLink to="/login">Login</NavLink>
            </Message>
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
    signup: (username, email, password1, password2) =>
      dispatch(authSignup(username, email, password1, password2))
  };
};

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(RegistrationForm);
