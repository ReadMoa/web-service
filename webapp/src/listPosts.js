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

  const items = [];
  if (error) {
    return <div>Error: {error.message}</div>;
  } else if (!isLoaded) {
    return <div>Loading...</div>;
  } else {
    for (const [, value] of posts.slice(0, 50).entries()) {
      items.push(
        <ImgMediaCard
          title={value.title}
          description={value.description}
          imageUrl={value.main_image_url}
          postUrl={value.post_url}
        />
      );
    }

    return <Box width="380px">{items}</Box>;
  }
}

export default ListPosts;
