import React from "react";
import {
    Button,
    Form,
    Grid,
    Header,
    Message,
    Segment,
    Image, Responsive
} from "semantic-ui-react";
import {connect} from "react-redux";
import {NavLink, Redirect} from "react-router-dom";
import {authLogin} from "../store/actions/auth";
import {useHistory} from "react-router-dom";
import {uploadedSearch} from "../store/actions/uploadedSearch";
import {baseUrl} from "./helpers";


const getWidth = () => {
    const isSSR = typeof window === "undefined";
    return isSSR ? Responsive.onlyTablet.minWidth : window.innerWidth;
};

class SearchResults extends React.Component {
    state = {
        searchResults: null,
    };

    componentDidMount() {
        const imageId = this.props.match.params.imageId;
        const state = this.props.location.state;
        if (!state) {
            this.props.uploadedSearch(imageId, 0, 10);
        }
    }

    clickImage = value => {
        this.props.history.push("/database-image-search/" + value)
    };

    render() {
        const {error, loading, response} = this.props;
        let imgs = this.props.location.state ? this.props.location.state.searchResults : null;
        let uploadedImg = this.props.location.state ? this.props.location.state.uploadedImage : null;
        if (!imgs) {
            imgs = response ? response.data.similar_images : [];
            uploadedImg = response ? response.data.uploaded_image : [];
        }

        const ImagesList = (imgs) => (
            <Grid container columns="equal">
                <Grid.Row>
                    <Image size="medium" src={baseUrl + uploadedImg.image}/>
                </Grid.Row>
                {imgs.imgs.map((i) => (
                        <Grid.Column width={2} key={i['id']}>
                            <Image
                                size="large"
                                key={i['id']}
                                src={baseUrl + i.thumbnail_path}
                                onClick={() => this.clickImage(i['id'])}
                            />
                            {i.distance}
                        </Grid.Column>
                    )
                )}
            </Grid>
        );
        return (
            <Responsive getWidth={getWidth} minWidth={Responsive.onlyTablet.minWidth}>
                <Segment style={{padding: "8em 0em"}} vertical>
                    <ImagesList imgs={imgs}></ImagesList>
                </Segment>
            </Responsive>
        );
    }
}

const mapStateToProps = state => {
    return {
        loading: state.uploadedSearch.loading,
        error: state.uploadedSearch.error,
        response: state.uploadedSearch.response
    };
};

const mapDispatchToProps = dispatch => {
    return {
        uploadedSearch: (imageId, paginationFrom, paginationSize) => dispatch(uploadedSearch(imageId, paginationFrom, paginationSize))
    };
};

export default connect(
    mapStateToProps,
    mapDispatchToProps
)(SearchResults);
