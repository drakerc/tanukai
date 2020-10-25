import { baseApiUrl, axiosWithHeaders } from "../utility"
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

export const imageSearch = (images, imageUrl, partitions, maximumRating, privateImage) => {
  localStorage.setItem("partitions", partitions);
  localStorage.setItem("maximum_rating", maximumRating);

    if (imageUrl) {
    return dispatch => {
      dispatch(searchStart());
      const data = {
        'image_url': imageUrl,
        'partitions': partitions,
        'maximum_rating': maximumRating
      };
      axiosWithHeaders
        .post(baseApiUrl + "api/v1/upload-by-url", data)
        .then(res => {
          dispatch(searchSuccess(res));
        })
        .catch(err => {
          dispatch(searchFailed(err));
        });
    };
  }

  const data = new FormData();
  data.append('image', images);
  data.append('partitions', partitions);
  data.append('maximum_rating', maximumRating);
  data.append('private_image', privateImage);

  return dispatch => {
    dispatch(searchStart());
    axiosWithHeaders
      .post(baseApiUrl + "api/v1/upload-image", data, { headers: { 'Content-Type': 'multipart/form-data' } })
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
