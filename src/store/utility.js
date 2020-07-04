export const baseApiUrl = 'http://127.0.0.1:8000/';

export const updateObject = (oldObject, updatedProperties) => {
  return {
    ...oldObject,
    ...updatedProperties
  };
};
