export const baseApiUrl = process.env.REACT_APP_API_URL;

export const updateObject = (oldObject, updatedProperties) => {
  return {
    ...oldObject,
    ...updatedProperties
  };
};
