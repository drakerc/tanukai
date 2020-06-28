import * as actionTypes from "../actions/actionTypes";
import { updateObject } from "../utility";

const initialState = {
  response: null,
  error: null,
  loading: false
};

const uploadedSearchStart = (state, action) => {
  return updateObject(state, {
    error: null,
    loading: true
  });
};

const uploadedSearchSuccess = (state, action) => {
  return updateObject(state, {
    response: action.response,
    error: null,
    loading: false
  });
};

const uploadedSearchFailed = (state, action) => {
  return updateObject(state, {
    error: action.error,
    loading: false
  });
};

const reducer = (state = initialState, action) => {
  switch (action.type) {
    case actionTypes.UPLOADED_SEARCH_START:
      return uploadedSearchStart(state, action);
    case actionTypes.UPLOADED_SEARCH_SUCCESS:
      return uploadedSearchSuccess(state, action);
    case actionTypes.UPLOADED_SEARCH_FAILED:
      return uploadedSearchFailed(state, action);
    default:
      return state;
  }
};

export default reducer;
