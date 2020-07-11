import React from "react";
import {
    Button,
    Grid,
    Segment,
    Image,
    Responsive,
    Card,
    Icon,
    Modal,
    Pagination
} from "semantic-ui-react";
import {connect} from "react-redux";
import {uploadedSearch} from "../store/actions/uploadedSearch";
import {baseUrl} from "./helpers";

var qs = require('qs');


const getWidth = () => {
    const isSSR = typeof window === "undefined";
    return isSSR ? Responsive.onlyMobile.minWidth : window.innerWidth;
};

class SearchResults extends React.Component {
    state = {
        searchResults: null,
        activePage: 1,
        paginationFrom: 0,
        paginationSize: 10
    };

    componentDidMount() {
        const query = qs.parse(this.props.location.search, {
            ignoreQueryPrefix: true
        });
        if (query.pagination_from) {
            this.setState({activePage: (query.pagination_from / 10) + 1});
        }

        const imageId = this.props.match.params.imageId;
        const state = this.props.location.state;
        if (!state) {
            this.props.uploadedSearch(imageId, query.pagination_from, query.pagination_size);
        }
    }

    componentDidUpdate(prevProps, prevState) {
        const currentQuery = qs.parse(this.props.location.search, {
            ignoreQueryPrefix: true
        })
        const previousQuery = qs.parse(prevProps.location.search, {
            ignoreQueryPrefix: true
        })
        if (previousQuery.pagination_from !== currentQuery.pagination_from) {
            const imageId = this.props.match.params.imageId;
            this.props.uploadedSearch(imageId, currentQuery.pagination_from, currentQuery.pagination_size);
        }
    }

    handlePaginationChange = (e, {activePage}) => {
        this.setState({activePage});
        const paginationFrom = (activePage - 1) * this.state.paginationSize;
        this.props.history.push("/search-results/" + this.props.match.params.imageId + '?pagination_from=' + paginationFrom + '&pagination_size=' + this.state.paginationSize)
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
                <Pagination
                    activePage={this.state.activePage}
                    onPageChange={this.handlePaginationChange}
                    totalPages={5}
                />
                <Grid.Row>
                    <Image size="medium" src={baseUrl + uploadedImg.image}/>
                </Grid.Row>
                <Card.Group>
                    {imgs.imgs.map((i) => (
                            <Card>
                                <Modal size='large' trigger={
                                    <Image
                                        fluid
                                        key={i['id']}
                                        src={baseUrl + i.thumbnail_path}
                                    />
                                }>
                                    <Modal.Header>
                                        <Modal.Actions>
                                            <div className='ui two buttons'>
                                                <a href={i.data.source_url}>
                                                    <Button basic>
                                                        <Icon link name='linkify'/>
                                                        Go to source
                                                    </Button>
                                                </a>
                                                <Button basic onClick={() => this.clickImage(i['id'])}>
                                                    <Icon link name='search'/>
                                                    Find similar
                                                </Button>
                                            </div>
                                        </Modal.Actions>
                                    </Modal.Header>
                                    <Modal.Content image>
                                        <Image
                                            src={baseUrl + i.path}
                                            wrapped
                                        />
                                    </Modal.Content>
                                </Modal>
                                <Card.Content>
                                    <Card.Header>
                                        {i.distance}
                                    </Card.Header>
                                    <Card.Meta>{i.data.source_website}</Card.Meta>
                                    <Card.Description>
                                        {i.data.source_description}
                                    </Card.Description>
                                </Card.Content>
                                <Card.Content extra>
                                    <div className='ui two buttons'>
                                        <a href={i.data.source_url}>
                                            <Button basic>
                                                <Icon link name='linkify'/>
                                                Go to source
                                            </Button>
                                        </a>
                                        <Button basic onClick={() => this.clickImage(i['id'])}>
                                            <Icon link name='search'/>
                                            Find similar
                                        </Button>
                                    </div>
                                </Card.Content>
                            </Card>
                        )
                    )}
                </Card.Group>
                <Pagination
                    activePage={this.state.activePage}
                    onPageChange={this.handlePaginationChange}
                    totalPages={10}
                />
            </Grid>
        );
        return (
            <Responsive getWidth={getWidth} minWidth={Responsive.onlyMobile.minWidth}>
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
