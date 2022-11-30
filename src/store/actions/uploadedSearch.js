import { baseApiUrl, axiosWithHeaders } from "../utility"
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

export const uploadedSearch = (imageId, paginationFrom = 0, paginationSize = 20) => {
  const partitions = localStorage.getItem("partitions") ? localStorage.getItem("partitions") : ['furaffinity', 'reddit'];
  // TODO: move default partitions somewhere else, leads to code duplication
  const maximumRating = localStorage.getItem("maximum_rating") ? localStorage.getItem("maximum_rating") : 'explicit';
  const params = new URLSearchParams({
    pagination_from: paginationFrom,
    pagination_size: paginationSize,
    partitions: partitions,
    maximum_rating: maximumRating
  });
  return dispatch => {
    dispatch(uploadedSearchStart());
    axiosWithHeaders
      .get(baseApiUrl + "api/v1/uploaded-image-search/" + imageId + "?" + params.toString())
      .then(res => {
        dispatch(uploadedSearchSuccess(res));
      })
      .catch(err => {
        dispatch(uploadedSearchFailed(err));
      });
  };
};
