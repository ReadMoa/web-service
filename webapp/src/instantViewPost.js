import React from "react";
import Button from "@material-ui/core/Button";
import Dialog from "@material-ui/core/Dialog";
import DialogActions from "@material-ui/core/DialogActions";
import DialogContent from "@material-ui/core/DialogContent";
import DialogContentText from "@material-ui/core/DialogContentText";
import DialogTitle from "@material-ui/core/DialogTitle";
import "./instantViewPost.css";

export default function InstantViewPost(props) {
  const descriptionElementRef = React.useRef(null);
  React.useEffect(() => {
    if (props.openModalView) {
      const { current: descriptionElement } = descriptionElementRef;
      if (descriptionElement !== null) {
        descriptionElement.focus();
      }
    }
  }, [props.openModalView]);

  return (
    <div>
      <Dialog
        open={props.openModalView}
        onClose={props.handleCloseModalView}
        scroll="paper"
        aria-labelledby="scroll-dialog-title"
        aria-describedby="scroll-dialog-description"
      >
        <DialogTitle id="scroll-dialog-title">글 엿보기</DialogTitle>
        <DialogContent dividers={true}>
          <DialogContentText
            id="scroll-dialog-description"
            ref={descriptionElementRef}
            tabIndex={-1}
          >
            <iframe
              className="iframe-view"
              src={props.postUrl}
              title="View Post Frame"
            ></iframe>
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={props.handleCloseModalView} color="primary">
            닫기
          </Button>
          <Button href={props.viewPageUrl} color="primary">
            전체 화면
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
}
