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
import {databaseSearch} from "../store/actions/databaseSearch";

const getWidth = () => {
    const isSSR = typeof window === "undefined";
    return isSSR ? Responsive.onlyTablet.minWidth : window.innerWidth;
};

class DatabaseSearchResults extends React.Component {
    state = {
        responseFetched: false,
        imageId: null,
        paginationFrom: null,
        paginationSize: null,
        imgs: [],
        uploadedImg: [],
    };

    handleChange = e => {
        this.setState({[e.target.name]: e.target.value});
    };

    componentDidMount() {
        const imageId = this.props.match.params.imageId;
        this.props.databaseSearch(imageId, 0, 10);
    }

    componentDidUpdate(prevProps) {
        if (this.props.match.params.imageId !== prevProps.match.params.imageId) {
            const imageId = this.props.match.params.imageId;
            this.props.databaseSearch(imageId, 0, 10);
            this.setState({responseFetched: false});
        }
    }

    clickImage = value => {
        this.props.history.push("/database-image-search/" + value)
    };

    render() {
        const {error, loading, response} = this.props;
        const imgs = response ? response.data.similar_images : [];
        const uploadedImg = response ? response.data.uploaded_image : [];

        const ImagesList = (imgs) => (
            <Grid container columns="equal">
                <Grid.Row>
                    <Image size="medium" src={'http://localhost/' + uploadedImg.image}/>
                </Grid.Row>
                {imgs.imgs.map((i) => (
                        <Grid.Column width={2} key={i['id']}>
                            <Image
                                size="large"
                                src={'http://localhost/' + i.thumbnail_path}
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
        loading: state.databaseSearch.loading,
        error: state.databaseSearch.error,
        response: state.databaseSearch.response
    };
};

const mapDispatchToProps = dispatch => {
    return {
        databaseSearch: (imageId, paginationFrom, paginationSize) => dispatch(databaseSearch(imageId, paginationFrom, paginationSize))
    };
};

export default connect(
    mapStateToProps,
    mapDispatchToProps
)(DatabaseSearchResults);

