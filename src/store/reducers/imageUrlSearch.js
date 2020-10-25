import * as actionTypes from "../actions/actionTypes";
import { updateObject } from "../utility";

const initialState = {
  response: null,
  error: null,
  loading: false
};

const imageUrlSearchStart = (state, action) => {
  return updateObject(state, {
    error: null,
    loading: true
  });
};

const imageUrlSearchSuccess = (state, action) => {
  return updateObject(state, {
    response: action.response,
    error: null,
    loading: false
  });
};

const imageUrlSearchFailed = (state, action) => {
  return updateObject(state, {
    error: action.error,
    loading: false
  });
};

const reducer = (state = initialState, action) => {
  switch (action.type) {
    case actionTypes.IMAGE_URL_SEARCH_START:
      return imageUrlSearchStart(state, action);
    case actionTypes.IMAGE_URL_SEARCH_SUCCESS:
      return imageUrlSearchSuccess(state, action);
    case actionTypes.IMAGE_URL_SEARCH_FAILED:
      return imageUrlSearchFailed(state, action);
    default:
      return state;
  }
};

export default reducer;
