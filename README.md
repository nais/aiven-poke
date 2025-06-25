# aiven-poke

Poke teams about Aiven related issues

## Architecture

aiven-poke runs as a Naisjob in gcp clusters, collecting topics and poking team about issues. 

## Development

Build docker image: `mise run docker`
Run prospector and pytest: `mise run check`
