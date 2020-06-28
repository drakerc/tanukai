import axios from "axios";
import * as actionTypes from "./actionTypes";

export const uploadedSearchStart = () => {
    return {
        type: actionTypes.UPLOADED_SEARCH_START
    };
};

export const uploadedSearchSuccess = response => {
    return {
        type: actionTypes.UPLOADED_SEARCH_SUCCESS,
        response: response
    };
};

export const uploadedSearchFailed = error => {
    return {
        type: actionTypes.UPLOADED_SEARCH_FAILED,
        error: error
    };
};

export const uploadedSearch = (imageId, paginationFrom = 0, paginationSize = 10) => {
    return dispatch => {
        dispatch(uploadedSearchStart());
        axios
            .get("http://127.0.0.1:8000/api/v1/uploaded-image-search/" + imageId + "?pagination_from=" + paginationFrom + '&pagination_size=' + paginationSize)
            .then(res => {
                dispatch(uploadedSearchSuccess(res));
            })
            .catch(err => {
                dispatch(uploadedSearchFailed(err));
            });
    };
};
