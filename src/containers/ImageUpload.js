import React from "react";
import {
    Button,
    Form,
    Grid,
    Header,
    Message,
    Segment
} from "semantic-ui-react";
import {connect} from "react-redux";
import {NavLink, Redirect} from "react-router-dom";
import {imageSearch, resetProps} from "../store/actions/imagesearch";
import ImageUploader from 'react-images-upload';
import {getSettings} from "../store/actions/settings";
import {putPartitions} from "../store/actions/partitions";
import {putRating} from "../store/actions/rating";


class ImageUpload extends React.Component {
    state = {
        images: null,
        partitions: [],
        partitionsSelected: [],
        maximumRating: null
    };

    componentDidMount() {
        this.props.getSettings();
    }

    componentDidUpdate(prevProps, prevState) {
        if (prevProps.settingsResponse !== this.props.settingsResponse) {
            console.log(this.state.partitionsSelected)
            let settingsResponse = this.props.settingsResponse;
            let apiPartitions = settingsResponse.data.partitions;
            let partitions = [];
            let partitionsSelected = [];

            Object.keys(apiPartitions).forEach(function (partitionName) {
                if (apiPartitions[partitionName].count === 0) {
                    return;
                }
                partitions.push(
                    {
                        key: partitionName,
                        text: partitionName + ' ' + apiPartitions[partitionName].count,
                        value: partitionName
                    }
                );
                if (apiPartitions[partitionName].active) {
                    partitionsSelected.push(partitionName);
                }
            });
            let maximumRating = settingsResponse.data.rating;
            this.setState({partitionsSelected});
            this.setState({partitions});
            this.setState({maximumRating});
        }
    }

    handleSubmit = e => {
        e.preventDefault();
        const {images, partitionsSelected, maximumRating} = this.state;
        this.props.imageSearch(images, partitionsSelected, maximumRating);
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
        this.setState({[value.name]: value.value});
        if (value.name === 'partitionsSelected') {
            let partitions = value.value.map((i) => (
                {'partition': i}
            ));
            this.props.putPartitions(partitions);
        }
        if (value.name === 'maximumRating') {
            this.props.putRating({'rating': value.value});
        }
    };

    render() {
        let {images, maximumRating} = this.state;
        const {error, loading, response, settingsLoading, settingsError, settingsResponse} = this.props;
        if (images && response) {
            return <Redirect to={{
                pathname: '/search-results/' + response.data.uploaded_image.pk,
                state: {searchResults: response.data.similar_images, uploadedImage: response.data.uploaded_image}
            }}
            />
        }
        return (
            <React.Fragment>
                <Form size="large" onSubmit={this.handleSubmit}>
                    <Segment stacked>
                        <ImageUploader
                            withIcon={true}
                            withPreview={true}
                            buttonText='Upload an image'
                            onChange={this.onDrop}
                            name="images"
                            imgExtension={['.jpg', '.gif', '.png']}
                            maxFileSize={5242880}
                            singleImage={true}
                        />
                        <Form.Dropdown
                            placeholder='Select website(s)'
                            onChange={this.handleChange}
                            fluid
                            multiple
                            value={this.state.partitionsSelected}
                            name="partitionsSelected"
                            selection
                            options={this.state.partitions}/>
                        <Form>
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
                        </Form>

                        <Button
                            color="teal"
                            fluid
                            size="large"
                            loading={loading}
                            disabled={images === null}>
                            Start searching
                        </Button>
                    </Segment>
                </Form>
            </React.Fragment>
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
        imageSearch: (images, partitions, maximumRating) =>
            dispatch(imageSearch(images, partitions, maximumRating)),
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
