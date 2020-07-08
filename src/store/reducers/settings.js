import * as actionTypes from "../actions/actionTypes";
import { updateObject } from "../utility";

const initialState = {
  response: null,
  error: null,
  loading: false
};

const getSettingsStart = (state, action) => {
  return updateObject(state, {
    error: null,
    loading: true
  });
};

const getSettingsSuccess = (state, action) => {
  return updateObject(state, {
    response: action.response,
    error: null,
    loading: false
  });
};

const getSettingsFailed = (state, action) => {
  return updateObject(state, {
    error: action.error,
    loading: false
  });
};


const reducer = (state = initialState, action) => {
  switch (action.type) {
    case actionTypes.GET_SETTINGS_START:
      return getSettingsStart(state, action);
    case actionTypes.GET_SETTINGS_SUCCESS:
      return getSettingsSuccess(state, action);
    case actionTypes.GET_SETTINGS_FAILED:
      return getSettingsFailed(state, action);
    default:
      return state;
  }
};

export default reducer;
