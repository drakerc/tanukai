import * as actionTypes from "../actions/actionTypes";
import { updateObject } from "../utility";

const initialState = {
  response: null,
  error: null,
  loading: false
};

const putRatingStart = (state, action) => {
  return updateObject(state, {
    error: null,
    loading: true
  });
};

const putRatingSuccess = (state, action) => {
  return updateObject(state, {
    response: action.response,
    error: null,
    loading: false
  });
};

const putRatingFailed = (state, action) => {
  return updateObject(state, {
    error: action.error,
    loading: false
  });
};


const reducer = (state = initialState, action) => {
  switch (action.type) {
    case actionTypes.PUT_RATING_START:
      return putRatingStart(state, action);
    case actionTypes.PUT_RATING_SUCCESS:
      return putRatingSuccess(state, action);
    case actionTypes.PUT_RATING_FAILED:
      return putRatingFailed(state, action);
    default:
      return state;
  }
};

export default reducer;
