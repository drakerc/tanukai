import React from "react";
import { Route } from "react-router-dom";
import Hoc from "./hoc/hoc";

import Login from "./containers/Login";
import Signup from "./containers/Signup";
import Home from "./components/Home";
import SearchResults from "./containers/SearchResults"

const BaseRouter = (isAuthenticated) => (
  <Hoc>
    <Route path="/login" component={Login} isAuthenticated={isAuthenticated} />
    <Route path="/signup" component={Signup} isAuthenticated={isAuthenticated} />
    <Route path="/search-results/:imageId" component={SearchResults} />
    <Route path="/database-image-search/:dbImageId" component={SearchResults} />
    <Route path="/url-search-results/:imageUrl" component={SearchResults} />
    <Route exact path="/" component={Home} isAuthenticated={isAuthenticated}/>
  </Hoc>
);

export default BaseRouter;
