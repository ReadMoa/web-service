// @flow

import React from "react";
import ReactDOM from "react-dom";
import { BrowserRouter as Router, Switch, Route, Link } from "react-router-dom";
import "./index.css";
import * as serviceWorker from "./serviceWorker";
import ListPosts from "./listPosts";
import WritePost from "./writePost";

function MainApp() {
  return (
    <Router>
      <div>
        <nav>
          <ul>
            <li>
              <Link to="/">Home</Link>
            </li>
            <li>
              <Link to="/write_post">Write post</Link>
            </li>
          </ul>
        </nav>

        <Switch>
          <Route path="/write_post">
            <WritePost />
          </Route>
          <Route path="/">
            <ListPosts />
          </Route>
        </Switch>
      </div>
    </Router>
  );
}

ReactDOM.render(<MainApp />, document.getElementById("root"));

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();
