import PropTypes from 'prop-types';
import Timeline from "@mui/lab/Timeline";
import TimelineItem, { timelineItemClasses } from "@mui/lab/TimelineItem";
import TimelineSeparator from "@mui/lab/TimelineSeparator";
import TimelineConnector from "@mui/lab/TimelineConnector";
import TimelineContent from "@mui/lab/TimelineContent";
import TimelineDot from "@mui/lab/TimelineDot";
import Typography from "@mui/material/Typography";
import {capitalize, replace} from "lodash";

const ResponseTimelineItem = ({message}) => {
  let title
  let content

  const formatNodeName = (node) =>
    capitalize(replace(node, "_", " "));


  switch (message.node) {

    case "init":
      title = formatNodeName(message.node)
      content = "Initializing..."
      break
    case "reset":
      title = formatNodeName(message.node)
      content = "Reverting to the original guestion and search the web"
      break
    case "retrieve":
      title = formatNodeName(message.node)
      content = message.generation
      break
    case "web_search":
      title = formatNodeName(message.node)
      content = message.generation
      break
    case "grade_documents":
      title = formatNodeName(message.node)
      content = message.generation
      break
    case "generate":
      title = formatNodeName(message.node)
      content = message.generation
      break
    case "transform_query":
      title = formatNodeName(message.node)
      content = (
        <>
          {message.generation}
          <br />
          <b>New question:</b> {message.question}
        </>
      )
      break
    case "no_result":
      title = formatNodeName(message.node)
      content = message.generation
      break
    case "result":
      title = formatNodeName(message.node)
      content = message.generation
      break
    default:
      title = formatNodeName(message.node)
      content = message.generation
  }

  return (
    <TimelineItem>
      <TimelineSeparator color="primary">
        <TimelineDot color="primary"/>
        <TimelineConnector color="primary"/>
      </TimelineSeparator>
      <TimelineContent>
        <Typography variant="h6" component="span" color="primary">
          {title}
        </Typography>
        <Typography>{content}</Typography>
      </TimelineContent>
    </TimelineItem>
  );
};

ResponseTimelineItem.propTypes = {
  message: PropTypes.object.isRequired,
}

const ResponeTimeline = ({responses = [],}) => {
  return (
    <Timeline
      sx={{
        [`& .${timelineItemClasses.root}:before`]: {
          flex: 0,
          padding: 0,
        }
      }}
    >
      {responses?.map((message, index) => (
        <ResponseTimelineItem
          key={index}
          message={message}
        />
      ))}
    </Timeline>
  );
};

ResponeTimeline.propTypes = {
  responses: PropTypes.array.isRequired,
}

export default ResponeTimeline;
