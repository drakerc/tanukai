import React, {Component} from "react";
import {BrowserRouter as Router} from "react-router-dom";
import {connect} from "react-redux";
import BaseRouter from "./routes";
import * as actions from "./store/actions/auth";
import "semantic-ui-css/semantic.min.css";
import CustomLayout from "./containers/Layout";
import ScrollToTop from "./utils/ScrollToTop"

require('dotenv').config()

class App extends Component {
    componentDidMount() {
        this.props.onTryAutoSignup();
    }

    render() {
        return (
            <Router>
                <ScrollToTop>
                    <CustomLayout {...this.props}>
                        <BaseRouter/>
                    </CustomLayout>
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
        onTryAutoSignup: () => dispatch(actions.authCheckState())
    };
};

export default connect(
    mapStateToProps,
    mapDispatchToProps
)(App);
