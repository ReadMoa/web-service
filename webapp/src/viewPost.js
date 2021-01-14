// @flow
import React from "react";
import "./viewPost.css";

import Box from "@material-ui/core/Box";

function IFrameContainer(props) {
  return (
    <div class="iframe-container">
      <iframe src={props.message}></iframe>
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
