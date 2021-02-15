// @flow
import React, { useEffect, useState } from "react";
import "./listPosts.css";

import Box from "@material-ui/core/Box";
import Button from "@material-ui/core/Button";
import { makeStyles } from "@material-ui/core/styles";
import Card from "@material-ui/core/Card";
import CardActionArea from "@material-ui/core/CardActionArea";
import CardActions from "@material-ui/core/CardActions";
import CardContent from "@material-ui/core/CardContent";
import CardMedia from "@material-ui/core/CardMedia";
import InfiniteScroll from "react-infinite-scroll-component";
import Typography from "@material-ui/core/Typography";

import { getApiServerPath } from "./constants.js";
import InstantPostView from "./instantViewPost.js";

const useStyles = makeStyles({
  root: {
    maxWidth: "380px",
  },
  box: {
    margin: "2px",
  },
});

function ImgMediaCardMediaSection(props) {
  if (props.imageUrl !== "") {
    return (
      <CardMedia
        component="img"
        alt={props.title}
        height="200"
        image={props.imageUrl}
        title={props.title}
      />
    );
  }
  return null;
}

function ImgMediaCard(props) {
  const classes = useStyles();

  function handleClick(event) {
    // Open InstantViewPost dialog when an item in the list was clicked.
    props.handleOpenModalView();
    // These two handlers will set the states in the parent component to pass
    // the URL and page_view URL to the InstantViewPost component.
    props.handleSelectPost(props.postUrl);
    props.handleViewPageUrl(props.viewPageUrl);
  }

  return (
    <Card className={classes.box}>
      <CardActionArea className={classes.root} href={props.viewPageUrl}>
        <ImgMediaCardMediaSection imageUrl={props.imageUrl} />
        <CardContent>
          <Typography gutterBottom variant="h5" component="h2">
            {props.title}
          </Typography>
          <Typography variant="body2" color="textSecondary" component="p">
            {props.description}
          </Typography>
        </CardContent>
      </CardActionArea>
      <CardActions>
        <Button
          size="small"
          color="primary"
          aria-label="작가 {props.author}"
          href={props.listPostsByAuthorUrl}
        >
          {props.author}
        </Button>
        <Button
          size="small"
          color="primary"
          onClick={handleClick}
          aria-label="포스트 살짝 보기"
        >
          살짝 보기
        </Button>
      </CardActions>
    </Card>
  );
}

const ListPosts = (props) => {
  const [posts, setPosts] = useState(Array.from({ length: 0 }));
  const [, setError] = useState(null);
  const [, setIsLoaded] = useState(false);
  const style = useStyles();

  // 'open' state indicates (or triggers) to open the InstantViewPost modal
  // dialog.
  const [open, setOpen] = React.useState(false);
  // These two states are for ImgMediaCard to pass the post URL and the page
  // view URL to the InstantViewPost component.
  const [selectedPost, setSelectedPost] = useState("");
  const [viewPageUrl, setViewPageUrl] = useState("");

  const handleOpenModalView = () => {
    setOpen(true);
  };

  const handleCloseModalView = () => {
    setOpen(false);
  };

  useEffect(() => {
    fetch(getApiServerPath() + "list_posts", {
      method: "GET",
    })
      .then((response) => response.json())
      .then(
        (response) => {
          setPosts(response.posts);
          setIsLoaded(true);
        },
        (err) => {
          setIsLoaded(true);
          setError(err);
        }
      )
      .catch((err) => {
        console.log(err);
      });
  }, []);

  const fetchMoreData = () => {
    const url =
      getApiServerPath() + "list_posts?start=" + posts.length + "&count=10";

    fetch(url, {
      method: "GET",
    })
      .then((response) => response.json())
      .then(
        (response) => {
          console.log(response.posts);
          setPosts((posts) => posts.concat(response.posts));
          setIsLoaded(true);
        },
        (err) => {
          setIsLoaded(true);
          setError(err);
        }
      )
      .catch((err) => {
        console.log(err);
      });
  };

  return (
    <Box width="380px">
      <InfiniteScroll
        dataLength={posts.length}
        next={fetchMoreData}
        hasMore={true}
        loader={<h4>Loading...</h4>}
      >
        {posts.map((post, index) => (
          <div style={style} key={index.toString()}>
            <ImgMediaCard
              key={index.toString()}
              title={post.title}
              description={post.description}
              imageUrl={post.main_image_url}
              postUrl={post.post_url}
              viewPageUrl={"/p/" + post.post_url_hash}
              listPostsByAuthorUrl={"/a/" + post.author_key}
              author={post.author}
              handleOpenModalView={handleOpenModalView}
              handleSelectPost={setSelectedPost}
              handleViewPageUrl={setViewPageUrl}
            />
          </div>
        ))}
      </InfiniteScroll>

      <InstantPostView
        postUrl={selectedPost}
        viewPageUrl={viewPageUrl}
        openModalView={open}
        handleCloseModalView={handleCloseModalView}
      />
    </Box>
  );
};

export default ListPosts;
