import React from "react";
import ReactDOM from "react-dom";
import App from "./App";
import registerServiceWorker from "./registerServiceWorker";
import {createStore, compose, applyMiddleware, combineReducers} from "redux";
import {Provider} from "react-redux";
import thunk from "redux-thunk";

import authReducer from "./store/reducers/auth";
import imageSearchReducer from "./store/reducers/imagesearch"
import databaseSearchReducer from "./store/reducers/databaseSearch"
import uploadedSearchReducer from "./store/reducers/uploadedSearch"
import getSettingsReducer from "./store/reducers/settings"
import putPartitionsReducer from "./store/reducers/partitions"
import putRatingReducer from "./store/reducers/rating"


const composeEnhances = window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__ || compose;

const rootReducer = combineReducers({
    auth: authReducer,
    imageSearch: imageSearchReducer,
    databaseSearch: databaseSearchReducer,
    uploadedSearch: uploadedSearchReducer,
    getSettings: getSettingsReducer,
    putPartitions: putPartitionsReducer,
    putRating: putRatingReducer,
});

const store = createStore(rootReducer, composeEnhances(applyMiddleware(thunk)));

const app = (
    <Provider store={store}>
        <App/>
    </Provider>
);

ReactDOM.render(app, document.getElementById("root"));
registerServiceWorker();
