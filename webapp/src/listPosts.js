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
import Typography from "@material-ui/core/Typography";

// The base path for ReadMoa APIs.
const API_SERVER_PATH = "http://127.0.0.1:8080/api/";
// const API_SERVER_PATH = "/api/";

const useStyles = makeStyles({
  root: {
    maxWidth: "100%",
  },
});

function ImgMediaCard(props) {
  const classes = useStyles();

  return (
    <Card>
      <CardActionArea className={classes.root}>
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

function ListPosts() {
  const [posts, setPosts] = useState([]);
  const [error, setError] = useState(null);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    fetch(API_SERVER_PATH + "list_posts", {
      method: "GET",
    })
      .then((response) => response.json())
      .then(
        (response) => {
          //console.log(response.posts);
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

  if (error) {
    return <div>Error: {error.message}</div>;
  } else if (!isLoaded) {
    return <div>Loading...</div>;
  } else {
    console.log(posts);
    return (
      <Box width="100%" justifyContent="center">
        <ImgMediaCard
          title={posts[0].title}
          description={posts[0].description}
          imageUrl={posts[0].main_image_url}
          postUrl={posts[0].post_url}
        />
        <ImgMediaCard
          title={posts[1].title}
          description={posts[1].description}
          imageUrl={posts[1].main_image_url}
          postUrl={posts[1].post_url}
        />
        <ImgMediaCard
          title={posts[2].title}
          description={posts[2].description}
          imageUrl={posts[2].main_image_url}
          postUrl={posts[2].post_url}
        />
        <ImgMediaCard
          title={posts[3].title}
          description={posts[3].description}
          imageUrl={posts[3].main_image_url}
          postUrl={posts[3].post_url}
        />
        <ImgMediaCard
          title={posts[4].title}
          description={posts[4].description}
          imageUrl={posts[4].main_image_url}
          postUrl={posts[4].post_url}
        />{" "}
        <ImgMediaCard
          title={posts[5].title}
          description={posts[5].description}
          imageUrl={posts[5].main_image_url}
          postUrl={posts[5].post_url}
        />
      </Box>
    );
  }
}

export default ListPosts;
