import React, { useState } from "react";
import { useHistory } from "react-router";
import "./writePost.css";

import Box from "@material-ui/core/Box";
import Button from "@material-ui/core/Button";
import { makeStyles } from "@material-ui/core/styles";
import TextField from "@material-ui/core/TextField";

// The base path for ReadMoa APIs.
const API_SERVER_PATH = "http://127.0.0.1:8080/api/";
// const API_SERVER_PATH = "/api/";

const useStyles = makeStyles((theme) => ({
  root: {
    "& > *": {
      margin: theme.spacing(1),
      width: "36ch",
    },
  },
}));

function WritePost() {
  const classes = useStyles();
  const history = useHistory();

  const onSubmit = (e) => {
    fetch(API_SERVER_PATH + "add_post", {
      method: "POST",
      mode: "cors",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ url: url, comment: comment, idtoken: idtoken }),
    })
      .then((response) => {
        history.push("/");
      })
      .catch((err) => {
        console.log(err);
      });

    console.log(`URL: ${url}, Comment: ${comment}`);
    e.preventDefault();
  };

  const [url, setUrl] = useState("");
  const [comment, setComment] = useState("");
  const [idtoken, setIdtoken] = useState("");

  return (
    <div className="App" onSubmit={onSubmit}>
      <form className={classes.root} noValidate autoComplete="off">
        <div width="100%">
          <TextField
            id="outlined-basic"
            label="URL"
            variant="outlined"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            fullWidth
          />
        </div>
        <div width="100%">
          <TextField
            id="outlined-basic"
            label="Comment"
            variant="outlined"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            fullWidth
          />
        </div>
        <div width="100%">
          <Button variant="contained" type="submit">
            Submit
          </Button>
        </div>
      </form>
    </div>
  );
}

export default WritePost;
