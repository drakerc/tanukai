import { baseApiUrl, axiosWithHeaders } from "../utility"
import * as actionTypes from "./actionTypes";

export const imageUrlSearchStart = () => {
  return {
    type: actionTypes.IMAGE_URL_SEARCH_START
  };
};

export const imageUrlSearchSuccess = response => {
  return {
    type: actionTypes.IMAGE_URL_SEARCH_SUCCESS,
    response: response
  };
};

export const imageUrlSearchFailed = error => {
  return {
    type: actionTypes.IMAGE_URL_SEARCH_FAILED,
    error: error
  };
};

export const imageUrlSearch = (imageUrl, paginationFrom = 0, paginationSize = 10) => {
  const partitions = localStorage.getItem("partitions") ? localStorage.getItem("partitions").split(',') : ['e621', 'danbooru'];
  const maximumRating = localStorage.getItem("maximum_rating") ? localStorage.getItem("maximum_rating") : 'explicit';

  return dispatch => {
      dispatch(imageUrlSearchStart());
      const data = {
        'image_url': decodeURIComponent(imageUrl),
        'partitions': partitions,
        'maximum_rating': maximumRating
      };
      axiosWithHeaders
        .post(baseApiUrl + "api/v1/upload-by-url", data)
        .then(res => {
          dispatch(imageUrlSearchSuccess(res));
        })
        .catch(err => {
          dispatch(imageUrlSearchFailed(err));
        });
    };
};
