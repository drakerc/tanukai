import * as actionTypes from "../actions/actionTypes";
import { updateObject } from "../utility";

const initialState = {
  response: null,
  error: null,
  loading: false
};

const databaseSearchStart = (state, action) => {
  return updateObject(state, {
    error: null,
    loading: true
  });
};

const databaseSearchSuccess = (state, action) => {
  return updateObject(state, {
    response: action.response,
    error: null,
    loading: false
  });
};

const databaseSearchFailed = (state, action) => {
  return updateObject(state, {
    error: action.error,
    loading: false
  });
};

const reducer = (state = initialState, action) => {
  switch (action.type) {
    case actionTypes.DATABASE_SEARCH_START:
      return databaseSearchStart(state, action);
    case actionTypes.DATABASE_SEARCH_SUCCESS:
      return databaseSearchSuccess(state, action);
    case actionTypes.DATABASE_SEARCH_FAILED:
      return databaseSearchFailed(state, action);
    default:
      return state;
  }
};

export default reducer;
