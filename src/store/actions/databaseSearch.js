import axios from "axios";
import { baseApiUrl } from "../utility"
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

export const databaseSearch = (imageId, paginationFrom = 0, paginationSize = 10) => {
  const partitions = localStorage.getItem("partitions");
  const maximumRating = localStorage.getItem("maximum_rating");
  const params = new URLSearchParams({
    pagination_from: paginationFrom,
    pagination_size: paginationSize,
    partitions: partitions,
    maximum_rating: maximumRating
  });
  return dispatch => {
    dispatch(databaseSearchStart());
    axios
      .get(baseApiUrl + "api/v1/database-image-search/" + imageId + "?" + params.toString())
      .then(res => {
        dispatch(databaseSearchSuccess(res));
      })
      .catch(err => {
        dispatch(databaseSearchFailed(err));
      });
  };
};
