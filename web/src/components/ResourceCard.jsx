import React from "react";
import PropTypes from 'prop-types';
import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import CardActions from "@mui/material/CardActions";
import CardContent from "@mui/material/CardContent";
import Link from "@mui/material/Link";
import Typography from "@mui/material/Typography";

import {truncate} from "lodash";

const card = (source) => (
  <React.Fragment>
    <CardContent>
      <Typography color="primary" variant="h7" gutterBottom>
        {source.metadata.title}
      </Typography>
      <Typography sx={{ color: "text.primary", mb: 1.5 }}>
        {truncate(source.page_content, {'length': 50})}
      </Typography>
    </CardContent>
    <CardActions>
      <Link
        target="_blank"
        component="a"
        variant="primary"
        size="small"
        href={source.metadata.url}
      >
        Learn More
      </Link>
    </CardActions>
  </React.Fragment>
);

const ResourceCard = ({ source }) => {
  return (
    <Box sx={{ minWidth: 150 }}>
      <Card variant="outlined">{card(source)}</Card>
    </Box>
  );
};

ResourceCard.propTypes = {
  source: PropTypes.object.isRequired,
}

export default ResourceCard;
