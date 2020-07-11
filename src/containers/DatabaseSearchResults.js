import React from "react";
import {
    Button,
    Form,
    Grid,
    Header,
    Message,
    Segment,
    Image, Responsive, Pagination, Card, Modal, Icon
} from "semantic-ui-react";
import {connect} from "react-redux";
import {NavLink, Redirect} from "react-router-dom";
import {databaseSearch} from "../store/actions/databaseSearch";
import {baseUrl} from "./helpers";

var qs = require('qs');

const getWidth = () => {
    const isSSR = typeof window === "undefined";
    return isSSR ? Responsive.onlyTablet.minWidth : window.innerWidth;
};

class DatabaseSearchResults extends React.Component {
    state = {
        imageId: null,
        activePage: 1,
        paginationFrom: 0,
        paginationSize: 10,
        imgs: [],
        uploadedImg: [],
    };

    handleChange = e => {
        this.setState({[e.target.name]: e.target.value});
    };

    componentDidMount() {
        const query = qs.parse(this.props.location.search, {
            ignoreQueryPrefix: true
        });
        if (query.pagination_from) {
            this.setState({activePage: (query.pagination_from / 10) + 1});
        }
        const imageId = this.props.match.params.imageId;
        this.props.databaseSearch(imageId, query.pagination_from, query.pagination_to);
    }

    componentDidUpdate(prevProps) {
        const currentQuery = qs.parse(this.props.location.search, {
            ignoreQueryPrefix: true
        })
        const previousQuery = qs.parse(prevProps.location.search, {
            ignoreQueryPrefix: true
        })

        if (this.props.match.params.imageId !== prevProps.match.params.imageId || previousQuery.pagination_from !== currentQuery.pagination_from) {
            const imageId = this.props.match.params.imageId;
            this.setState({activePage: currentQuery.pagination_from ? (currentQuery.pagination_from / 10) + 1 : 1});
            this.props.databaseSearch(imageId, currentQuery.pagination_from, currentQuery.pagination_size);
        }
    }

    clickImage = value => {
        this.props.history.push("/database-image-search/" + value)
    };

    handlePaginationChange = (e, {activePage}) => {
        this.setState({activePage});
        const paginationFrom = (activePage - 1) * this.state.paginationSize;
        console.log(this.props.match.params.imageId)
        this.props.history.push("/database-image-search/" + this.props.match.params.imageId + '?pagination_from=' + paginationFrom + '&pagination_size=' + this.state.paginationSize)
    }

    render() {
        // TODO: this is basically the same thing as SearchResults.js, merge into 1 component instead
        const {error, loading, response} = this.props;
        const imgs = response ? response.data.similar_images : [];
        const uploadedImg = response ? response.data.uploaded_image : [];

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
                                        {i.distance}%
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

