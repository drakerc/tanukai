import React from "react";
import {
  Button, Card,
  Form,
  Grid, Header, Segment
} from "semantic-ui-react";
import { connect } from "react-redux";
import { Redirect } from "react-router-dom";
import { imageSearch, resetProps } from "../store/actions/imagesearch";
import ImageUploader from 'react-images-upload';
import { getSettings } from "../store/actions/settings";
import { putPartitions } from "../store/actions/partitions";
import { putRating } from "../store/actions/rating";
import Checkbox from "semantic-ui-react/dist/commonjs/modules/Checkbox";
import { Input } from 'semantic-ui-react'

class ImageUpload extends React.Component {
  state = {
    images: null,
    partitions: [],
    partitionsSelected: [],
    maximumRating: null,
    privateImage: false,
    imageUrl: null,
  };

  componentDidMount() {
    this.props.getSettings();
  }

  componentDidUpdate(prevProps) {
    if (prevProps.settingsResponse !== this.props.settingsResponse) {
      let settingsResponse = this.props.settingsResponse;
      let apiPartitions = settingsResponse.data.partitions;
      let partitions = [];
      let partitionsSelected = [];

      Object.keys(apiPartitions).forEach(function (partitionName) {
        if (apiPartitions[partitionName].count === 0) {
          return;
        }
        let count = apiPartitions[partitionName].count.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
        partitions.push(
          {
            key: partitionName,
            text: `${partitionName.toUpperCase()} (${count} images)`,
            value: partitionName
          }
        );
        if (apiPartitions[partitionName].active) {
          partitionsSelected.push(partitionName);
        }
      });
      let maximumRating = settingsResponse.data.rating;
      this.setState({ partitionsSelected });
      this.setState({ partitions });
      this.setState({ maximumRating });
    }
  }

  handleSubmit = e => {
    e.preventDefault();
    const { images, imageUrl, partitionsSelected, maximumRating, privateImage } = this.state;
    this.props.imageSearch(images, imageUrl, partitionsSelected, maximumRating, privateImage);
  };


  onDrop = (pictures) => {
    this.setState({
      images: pictures.length ? pictures[0] : null,
    });
  };

  componentWillUnmount() {
    this.props.resetProps();
  }

  handleChange = (event, value) => {
    this.setState({ [value.name]: value.value });
    if (value.name === 'partitionsSelected') {
      let partitions = value.value.map((i) => (
        { 'partition': i }
      ));
      this.props.putPartitions(partitions);
    }
    if (value.name === 'maximumRating') {
      this.props.putRating({ 'rating': value.value });
    }
  };

  toggleCheckBox = (event, value) => {
    this.setState({ [value.name]: value.checked });
  };

  render() {
    let { images, maximumRating, imageUrl } = this.state;
    const { isAuthenticated, error, loading, response, settingsLoading, settingsError, settingsResponse } = this.props;
    if (images && response) {
      return <Redirect to={{
        pathname: '/search-results/' + response.data.uploaded_image.pk,
        state: { searchResults: response.data.similar_images, uploadedImage: response.data.uploaded_image }
      }}
      />
    }
    if (imageUrl && response) {
      return <Redirect to={{
        pathname: '/url-search-results/' + encodeURIComponent(imageUrl),
        state: { searchResults: response.data.similar_images, uploadedImage: response.data.uploaded_image }
      }}
      />
    }
    return (
      <Form size="large" onSubmit={this.handleSubmit}>
        <ImageUploader
          withIcon={true}
          withPreview={true}
          buttonText='Upload an image*'
          onChange={this.onDrop}
          name="images"
          imgExtension={['.jpg', '.gif', '.png', '.jpeg', '.webp']}
          maxFileSize={5242880}
          singleImage={true}
        />
        <Grid container stackable verticalAlign="middle">
          <Grid.Row>
              <Input
                name="imageUrl"
                onChange={this.handleChange}
                placeholder="...or enter an image URL"
              />
          </Grid.Row>
        </Grid>
        <Form>
          <Grid columns={isAuthenticated ? 3 : 2} doubling>
            <Grid.Column>
              <p className="form__text">Select websites to search*:</p>
              <Form.Dropdown
                placeholder='Select website(s)'
                onChange={this.handleChange}
                fluid
                multiple
                value={this.state.partitionsSelected}
                name="partitionsSelected"
                selection
                options={this.state.partitions} />
            </Grid.Column>
            <Grid.Column>
              <p className="form__text">Select maximum safety rating*:</p>
              <Form.Field>
                <Form.Radio
                  label='Safe'
                  name='maximumRating'
                  value='safe'
                  checked={maximumRating === 'safe'}
                  onChange={this.handleChange}
                />
              </Form.Field>
              <Form.Field>
                <Form.Radio
                  label='Questionable'
                  name='maximumRating'
                  value='questionable'
                  checked={maximumRating === 'questionable'}
                  onChange={this.handleChange}
                />
              </Form.Field>
              <Form.Field>
                <Form.Radio
                  label='Explicit'
                  name='maximumRating'
                  value='explicit'
                  checked={maximumRating === 'explicit'}
                  onChange={this.handleChange}
                />
              </Form.Field>
            </Grid.Column>
            {isAuthenticated && (
                <Grid.Column>
                  <p className="form__text">Private image*:</p>
                  <Checkbox
                      name="privateImage"
                      onChange={this.toggleCheckBox}
                      toggle
                  />
                </Grid.Column>
            )}
          </Grid>
        </Form>
        <div className="buttonContainer--search">
          <Button
            fluid
            size="large"
            loading={loading}
            disabled={images === null && imageUrl === null}>
            Start searching
          </Button>
        </div>
      </Form >
    );
  }
}

const mapStateToProps = state => {
  return {
    loading: state.imageSearch.loading,
    error: state.imageSearch.error,
    response: state.imageSearch.response,
    settingsLoading: state.getSettings.loading,
    settingsError: state.getSettings.error,
    settingsResponse: state.getSettings.response,
  };
};

const mapDispatchToProps = dispatch => {
  return {
    imageSearch: (images, imageUrl, partitions, maximumRating, privateImage) =>
      dispatch(imageSearch(images, imageUrl, partitions, maximumRating, privateImage)),
    resetProps: () =>
      dispatch(resetProps()),
    getSettings: () =>
      dispatch(getSettings()),
    putPartitions: (partitions) =>
      dispatch(putPartitions(partitions)),
    putRating: (rating) =>
      dispatch(putRating(rating)),
  };
};

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(ImageUpload);
