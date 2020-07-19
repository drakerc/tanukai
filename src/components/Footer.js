import React from "react";
import { Link, withRouter } from "react-router-dom";
import {
  Container,
  Divider,
  Grid,
  Header,
  Image,
  List,
  Segment
} from "semantic-ui-react";

class Footer extends React.Component {
  render() {
    return (
      <Segment
        inverted
        vertical
        className="footer"
      >
        <Container textAlign="center">
          <Link to="/" title="Homepage">
            <div className="logo logo--light">Tanuk<span className="logo--accent">ai</span></div>
          </Link>
          <List horizontal inverted divided link size="small">
            <List.Item>
              Tanukai {new Date().getFullYear()} &copy; All rights reserved
            </List.Item>
          </List>
        </Container>
      </Segment>
    );
  }
}

export default Footer