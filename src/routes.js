import React from "react";
import {Route} from "react-router-dom";
import Hoc from "./hoc/hoc";

import Login from "./containers/Login";
import Signup from "./containers/Signup";
import HomepageLayout from "./containers/Home";
import SearchResults from "./containers/SearchResults"
// import UploadedSearchResults from "./containers/UploadedSearchResults"
import DatabaseSearchResults from "./containers/DatabaseSearchResults"


const BaseRouter = () => (
    <Hoc>
        <Route path="/login" component={Login}/>
        <Route path="/signup" component={Signup}/>
        <Route path="/search-results/:imageId" component={SearchResults}/>
        {/*<Route path="/uploaded-image-search/:imageId" component={UploadedSearchResults}/>*/}
        <Route path="/database-image-search/:imageId" component={DatabaseSearchResults}/>
        <Route exact path="/" component={HomepageLayout}/>
    </Hoc>
);

export default BaseRouter;
