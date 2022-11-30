import { baseApiUrl, axiosWithHeaders } from "../utility"
import * as actionTypes from "./actionTypes";

export const databaseSearchStart = () => {
  return {
    type: actionTypes.DATABASE_SEARCH_START
  };
};

export const databaseSearchSuccess = response => {
  return {
    type: actionTypes.DATABASE_SEARCH_SUCCESS,
    response: response
  };
};

export const databaseSearchFailed = error => {
  return {
    type: actionTypes.DATABASE_SEARCH_FAILED,
    error: error
  };
};

export const databaseSearch = (imageId, paginationFrom = 0, paginationSize = 20) => {
  const partitions = localStorage.getItem("partitions") ? localStorage.getItem("partitions") : ['furaffinity', 'reddit'];
  const maximumRating = localStorage.getItem("maximum_rating") ? localStorage.getItem("maximum_rating") : 'explicit';
  const params = new URLSearchParams({
    pagination_from: paginationFrom,
    pagination_size: paginationSize,
    partitions: partitions,
    maximum_rating: maximumRating
  });
  return dispatch => {
    dispatch(databaseSearchStart());
    axiosWithHeaders
      .get(baseApiUrl + "api/v1/database-image-search/" + imageId + "?" + params.toString())
      .then(res => {
        dispatch(databaseSearchSuccess(res));
      })
      .catch(err => {
        dispatch(databaseSearchFailed(err));
      });
  };
};
