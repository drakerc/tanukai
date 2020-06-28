import * as actionTypes from "../actions/actionTypes";
import { updateObject } from "../utility";

const initialState = {
  response: null,
  error: null,
  loading: false
};

const searchStart = (state, action) => {
  return updateObject(state, {
    error: null,
    loading: true
  });
};

const searchSuccess = (state, action) => {
  return updateObject(state, {
    response: action.response,
    error: null,
    loading: false
  });
};

const searchFailed = (state, action) => {
  return updateObject(state, {
    error: action.error,
    loading: false
  });
};

const searchReset = (state, action) => {
  return updateObject(state, {
    error: null,
    loading: false,
    response: action.response
  });
};

const reducer = (state = initialState, action) => {
  switch (action.type) {
    case actionTypes.SEARCH_START:
      return searchStart(state, action);
    case actionTypes.SEARCH_SUCCESS:
      return searchSuccess(state, action);
    case actionTypes.SEARCH_FAILED:
      return searchFailed(state, action);
    case actionTypes.SEARCH_RESET:
      return searchReset(state, action);
    default:
      return state;
  }
};

export default reducer;
