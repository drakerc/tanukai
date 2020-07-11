import axios from "axios";
import {baseApiUrl} from "../utility"
import * as actionTypes from "./actionTypes";

export const putRatingStart = () => {
    return {
        type: actionTypes.PUT_RATING_START
    };
};

export const putRatingSuccess = response => {
    return {
        type: actionTypes.PUT_RATING_SUCCESS,
        response: response
    };
};

export const putRatingFailed = error => {
    return {
        type: actionTypes.PUT_RATING_FAILED,
        error: error
    };
};

export const putRating = (rating) => {
    localStorage.setItem("maximum_rating", rating);
    return dispatch => {
        dispatch(putRatingStart());
        const token = localStorage.getItem("token");
        const headers = token ? {'Authorization': 'Token ' + token} : null;
        if (!headers) {
            dispatch(putRatingFailed());
            return;
        }
        axios
            .put(baseApiUrl + "api/v1/rating", rating, {'headers': headers})
            .then(res => {
                dispatch(putRatingSuccess(res));
            })
            .catch(err => {
                dispatch(putRatingFailed(err));
            });
    };
};
