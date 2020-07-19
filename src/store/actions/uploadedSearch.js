import axios from "axios";
import { baseApiUrl } from "../utility"
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
  const partitions = localStorage.getItem("partitions");
  const maximumRating = localStorage.getItem("maximum_rating");
  const params = new URLSearchParams({
    pagination_from: paginationFrom,
    pagination_size: paginationSize,
    partitions: partitions,
    maximum_rating: maximumRating
  });
  return dispatch => {
    dispatch(uploadedSearchStart());
    axios
      .get(baseApiUrl + "api/v1/uploaded-image-search/" + imageId + "?" + params.toString())
      .then(res => {
        dispatch(uploadedSearchSuccess(res));
      })
      .catch(err => {
        dispatch(uploadedSearchFailed(err));
      });
  };
};
