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
import {Slider} from "react-semantic-ui-range";


class ImageUpload extends React.Component {
    state = {
        images: null,
        partitions: ['danbooru', 'e621'],
        maximumRating: 'explicit'
    };

    handleSubmit = e => {
        e.preventDefault();
        const {images, partitions, maximumRating} = this.state;
        this.props.imageSearch(images, partitions, maximumRating);
    };


    onDrop = (pictures) => {
        console.log(pictures)
        this.setState({
            images: pictures.length ? pictures[0] : null,
        });
    }

    componentWillUnmount() {
        this.props.resetProps();
    }

    handleChange = (event, value) => {
        this.setState({[value.name]: value.value});
    };

    render() {
        let {images, partitions} = this.state;
        const {error, loading, response} = this.props;
        if (images && response) {
            return <Redirect to={{
                pathname: '/search-results/' + response.data.uploaded_image.pk,
                state: {searchResults: response.data.similar_images, uploadedImage: response.data.uploaded_image}
            }}
            />
        }
        const options = [
            {key: 'e621', text: 'E621', value: 'e621'},
            {key: 'danbooru', text: 'danbooru', value: 'danbooru'},
        ];
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
                            value={partitions}
                            name="partitions"
                            selection
                            options={options}/>
                        <Form>
                            <Form.Field>
                                <Form.Radio
                                    label='Safe'
                                    name='maximumRating'
                                    value='safe'
                                    checked={this.state.maximumRating === 'safe'}
                                    onChange={this.handleChange}
                                />
                            </Form.Field>
                            <Form.Field>
                                <Form.Radio
                                    label='Questionable'
                                    name='maximumRating'
                                    value='questionable'
                                    checked={this.state.maximumRating === 'questionable'}
                                    onChange={this.handleChange}
                                />
                            </Form.Field>
                            <Form.Field>
                                <Form.Radio
                                    label='Explicit'
                                    name='maximumRating'
                                    value='explicit'
                                    checked={this.state.maximumRating === 'explicit'}
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
        response: state.imageSearch.response
    };
};

const mapDispatchToProps = dispatch => {
    return {
        imageSearch: (images, partitions, maximumRating) =>
            dispatch(imageSearch(images, partitions, maximumRating)),
        resetProps: () =>
            dispatch(resetProps())
    };
};

export default connect(
    mapStateToProps,
    mapDispatchToProps
)(ImageUpload);
