# aiven-poke

Poke teams about Aiven related issues

## Architecture

aiven-poke runs as a Naisjob in gcp clusters, collecting topics and poking team about issues. 

## Development

We use [`earthly`](https://earthly.dev) for building.
If you don't have earthly installed, you can use the wrapper [`earthlyw`](https://github.com/mortenlj/earthlyw) in the root of the repository.

Build docker image: `./earthlyw +docker`
Run prospector and pytest: `./earthlyw +tests`
