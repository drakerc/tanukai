import React from "react";
import { connect } from "react-redux";
import { uploadedSearch } from "../store/actions/uploadedSearch";
import { databaseSearch } from "../store/actions/databaseSearch";
import { baseUrl } from "./helpers";

import {
  Button,
  Grid,
  Segment,
  Image,
  Responsive,
  Card,
  Icon,
  Modal,
  Pagination,
  Container,
  Label,
  Dimmer,
  Loader
} from "semantic-ui-react";

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
    paginationSize: 10,
    imgs: [],
    uploadedImg: []
  };

  componentDidMount() {
    const query = qs.parse(this.props.location.search, {
      ignoreQueryPrefix: true
    });
    if (query.pagination_from) {
      this.setState({ activePage: (query.pagination_from / 10) + 1 });
    }

    const imageId = this.props.match.params.imageId;
    const dbImageId = this.props.match.params.dbImageId;
    if (imageId) {
      this.props.uploadedSearch(imageId, query.pagination_from, query.pagination_size);
    }
    if (dbImageId) {
      this.props.databaseSearch(dbImageId, query.pagination_from, query.pagination_to);
    }
  }

  componentDidUpdate(prevProps) {
    const currentQuery = qs.parse(this.props.location.search, {
      ignoreQueryPrefix: true
    });
    const previousQuery = qs.parse(prevProps.location.search, {
      ignoreQueryPrefix: true
    });
    const imageId = this.props.match.params.imageId;
    const dbImageId = this.props.match.params.dbImageId;

    if (previousQuery.pagination_from !== currentQuery.pagination_from) {
      if (imageId) {
        this.props.uploadedSearch(imageId, currentQuery.pagination_from, currentQuery.pagination_size);
      }
      if (dbImageId) {
        this.props.databaseSearch(dbImageId, currentQuery.pagination_from, currentQuery.pagination_size);
      }
    }

    if (dbImageId && dbImageId !== prevProps.match.params.dbImageId) {
      const imageId = this.props.match.params.dbImageId;
      this.setState({activePage: currentQuery.pagination_from ? (currentQuery.pagination_from / 10) + 1 : 1});
      this.props.databaseSearch(imageId, currentQuery.pagination_from, currentQuery.pagination_size);
    }
  }

  handleChange = e => {
    this.setState({ [e.target.name]: e.target.value });
  };

  handlePaginationChange = (e, { activePage }) => {
    this.setState({ activePage });
    const paginationFrom = (activePage - 1) * this.state.paginationSize;

    const imageId = this.props.match.params.imageId;
    const dbImageId = this.props.match.params.dbImageId;

    if (imageId) {
      this.props.history.push("/search-results/" + this.props.match.params.imageId + '?pagination_from=' + paginationFrom + '&pagination_size=' + this.state.paginationSize);
    }
    if (dbImageId) {
      this.props.history.push("/database-image-search/" + this.props.match.params.dbImageId + '?pagination_from=' + paginationFrom + '&pagination_size=' + this.state.paginationSize);
    }
  };

  clickImage = value => {
    this.props.history.push("/database-image-search/" + value);
  };

  render() {
    const { error, loading, response, errorDb, loadingDb, responseDb } = this.props;

    let imgs = this.props.location.state ? this.props.location.state.searchResults : null;
    let uploadedImg = this.props.location.state ? this.props.location.state.uploadedImage : null;

    const imageId = this.props.match.params.imageId;
    const dbImageId = this.props.match.params.dbImageId;

    if (!imgs) {
      if (imageId) {
        imgs = response ? response.data.similar_images : [];
        uploadedImg = response ? response.data.uploaded_image : [];
      }
      if (dbImageId) {
        imgs = responseDb ? responseDb.data.similar_images : [];
        uploadedImg = responseDb ? responseDb.data.uploaded_image : [];
        if (uploadedImg && uploadedImg.image) {
          uploadedImg.image = uploadedImg.image.substr(7); // dirty hack till I have a separate model
        }
      }
    }

    const ImagesList = (imgs) => (
      <Container>
        {loading || loadingDb ? (
          <div className="loadingContainer">
            <Dimmer active inverted>
              <Loader size='massive' inverted content='Loading' />
            </Dimmer>
          </div>
        ) : (
            <Grid columns="3" centered>
              <Grid.Column className="mainImageColumn">
                {/* // TODO: change in the backend? */}
                <p className="mainImageText">Uploaded image: </p>
                <Image size="small" src={baseUrl + uploadedImg.image} className="mainImage" />
              </Grid.Column>
              <Grid.Row>
                <Pagination
                  activePage={this.state.activePage}
                  onPageChange={this.handlePaginationChange}
                  totalPages={this.state.paginationSize}
                  secondary
                />
              </Grid.Row>
              <Card.Group>
                {imgs.imgs.map((i) => (
                  <Card size="medium">
                    <Modal size='large' trigger={
                      i['id'] && baseUrl + i.thumbnail_path ? (
                        <Image
                          key={i['id']}
                          src={baseUrl + i.thumbnail_path}
                        />
                      ) : (
                          <Image size='small'>
                            <Label content='Image not found!' icon='warning' />
                          </Image>
                        )
                    }>
                      <Modal.Header>
                        <Modal.Actions>
                          <div className='ui two buttons'>
                            {i.data.source_url && (
                              <a href={i.data.source_url}>
                                <Button basic>
                                  <Icon link name='linkify' />
                            Go to source
                          </Button>
                              </a>
                            )}
                            {i['id'] && (
                              <Button basic onClick={() => this.clickImage(i['id'])}>
                                <Icon link name='search' />
                          Find similar
                              </Button>
                            )}
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
                      {i.distance && (
                        <Card.Header>
                          {i.distance}%
                        </Card.Header>
                      )}
                      {i.data.source_website && (
                        <Card.Meta>{i.data.source_website}</Card.Meta>
                      )}
                      {i.data.source_description && (
                        <Card.Description>
                          {i.data.source_description.substring(0, 300)}
                        </Card.Description>
                      )}
                    </Card.Content>
                    <Card.Content extra>
                      <div className='ui two buttons'>
                        {i.data.source_url && (
                          <a href={i.data.source_url}>
                            <Button basic>
                              <Icon link name='linkify' />
                      Go to source
                    </Button>
                          </a>
                        )}
                        {i['id'] && (
                          <Button basic onClick={() => this.clickImage(i['id'])}>
                            <Icon link name='search' />
                      Find similar
                          </Button>
                        )}
                      </div>
                    </Card.Content>
                  </Card>
                )
                )}
              </Card.Group>
              <Pagination
                activePage={this.state.activePage}
                onPageChange={this.handlePaginationChange}
                totalPages={this.state.paginationSize}
                secondary
              />
            </Grid>
          )}
      </Container>
    );
    return (
      <Responsive getWidth={getWidth} minWidth={Responsive.onlyMobile.minWidth}>
        <Segment>
          <div className="imagesListContainer">
            <ImagesList imgs={imgs}></ImagesList>
          </div>
        </Segment>
      </Responsive>
    );
  }
}

const mapStateToProps = state => {
  return {
    loading: state.uploadedSearch.loading,
    error: state.uploadedSearch.error,
    response: state.uploadedSearch.response,
    loadingDb: state.databaseSearch.loading,
    errorDb: state.databaseSearch.error,
    responseDb: state.databaseSearch.response
  };
};

const mapDispatchToProps = dispatch => {
  return {
    uploadedSearch: (imageId, paginationFrom, paginationSize) => dispatch(uploadedSearch(imageId, paginationFrom, paginationSize)),
    databaseSearch: (dbImageId, paginationFrom, paginationSize) => dispatch(databaseSearch(dbImageId, paginationFrom, paginationSize))
  };
};

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(SearchResults);
