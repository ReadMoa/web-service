// @flow
import React from "react";
import "./viewPost.css";

import Box from "@material-ui/core/Box";

function IFrameContainer(props) {
  return (
    <div className="iframe-container">
      <iframe src={props.message} title="View Post Frame"></iframe>
    </div>
  );
}

const ViewPost = (props) => {
  return (
    <Box width="100%">
      <IFrameContainer message={props.message} />
    </Box>
  );
};

export default ViewPost;
