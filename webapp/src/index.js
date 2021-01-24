// @flow

import React from "react";
import ReactDOM from "react-dom";
import AppBar from "@material-ui/core/AppBar";
import Box from "@material-ui/core/Box";
import Button from "@material-ui/core/Button";
import { BrowserRouter as Router, Switch, Route } from "react-router-dom";
import IconButton from "@material-ui/core/IconButton";
import * as serviceWorker from "./serviceWorker";
import MenuIcon from "@material-ui/icons/Menu";
import { makeStyles } from "@material-ui/core/styles";
import Toolbar from "@material-ui/core/Toolbar";
import Typography from "@material-ui/core/Typography";

// Custom resources.
import "./index.css";
import ListPosts from "./listPosts";
import WritePost from "./writePost";
import ViewPost from "./viewPost";

const useStyles = makeStyles((theme) => ({
  root: {
    flexGrow: 1,
  },
  menuButton: {
    marginRight: theme.spacing(1),
  },
  title: {
    flexGrow: 1,
  },
}));

function MainApp() {
  const classes = useStyles();

  const el = document.getElementById("root");

  return (
    <Router>
      <div style={{ width: "100%" }}>
        <AppBar position="static">
          <Toolbar variant="dense">
            <IconButton
              edge="start"
              className={classes.menuButton}
              color="inherit"
              aria-label="menu"
            >
              <MenuIcon />
            </IconButton>
            <Box justifyContent="left" style={{ width: "60%" }}>
              <Button href="/">ReadMoa</Button>
            </Box>
            <Box justifyContent="right" style={{ width: "40%" }}>
              <Button href="/" color="inherit">
                홈
              </Button>
              <Button href="/write_post" color="inherit">
                글추가
              </Button>
            </Box>
          </Toolbar>
        </AppBar>

        <Box display="flex" justifyContent="center">
          <Switch>
            <Route path="/p/:post_url_key">
              <ViewPost message={el.getAttribute("data-param")} />
            </Route>
            <Route path="/write_post">
              <WritePost />
            </Route>
            <Route path="/">
              <ListPosts />
            </Route>
          </Switch>
        </Box>
      </div>
    </Router>
  );
}

ReactDOM.render(<MainApp />, document.getElementById("root"));

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();
