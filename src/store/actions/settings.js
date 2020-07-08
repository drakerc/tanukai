import axios from "axios";
import {baseApiUrl} from "../utility"
import * as actionTypes from "./actionTypes";

export const getSettingsStart = () => {
    return {
        type: actionTypes.GET_SETTINGS_START
    };
};

export const getSettingsSuccess = response => {
    return {
        type: actionTypes.GET_SETTINGS_SUCCESS,
        response: response
    };
};

export const getSettingsFailed = error => {
    return {
        type: actionTypes.GET_SETTINGS_FAILED,
        error: error
    };
};

export const getSettings = () => {
    return dispatch => {
        dispatch(getSettingsStart());
        const token = localStorage.getItem("token");
        const headers = token ? {'Authorization': 'Token ' + token} : null;
        axios
            .get(baseApiUrl + "api/v1/settings", {'headers': headers})
            .then(res => {
                dispatch(getSettingsSuccess(res));
            })
            .catch(err => {
                dispatch(getSettingsFailed(err));
            });
    };
};
