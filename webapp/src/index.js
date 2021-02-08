// @flow
import React from "react";
import ReactDOM from "react-dom";
import AppBar from "@material-ui/core/AppBar";
import BookIcon from "@material-ui/icons/Book";
import Box from "@material-ui/core/Box";
import Button from "@material-ui/core/Button";
import { BrowserRouter as Router, Switch, Route } from "react-router-dom";
import CodeIcon from "@material-ui/icons/Code";
import Divider from "@material-ui/core/Divider";
import IconButton from "@material-ui/core/IconButton";
import Menu from "@material-ui/core/Menu";
import MenuItem from "@material-ui/core/MenuItem";
import MenuIcon from "@material-ui/icons/Menu";
import { makeStyles } from "@material-ui/core/styles";
import Toolbar from "@material-ui/core/Toolbar";
import { Typography } from "@material-ui/core";
import * as serviceWorker from "./serviceWorker";

// Custom resources.
import "./index.css";
import ListPosts from "./listPosts";
import ListPostsByAuthor from "./listPostsByAuthor";
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
  menuItem: {
    width: "100%",
    maxWidth: 360,
    // TODO: choose the right color (palette.background.paper).
    backgroundColor: theme.palette.action.disabledBackground,
    color: theme.palette.text.secondary,
  },
}));

function MainApp() {
  const classes = useStyles();

  const root_elem = document.getElementById("root");
  const [anchorEl, setAnchorEl] = React.useState(null);

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

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
              onClick={handleClick}
            >
              <MenuIcon />
            </IconButton>

            <Menu
              id="simple-menu"
              anchorEl={anchorEl}
              keepMounted
              open={Boolean(anchorEl)}
              onClose={handleClose}
            >
              <MenuItem button component="a" href="https://readmoa.github.io/">
                <BookIcon /> 블로그
              </MenuItem>
              <Divider />
              <MenuItem
                button
                component="a"
                href="https://www.github.com/ReadMoa/web-service"
              >
                <CodeIcon />
                소스 코드
              </MenuItem>
            </Menu>

            <Box
              display="flex"
              justifyContent="flex-start"
              style={{ width: "50%" }}
            >
              <Button href="/">ReadMoa</Button>
              <Typography variant="body2" color="textSecondary" component="p">
                <i>beta</i>
              </Typography>
            </Box>
            <Box
              display="flex"
              justifyContent="flex-end"
              style={{ width: "40%" }}
            >
              <Button href="/write_post" color="inherit">
                글추가
              </Button>
            </Box>
          </Toolbar>
        </AppBar>

        <Box display="flex" justifyContent="center">
          <Switch>
            <Route path="/p/:post_url_key">
              <ViewPost message={root_elem.getAttribute("data-param")} />
            </Route>
            <Route path="/a/:author_key">
              <ListPostsByAuthor />
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
