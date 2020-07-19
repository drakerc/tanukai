import axios from "axios";

const token = localStorage.getItem("token");
if (token) {
  axios.defaults.headers.common['Authorization'] = 'Token ' + token;
}

export const axiosWithHeaders = axios;

export const baseApiUrl = process.env.REACT_APP_API_URL;

export const updateObject = (oldObject, updatedProperties) => {
  return {
    ...oldObject,
    ...updatedProperties
  };
};
