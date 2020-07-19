import {axiosWithHeaders, baseApiUrl} from "../utility"
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
    if (!token) {
      dispatch(putRatingFailed());
      return;
    }
    axiosWithHeaders
      .put(baseApiUrl + "api/v1/rating", rating)
      .then(res => {
        dispatch(putRatingSuccess(res));
      })
      .catch(err => {
        dispatch(putRatingFailed(err));
      });
  };
};
