import {useState, useEffect, useRef} from "react";
import axios from 'axios';

import Container from '@mui/material/Container';
import Box from '@mui/material/Box';
import FormLabel from '@mui/material/FormLabel';
import FormControl from '@mui/material/FormControl';
import TextField from '@mui/material/TextField';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import Collapse from '@mui/material/Collapse';
import FormControlLabel from '@mui/material/FormControlLabel';
import Switch from '@mui/material/Switch';
import Grid from '@mui/material/Grid2';
import Paper from '@mui/material/Paper';
import Skeleton from '@mui/material/Skeleton';

import ResponeTimeline from "./components/ResponseTimeline.jsx";
import ResourceCard from "./components/ResourceCard.jsx";
import TemplateFrame from "./TemplateFrame.jsx";
import {last} from "lodash";

const App = () => {
  const [loading, setLoading] = useState(false);
  const [query, setQuery] = useState("");
  const [answers, setAnswers] = useState([]);
  const [finalAnswer, setFinalAnswer] = useState('')
  const [sources, setSources] = useState([]);
  const [toggleDebug, setToggleDebug] = useState(true);
  const debugContainer = useRef(null);

  const scrollToBottom = () => {
    debugContainer.current?.scrollIntoView({behavior: "smooth"})
  }

  useEffect(() => {
    const searchQuery = query.trim();
    if (searchQuery === "") {
      setAnswers([]);
      setSources([]);
      return;
    }
    setLoading(true);

    setAnswers([]);
    axios
      .post(
        "/search",
        {
          query: searchQuery,
        },
        {
          headers: {
            Accept: "text/event-stream",
          },
          responseType: "stream",
          adapter: "fetch",
        },
      )
      .then(async (response) => {
        const stream = response.data;
        const data = [];

        // consume response
        const reader = stream.pipeThrough(new TextDecoderStream()).getReader();
        while (true) {
          const {value, done} = await reader.read();
          if (done) break;

          const messageList = `[${value.replaceAll("}{", "},{")}]`;
          let messages
          try {
            messages = JSON.parse(messageList);
          } catch (e) {
            console.debug(value);
            console.error(e)
          }
          messages.forEach((message) => {
            data.push(message);
          });
          const lastMessage = last(messages);
          if (lastMessage.documents && lastMessage.documents.length > 0) {
            setSources(lastMessage.documents);
          }
          if (lastMessage.error) {
            setSources([]);
          }
          setAnswers(data);
        }
        setAnswers(data);

        if (data.length > 0) {
          const lastMessage = last(data);
          if (lastMessage.documents && lastMessage.documents.length > 0) {
            setSources(lastMessage.documents);
          }
          if (lastMessage.error) {
            setSources([]);
          }
          const result = data.find((message) => {
            if (message.node === 'result') {
              return true;
            }
            return false;
          });
          if (result)
            setFinalAnswer(result.generation);
          else
            setFinalAnswer("This request generated no results");
        }
        setLoading(false);
      })
      .catch((error) => {
        setLoading(false);
        console.error("There was an error retrieving the results: ", error);
        setFinalAnswer("ERROR: There was an error retrieving the results");
      });
  }, [query]);

  useEffect(() => {
    scrollToBottom();
  }, [debugContainer, answers.length]);

  const handleToggleDebug = () => {
    setToggleDebug((prev) => !prev);
  }

  return (
    <TemplateFrame>
      <Box
        id="hero"
        sx={(theme) => ({
          width: "100%",
          height: "100%",
          backgroundRepeat: "no-repeat",
          backgroundImage:
            "radial-gradient(ellipse 80% 50% at 50% -20%, hsl(210, 100%, 90%), transparent)",
          ...theme.applyStyles("dark", {
            backgroundImage:
              "radial-gradient(ellipse 80% 50% at 50% -20%, hsl(210, 100%, 16%), transparent)",
          }),
        })}
      >
        <Container
          sx={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            pt: {xs: 10, sm: 14},
            pb: {xs: 6, sm: 8},
            width: "100%",
            height: "100%",
          }}
        >
          <Stack
            spacing={2}
            useFlexGap
            sx={{alignItems: "center", width: {xs: "100%", sm: "100%", md: "80%"}}}
          >
            <Typography
              variant="h1"
              sx={{
                display: "flex",
                flexDirection: {xs: "column", sm: "row"},
                alignItems: "center",
                fontSize: "clamp(3rem, 10vw, 3.5rem)",
              }}
            >
              RAG&nbsp;
              <Typography
                component="span"
                variant="h1"
                sx={(theme) => ({
                  fontSize: "inherit",
                  color: "primary.main",
                  ...theme.applyStyles("dark", {
                    color: "primary.main",
                  }),
                })}
              >
                Search
              </Typography>
            </Typography>
            <Box
              // noValidate
              sx={{
                display: "flex",
                flexDirection: "column",
                width: "100%",
                gap: 2,
              }}
            >
              <FormControl>
                <FormLabel htmlFor="backgroundURL">Search</FormLabel>
                <TextField
                  id="query"
                  name="query"
                  placeholder="Query"
                  fullWidth
                  variant="outlined"
                  sx={{ariaLabel: "query"}}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      console.log(e);
                      setQuery(e.target.value);
                    }
                  }}
                />
              </FormControl>
            </Box>
            <Stack spacing={2} sx={{mt: 5, width: '100%'}}>
              <FormControlLabel
                control={<Switch checked={toggleDebug} onChange={handleToggleDebug}/>}
                label="See the magic happening"
              />
              <Stack
                direction="row"
                spacing={2}
              >
                <Stack spacing={2} sx={{
                  'maxWidth': toggleDebug ? '70%' : '100%',
                  flexGrow: 1
                }}>
                  {loading ? (
                    <Stack spacing={5}>
                      <Grid container rowSpacing={1} columnSpacing={2}>
                        {Array.from({length: 5}, (_, i) => (
                          <Grid key={i} size={{xs: 6, sm: 4}}>
                              <Skeleton animation="wave" variant="rounded"height={80}/>
                          </Grid>
                        ))}
                      </Grid>
                      <Box>
                        {Array.from({length: 6}, (_, i) => (
                          <Skeleton key={i} animation="wave"/>
                        ))}
                      </Box>
                    </Stack>
                  ) : (
                    <Stack spacing={5}>
                      <Grid container rowSpacing={1} columnSpacing={2}>
                        {sources.map((source, index) => (
                          <Grid key={index} size={{xs: 6, sm: 4}}>
                            <Paper>
                              <ResourceCard source={source}/>
                            </Paper>
                          </Grid>
                        ))}
                      </Grid>
                      <Typography variant="h6">{finalAnswer}</Typography>
                    </Stack>
                  )}
                </Stack>
                <Collapse
                  orientation="horizontal"
                  in={toggleDebug}
                  sx={{
                    'maxWidth': '30%',
                    'height': '50vh',
                    'overflow-y': 'auto',
                    'overflow-x': 'hidden',
                  }}
                >
                  <ResponeTimeline
                    responses={answers}
                  />
                  <Box ref={debugContainer}/>
                </Collapse>
              </Stack>
            </Stack>
          </Stack>
        </Container>
      </Box>
    </TemplateFrame>
  );
};

export default App;
