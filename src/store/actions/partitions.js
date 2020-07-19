import { baseApiUrl, axiosWithHeaders } from "../utility"
import * as actionTypes from "./actionTypes";

export const putPartitionsStart = () => {
  return {
    type: actionTypes.PUT_PARTITIONS_START
  };
};

export const putPartitionsSuccess = response => {
  return {
    type: actionTypes.PUT_PARTITIONS_SUCCESS,
    response: response
  };
};

export const putPartitionsFailed = error => {
  return {
    type: actionTypes.PUT_PARTITIONS_FAILED,
    error: error
  };
};

export const putPartitions = (partitions) => {
  localStorage.setItem("partitions", partitions);
  return dispatch => {
    dispatch(putPartitionsStart());
    const token = localStorage.getItem("token");
    if (!token) {
      dispatch(putPartitionsFailed());
      return;
    }
    axiosWithHeaders
      .put(baseApiUrl + "api/v1/partitions", partitions)
      .then(res => {
        dispatch(putPartitionsSuccess(res));
      })
      .catch(err => {
        dispatch(putPartitionsFailed(err));
      });
  };
};
