import * as actionTypes from "../actions/actionTypes";
import { updateObject } from "../utility";

const initialState = {
  response: null,
  error: null,
  loading: false
};

const putPartitionsStart = (state, action) => {
  return updateObject(state, {
    error: null,
    loading: true
  });
};

const putPartitionsSuccess = (state, action) => {
  return updateObject(state, {
    response: action.response,
    error: null,
    loading: false
  });
};

const putPartitionsFailed = (state, action) => {
  return updateObject(state, {
    error: action.error,
    loading: false
  });
};


const reducer = (state = initialState, action) => {
  switch (action.type) {
    case actionTypes.PUT_PARTITIONS_START:
      return putPartitionsStart(state, action);
    case actionTypes.PUT_PARTITIONS_SUCCESS:
      return putPartitionsSuccess(state, action);
    case actionTypes.PUT_PARTITIONS_FAILED:
      return putPartitionsFailed(state, action);
    default:
      return state;
  }
};

export default reducer;
