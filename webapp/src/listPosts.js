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

import * as Constants from "./constants.js";

const useStyles = makeStyles({
  root: {
    maxWidth: "380px",
  },
  box: {
    margin: "2px",
  },
});

function ImgMediaCard(props) {
  const classes = useStyles();

  return (
    <Card className={classes.box}>
      <CardActionArea className={classes.root} href={props.postUrl}>
        <CardMedia
          component="img"
          alt={props.title}
          height="200"
          image={props.imageUrl}
          title={props.title}
        />
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
        <Button size="small" color="primary">
          Learn More
        </Button>
        <Button size="small" color="primary" href={props.postUrl}>
          Read
        </Button>
      </CardActions>
    </Card>
  );
}

const ListPosts = () => {
  const [posts, setPosts] = useState(Array.from({ length: 0 }));
  const [error, setError] = useState(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const style = useStyles();

  useEffect(() => {
    fetch(Constants.API_SERVER_PATH + "list_posts", {
      method: "GET",
    })
      .then((response) => response.json())
      .then(
        (response) => {
          setPosts(response.posts);
          setIsLoaded(true);
        },
        (error) => {
          setIsLoaded(true);
          setError(error);
        }
      )
      .catch((err) => {
        console.log(err);
      });
  }, []);

  const fetchMoreData = () => {
    const url =
      Constants.API_SERVER_PATH +
      "list_posts?start=" +
      posts.length +
      "&count=10";

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
        (error) => {
          setIsLoaded(true);
          setError(error);
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
            />
          </div>
        ))}
      </InfiniteScroll>
    </Box>
  );
};

export default ListPosts;
