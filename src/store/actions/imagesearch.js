import axios from "axios";
import {baseApiUrl} from "../utility"
import * as actionTypes from "./actionTypes";

export const searchStart = () => {
    return {
        type: actionTypes.SEARCH_START
    };
};

export const searchSuccess = response => {
    return {
        type: actionTypes.SEARCH_SUCCESS,
        response: response
    };
};

export const searchFailed = error => {
    return {
        type: actionTypes.SEARCH_FAILED,
        error: error
    };
};

export const searchReset = () => {
    return {
        type: actionTypes.SEARCH_RESET,
        response: null
    };
};

export const imageSearch = (images, partitions, maximumRating) => {
    const data = new FormData();
    data.append('file', images);
    data.append('partitions', partitions);
    data.append('maximum_rating', maximumRating);

    return dispatch => {
        dispatch(searchStart());
        axios
            .post(baseApiUrl + "api/v1/upload-image", data, {headers: {'Content-Type': 'multipart/form-data'}})
            .then(res => {
                dispatch(searchSuccess(res));
            })
            .catch(err => {
                dispatch(searchFailed(err));
            });
    };
};

export const resetProps = () => {
    return dispatch => {
        dispatch(searchReset());
    };
};
